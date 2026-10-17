"""Reproduce 2025-26 Census BTOS industry-level AI/employee *association* audit.

Pure-stdlib, offline, read-only. Models compare an aggregate indicator of
business AI adoption to a next-wave *firm employment-change balance*, not job
counts, causal effects, firm transitions, or Anthropic rho calibration.
"""
from __future__ import annotations

import hashlib
import json
import math
from pathlib import Path
import random
from typing import Callable

DATA = Path(__file__).resolve().parents[1] / "research" / "data" / "2026-10-17-btos-sector-lag-panel.json"
SECTORS = ("23", "31", "42", "44", "48", "51", "52", "54", "62", "72")
PERIODS = tuple(range(88, 111, 2))
TRAIN_T_LAST = 7
BOOT_SEED = 20261017
BOOT_DRAWS = 2000


def load_panel() -> tuple[dict, dict[tuple[str, int], dict]]:
    payload = json.loads(DATA.read_text(encoding="utf-8"))
    assert tuple(payload["universe"]["periods"]) == PERIODS
    assert tuple(payload["universe"]["sectors"]) == SECTORS
    assert len(payload["records"]) == len(SECTORS) * len(PERIODS) == 120
    records = {}
    for row in payload["records"]:
        key = (row["sector"], row["period"])
        assert row["sector"] in SECTORS and row["period"] in PERIODS
        assert key not in records
        for column in ("ai_pct", "emp_up_pct", "emp_down_pct", "rev_up_pct", "rev_down_pct"):
            value = row[column]
            assert isinstance(value, (int, float)) and math.isfinite(value)
            assert 0 <= value <= 100
        records[key] = row
    return payload, records


def observations(records: dict) -> list[dict]:
    result = []
    for sector in SECTORS:
        for t in range(1, len(PERIODS) - 1):
            prev = records[sector, PERIODS[t - 1]]
            curr = records[sector, PERIODS[t]]
            nxt = records[sector, PERIODS[t + 1]]
            result.append({
                "sector": sector, "t": t, "next_period": PERIODS[t + 1],
                "ai": curr["ai_pct"], "dai": curr["ai_pct"] - prev["ai_pct"],
                "y": curr["emp_up_pct"] - curr["emp_down_pct"],
                "rev": curr["rev_up_pct"] - curr["rev_down_pct"],
                "y_next": nxt["emp_up_pct"] - nxt["emp_down_pct"],
            })
    return result


def features(row: dict, model: str) -> list[float]:
    x = ([1.0] + [float(row["sector"] == s) for s in SECTORS[1:]]
         + [float(row["t"]), row["y"], row["rev"]])
    if model == "ai_level":
        x.append(row["ai"])
    elif model == "ai_change":
        x.append(row["dai"])
    elif model != "no_ai":
        raise ValueError("Unknown model")
    return x


def gaussian_solve(a: list[list[float]], b: list[float]) -> list[float]:
    """Ordinary least squares through pivoted normal equations; small fixed design."""
    n = len(b)
    matrix = [list(a[i]) + [b[i]] for i in range(n)]
    for k in range(n):
        pivot = max(range(k, n), key=lambda i: abs(matrix[i][k]))
        matrix[k], matrix[pivot] = matrix[pivot], matrix[k]
        diagonal = matrix[k][k]
        if abs(diagonal) < 1e-10:
            raise ValueError("Singular design matrix")
        for j in range(k, n + 1):
            matrix[k][j] /= diagonal
        for i in range(n):
            if i == k:
                continue
            factor = matrix[i][k]
            for j in range(k, n + 1):
                matrix[i][j] -= factor * matrix[k][j]
    return [row[n] for row in matrix]


def fit(rows: list[dict], model: str) -> list[float]:
    d = len(features(rows[0], model))
    a = [[0.0] * d for _ in range(d)]
    b = [0.0] * d
    for row in rows:
        x = features(row, model)
        for j in range(d):
            b[j] += x[j] * row["y_next"]
            for k in range(d):
                a[j][k] += x[j] * x[k]
    return gaussian_solve(a, b)


