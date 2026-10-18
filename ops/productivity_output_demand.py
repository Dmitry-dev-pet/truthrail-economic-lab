"""Year-ahead phenomenological output / labor-hours research (BLS services).

All code uses standard Python; reads archived official publication table-1 extracts.
Study goal: Does *lagged* annual output/hour growth predict next-year real
output, beyond lagged output alone? 2025 is a strict temporal holdout.
This deliberately does not identify causal productivity shocks or AI effects.
"""
from __future__ import annotations

import hashlib
import json
import math
from pathlib import Path
import random

BASE = Path(__file__).resolve().parents[1] / "research" / "data"
DATA = BASE / "2026-10-18-bls-service-output-hours-2022-25.json"
PLAN = BASE / "2026-10-18-lagged-productivity-research-plan.json"
YEARS = (2022, 2023, 2024, 2025)
TRAIN_YEARS = (2023, 2024)
HOLDOUT_YEAR = 2025
DRAW_COUNT = 2000
BOOTSTRAP_SEED = 20261018


def load() -> tuple[dict, dict, dict]:
    data = json.loads(DATA.read_text(encoding="utf-8"))
    plan = json.loads(PLAN.read_text(encoding="utf-8"))
    assert tuple(plan["training_years"]) == TRAIN_YEARS
    assert plan["heldout_year"] == HOLDOUT_YEAR
    codes = tuple(data["selected_naics"])
    assert len(codes) == len(set(codes)) == 28
    assert not any(b.startswith(a) for a in codes for b in codes if a != b)
    assert len(data["rows"]) == 28 * len(YEARS)
    lookup = {}
    for row in data["rows"]:
        code, year = row["naics"], row["year"]
        key = code, year
        if code not in codes or year not in YEARS or key in lookup:
            raise ValueError("Unknown, duplicate or out-of-scope industry/year")
        for column in ("real_output_pct", "total_hours_pct",
                       "labor_productivity_pct", "employment_thousands"):
            v = row[column]
            if not isinstance(v, (int, float)) or not math.isfinite(v):
                raise ValueError(f"Invalid observation {key}: {column}")
        if min(100 + row["real_output_pct"], 100 + row["total_hours_pct"]) <= 0:
            raise ValueError("Invalid growth rate")
        lookup[key] = row
    for code in codes:
        for year in YEARS:
            if (code, year) not in lookup:
                raise ValueError(f"Missing {code} {year}")
    return data, plan, lookup


def observations(data: dict, lookup: dict) -> list[dict]:
    rows = []
    for code in data["selected_naics"]:
        for year in YEARS[1:]:
            current = lookup[code, year]
            lag = lookup[code, year - 1]
            rows.append({
                "naics": code,
                "name": current["industry"],
                "year": year,
                "q": current["real_output_pct"],
                "h": current["total_hours_pct"],
                "a": current["labor_productivity_pct"],
                "q_lag": lag["real_output_pct"],
                "h_lag": lag["total_hours_pct"],
                "a_lag": lag["labor_productivity_pct"],
            })
    return rows


def least_squares(rows: list[dict], features: list[str], target: str) -> list[float]:
    """Small fixed OLS design with pivoted Gaussian elimination."""
    dim = len(features) + 1
    gram = [[0.0] * (dim + 1) for _ in range(dim)]
    for row in rows:
        x = [1.0] + [float(row[key]) for key in features]
        for i in range(dim):
            gram[i][dim] += x[i] * row[target]
            for j in range(dim):
                gram[i][j] += x[i] * x[j]
    for k in range(dim):
        pivot = max(range(k, dim), key=lambda i: abs(gram[i][k]))
        gram[k], gram[pivot] = gram[pivot], gram[k]
        if abs(gram[k][k]) < 1e-10:
            raise ValueError("Singular regression: verify source and predictors")
        scale = gram[k][k]
        for j in range(k, dim + 1):
            gram[k][j] /= scale
        for i in range(dim):
            if i == k:
                continue
            scale = gram[i][k]
            for j in range(k, dim + 1):
                gram[i][j] -= scale * gram[k][j]
    return [line[-1] for line in gram]


def prediction(row: dict, features: list[str], coeffs: list[float]) -> float:
    return coeffs[0] + sum(
        coeff * row[key] for key, coeff in zip(features, coeffs[1:])
    )


def metrics(errors: list[float]) -> dict:
    n = len(errors)
    assert n
    return {
        "n": n,
        "rmse_pp": math.sqrt(sum(e * e for e in errors) / n),
        "mae_pp": sum(abs(e) for e in errors) / n,
        "bias_pp": sum(errors) / n,
    }


def classify_2025(rows: list[dict]) -> dict:
    out = {
        "output_up_hours_up": 0,
        "output_up_hours_down": 0,
        "output_down_hours_up": 0,
        "output_down_hours_down": 0,
        "boundary_zero": 0,
    }
    for row in rows:
        q, h = row["q"], row["h"]
        if q == 0 or h == 0:
            out["boundary_zero"] += 1
        elif q > 0 and h > 0:
            out["output_up_hours_up"] += 1
        elif q > 0 and h < 0:
            out["output_up_hours_down"] += 1
        elif q < 0 and h > 0:
            out["output_down_hours_up"] += 1
        elif q < 0 and h < 0:
            out["output_down_hours_down"] += 1
    assert sum(out.values()) == len(rows)
    return out