def predict(row: dict, model: str, coeff: list[float]) -> float:
    return sum(x * c for x, c in zip(features(row, model), coeff))


def summarize_errors(errors: list[float]) -> dict:
    n = len(errors)
    return {
        "n": n,
        "rmse": math.sqrt(sum(e * e for e in errors) / n),
        "mae": sum(abs(e) for e in errors) / n,
        "bias": sum(errors) / n,
    }


def run() -> dict:
    payload, panel = load_panel()
    sample = observations(panel)
    train = [row for row in sample if row["t"] <= TRAIN_T_LAST]
    holdout = [row for row in sample if row["t"] > TRAIN_T_LAST]
    assert len(sample) == 100 and len(train) == 70 and len(holdout) == 30
    results = {}
    holdout_errors = {}
    for model in ("no_ai", "ai_level", "ai_change"):
        coefficients = fit(train, model)
        errors_train = [predict(r, model, coefficients) - r["y_next"] for r in train]
        errors_test = [predict(r, model, coefficients) - r["y_next"] for r in holdout]
        holdout_errors[model] = {s: [
            predict(r, model, coefficients) - r["y_next"]
            for r in holdout if r["sector"] == s
        ] for s in SECTORS}
        results[model] = {
            "predictors": ("sector fixed effects; linear period trend; current employment "
                           "balance; current revenue balance; " +
                           {"no_ai": "no AI",
                            "ai_level": "current AI-use percentage",
                            "ai_change": "last-four-week change in AI-use percentage"}[model]),
            "train": summarize_errors(errors_train),
            "holdout": summarize_errors(errors_test),
            "ai_coefficient_per_percentage_point": coefficients[-1] if model != "no_ai" else None,
        }

    rng = random.Random(BOOT_SEED)
    delta = []
    for _ in range(BOOT_DRAWS):
        sampled = [rng.choice(SECTORS) for _ in SECTORS]
        def sampled_rmse(name: str) -> float:
            errs = [e for sector in sampled for e in holdout_errors[name][sector]]
            return summarize_errors(errs)["rmse"]
        delta.append(sampled_rmse("no_ai") - sampled_rmse("ai_level"))
    delta.sort()
    return {
        "scope": "Conditional, exploratory sector aggregates; NOT causal AI-job effect",
        "source": payload["source"],
        "data_sha256": hashlib.sha256(DATA.read_bytes()).hexdigest(),
        "sectors": len(SECTORS), "industry_codes": list(SECTORS),
        "period_ids": list(PERIODS), "period_dates": [panel[SECTORS[0], p]["range"] for p in PERIODS],
        "records": len(panel), "paired_observations": len(sample),
        "training_observations": len(train), "holdout_observations": len(holdout),
        "holdout_outcome_periods": [106, 108, 110],
        "equal_weight_sector_ai_pct_start": sum(panel[s, PERIODS[0]]["ai_pct"] for s in SECTORS) / len(SECTORS),
        "equal_weight_sector_ai_pct_end": sum(panel[s, PERIODS[-1]]["ai_pct"] for s in SECTORS) / len(SECTORS),
        "holdout_persistence": summarize_errors([r["y"] - r["y_next"] for r in holdout]),
        "models": results,
        "ai_level_rmse_gain_vs_no_ai_95pct_sector_resampling_range": {
            "method": "fixed predictions, sectors resampled, not a confidence interval for causal effects",
            "lower": delta[50], "median": delta[1000], "upper": delta[1950],
        },
        "limitations": [
            "This is a sector-level firm-incidence percentage balance, not job numbers or hiring rates.",
            "Selected industries are not a representative probability sample and receive equal weight.",
            "The November 2025 AI question change prevents unadjusted use of older waves.",
            "One sampled wave per four weeks, short time horizon, survey error and seasonal effects.",
            "Adding level or change of AI use tests forecast association, not effects of AI adoption.",
            "M0, M1 and M2 miss the later decline in employment balance and lose to persistence.",
            "No independent firm-level data, wages, sector productivity, job postings or task reinstatement rho."
        ],
    }


if __name__ == "__main__":
    print(json.dumps(run(), ensure_ascii=False, indent=2, sort_keys=True, allow_nan=False))