def run() -> dict:
    data, plan, lookup = load()
    rows = observations(data, lookup)
    train = [r for r in rows if r["year"] in TRAIN_YEARS]
    holdout = [r for r in rows if r["year"] == HOLDOUT_YEAR]
    assert len(train) == 56 and len(holdout) == 28

    coefficients = {
        "M0": least_squares(train, ["q_lag"], "q"),
        "M1": least_squares(train, ["q_lag", "a_lag"], "q"),
        "A_ar1": least_squares(train, ["a_lag"], "a"),
    }

    def forecast_output(row: dict, model: str) -> float:
        if model == "persistence":
            return row["q_lag"]
        if model == "M0":
            return prediction(row, ["q_lag"], coefficients[model])
        if model == "M1":
            return prediction(row, ["q_lag", "a_lag"], coefficients[model])
        raise ValueError(model)

    def forecast_hours(row: dict, model: str) -> float:
        if model == "hours_persistence":
            return row["h_lag"]
        if model in ("hours_M0", "hours_M1"):
            q_hat = forecast_output(row, model[-2:])
            a_hat = prediction(row, ["a_lag"], coefficients["A_ar1"])
            if 1 + a_hat / 100 <= 0:
                raise ValueError("Invalid productivity growth forecast")
            # Identity applied ONLY to two out-of-period forecasts (no observed
            # 2025 output or productivity used as predictors).
            return 100 * ((1 + q_hat / 100) / (1 + a_hat / 100) - 1)
        raise ValueError(model)

    output_scores = {}
    for name in ("persistence", "M0", "M1"):
        output_scores[name] = {
            "train": None if name == "persistence" else metrics(
                [forecast_output(r, name) - r["q"] for r in train]
            ),
            "holdout": metrics([forecast_output(r, name) - r["q"] for r in holdout]),
        }
    hours_scores = {}
    for name in ("hours_persistence", "hours_M0", "hours_M1"):
        hours_scores[name] = {
            "train": None if name == "hours_persistence" else metrics(
                [forecast_hours(r, name) - r["h"] for r in train]
            ),
            "holdout": metrics([forecast_hours(r, name) - r["h"] for r in holdout]),
        }

    rng = random.Random(BOOTSTRAP_SEED)
    differences = []
    for _ in range(DRAW_COUNT):
        chosen = [rng.choice(holdout) for _ in holdout]
        s0 = metrics([forecast_output(r, "M0") - r["q"] for r in chosen])["rmse_pp"]
        s1 = metrics([forecast_output(r, "M1") - r["q"] for r in chosen])["rmse_pp"]
        differences.append(s0 - s1)
    differences.sort()

    return {
        "sources": data["source_urls"],
        "sha256": {
            "data": hashlib.sha256(DATA.read_bytes()).hexdigest(),
            "plan": hashlib.sha256(PLAN.read_bytes()).hexdigest(),
        },
        "n_industries": len(data["selected_naics"]),
        "n_annual_source_rows": len(data["rows"]),
        "n_train": len(train),
        "n_holdout": len(holdout),
        "training_years": list(TRAIN_YEARS),
        "holdout_year": HOLDOUT_YEAR,
        "model_coefficients": coefficients,
        "next_year_real_output_forecast": output_scores,
        "next_year_hours_forecast": hours_scores,
        "holdout_quadrants": classify_2025(holdout),
        "holdout_observations": [
            {
                "naics": r["naics"], "name": r["name"], "real_output_pct": r["q"],
                "hours_pct": r["h"], "labor_productivity_pct": r["a"],
                "output_pred_persistence_pct": forecast_output(r, "persistence"),
                "output_pred_M0_pct": forecast_output(r, "M0"),
                "output_pred_M1_pct": forecast_output(r, "M1"),
                "hours_pred_persistence_pct": forecast_hours(r, "hours_persistence"),
                "hours_pred_M0_pct": forecast_hours(r, "hours_M0"),
                "hours_pred_M1_pct": forecast_hours(r, "hours_M1"),
            }
            for r in holdout
        ],
        "fixed_fit_sector_resampling_gain_M1_over_M0_pp": {
            "low_2_5pct": differences[50],
            "median": differences[1000],
            "high_97_5pct": differences[1950],
            "meaning": (
                "Descriptive resampling of fixed forecasts across 28 intentionally "
                "selected, potentially correlated industries. NOT a causal confidence "
                "interval or independent statistical inference."
            ),
        },
        "scientific_verdict": (
            "A slight regression-to-regression RMSE improvement from lagged "
            "productivity does NOT beat direct output persistence on the 2025 "
            "holdout. Combining fitted forecasts through the labor identity "
            "also does NOT beat lagged-hours persistence. No robust predictive "
            "law of demand expansion or AI-induced hiring identified."
        ),
        "research_limits": plan["limitations"],
    }


if __name__ == "__main__":
    print(json.dumps(run(), ensure_ascii=False, sort_keys=True, indent=2, allow_nan=False))
