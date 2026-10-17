"""BTOS-CES empirical lag test: separate firm AI use from actual payroll jobs.

Requires only Python standard library, public frozen JSON in research/data/.
No API calls or private information; no modifications to the structural model.
The chronological holdout is NOT a true real-time vintage backtest because
historical CES values are frozen as revised on 2026-10-17.
"""
from __future__ import annotations

from datetime import date
import hashlib
import json
import math
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
BTOS_FILE = ROOT / "research/data/2026-10-17-btos-sector-lag-panel.json"
BLS_FILE = ROOT / "research/data/2026-10-17-bls-ces-sector-employment.json"
PLAN_FILE = ROOT / "research/data/2026-10-17-btos-bls-lag-plan.json"
BOOTSTRAP_SEED = 20261017
BOOTSTRAP_ITERATIONS = 2000


def month_offset(month: str, offset: int) -> str:
    year, month_i = (int(p) for p in month.split("-"))
    number = year * 12 + month_i - 1 + offset
    return f"{number // 12:04d}-{number % 12 + 1:02d}"


def load_study() -> tuple[dict, dict, dict, dict, dict]:
    plan = json.loads(PLAN_FILE.read_text(encoding="utf-8"))
    btos = json.loads(BTOS_FILE.read_text(encoding="utf-8"))
    bls = json.loads(BLS_FILE.read_text(encoding="utf-8"))

    sectors = plan["industries"]
    assert len(sectors) == len(set(sectors)) == 10
    assert plan["exposure_waves"] == [90, 92, 94, 96, 98, 100, 102, 104, 106]
    assert plan["training_exposure_waves"] == [90, 92, 94, 96, 98, 100]
    assert plan["held_out_exposure_waves"] == [102, 104, 106]
    assert len(btos["records"]) == 120
    assert len(bls["series"]) == 10

    btos_idx = {}
    for row in btos["records"]:
        key = row["sector"], row["period"]
        if key in btos_idx:
            raise ValueError(f"Duplicate BTOS observation: {key}")
        btos_idx[key] = row
    bls_idx = {}
    for series in bls["series"]:
        sector = series["sector"]
        if sector not in sectors or sector in bls_idx:
            raise ValueError("Missing or duplicate CES sector")
        records = {}
        for row in series["observations"]:
            key = row["month"]
            if key in records:
                raise ValueError(f"Duplicate CES month: {sector} {key}")
            number = row["persons_thousands"]
            if not isinstance(number, (float, int)) or not math.isfinite(number) or number <= 0:
                raise ValueError("Invalid monthly payroll employee count")
            records[key] = number
        if len(records) != 21 or max(records) != "2026-09":
            raise ValueError(f"Unexpected CES coverage: {sector}")
        bls_idx[sector] = records
    if set(bls_idx) != set(sectors):
        raise ValueError("Industry mapping incomplete")
    return plan, btos, bls, btos_idx, bls_idx


def make_rows(plan: dict, btos_idx: dict, bls_idx: dict) -> list[dict]:
    rows = []
    for sector in plan["industries"]:
        for wave in plan["exposure_waves"]:
            obs = btos_idx[sector, wave]
            earlier = btos_idx[sector, wave - 2]
            end_date = date.fromisoformat(
                # BTOS publishes M/D/YYYY - M/D/YYYY calendar windows
                "{:04d}-{:02d}-{:02d}".format(
                    *reversed(tuple(int(v) for v in obs["range"].split(" - ")[1].split("/")))
                )
            )
            month = f"{end_date.year:04d}-{end_date.month:02d}"
            series = bls_idx[sector]
            last_available = month_offset(month, -1)
            previous = month_offset(month, -2)
            future_month = month_offset(month, +1)
            if future_month > "2026-09":
                raise ValueError("Future/unreleased BLS payroll month requested")
            for m in (previous, last_available, month, future_month):
                if m not in series:
                    raise ValueError(f"No CES data: {sector}/{m}")
            def rate(newer: str, older: str) -> float:
                return 100.0 * (series[newer] / series[older] - 1.0)

            row = {
                "sector": sector,
                "wave": wave,
                "origin_month": month,
                "outcome_month": future_month,
                "ai_level": float(obs["ai_pct"]),
                "ai_change": float(obs["ai_pct"] - earlier["ai_pct"]),
                "revenue_balance": float(obs["rev_up_pct"] - obs["rev_down_pct"]),
                "last_released_payroll_growth": rate(last_available, previous),
                "future_payroll_growth": rate(future_month, month),
            }
            rows.append(row)
    if len(rows) != 90:
        raise ValueError("Incorrect joint panel size")
    return rows


def features(row: dict, name: str, sectors: list[str]) -> list[float]:
    cols = ([1.0] + [float(row["sector"] == s) for s in sectors[1:]]
            + [row["last_released_payroll_growth"], row["revenue_balance"]])
    if name == "M1_AIlevel":
        cols.append(row["ai_level"])
    elif name == "M2_AIchange":
        cols.append(row["ai_change"])
    elif name != "M0":
        raise ValueError(f"Unknown regression: {name}")
    return cols


def pivot_solve(matrix: list[list[float]], vector: list[float]) -> list[float]:
    """Small, strictly fixed OLS normal-equation solver with partial pivoting."""
    n = len(vector)
    array = [matrix[i][:] + [vector[i]] for i in range(n)]
    for k in range(n):
        pivot = max(range(k, n), key=lambda j: abs(array[j][k]))
        array[k], array[pivot] = array[pivot], array[k]
        factor = array[k][k]
        if abs(factor) < 1e-12:
            raise ValueError("Singular regression design")
        for j in range(k, n + 1):
            array[k][j] /= factor
        for i in range(n):
            if i == k:
                continue
            ratio = array[i][k]
            for j in range(k, n + 1):
                array[i][j] -= ratio * array[k][j]
    return [line[-1] for line in array]


def fit(rows: list[dict], name: str, sectors: list[str]) -> list[float]:
    cols = len(features(rows[0], name, sectors))
    xtx = [[0.0] * cols for _ in range(cols)]
    xty = [0.0] * cols
    for row in rows:
        x = features(row, name, sectors)
        for i in range(cols):
            xty[i] += x[i] * row["future_payroll_growth"]
            for j in range(cols):
                xtx[i][j] += x[i] * x[j]
    return pivot_solve(xtx, xty)


def metrics(errors: list[float]) -> dict:
    n = len(errors)
    assert n > 0
    return {
        "n": n,
        "rmse": math.sqrt(sum(e * e for e in errors) / n),
        "mae": sum(abs(e) for e in errors) / n,
        "bias": sum(errors) / n,
    }


def run() -> dict:
    plan, btos, bls, btos_idx, bls_idx = load_study()
    rows = make_rows(plan, btos_idx, bls_idx)
    train = [r for r in rows if r["wave"] in plan["training_exposure_waves"]]
    test = [r for r in rows if r["wave"] in plan["held_out_exposure_waves"]]
    assert len(train) == 60 and len(test) == 30
    sectors = plan["industries"]
    results = {}
    sector_errors = {}
    for name in ("persistence", "M0", "M1_AIlevel", "M2_AIchange"):
        coeffs = None if name == "persistence" else fit(train, name, sectors)
        def predict(row: dict) -> float:
            if coeffs is None:
                return row["last_released_payroll_growth"]
            return sum(c * v for c, v in zip(coeffs, features(row, name, sectors)))
        errors = [predict(r) - r["future_payroll_growth"] for r in test]
        sector_errors[name] = {
            s: [predict(r) - r["future_payroll_growth"]
                for r in test if r["sector"] == s]
            for s in sectors
        }
        results[name] = {
            "training": None if coeffs is None else metrics([
                predict(r) - r["future_payroll_growth"] for r in train
            ]),
            "holdout": metrics(errors),
            "coefficients": coeffs,
            "holdout_predictions": [
                {"sector": r["sector"], "wave": r["wave"], "month": r["outcome_month"],
                 "actual_growth_pct": r["future_payroll_growth"],
                 "predicted_growth_pct": predict(r)}
                for r in test
            ],
        }

    # Resample sectors as blocks; preserve all three held-out periods within a sector.
    # This conditions on the already-fitted predictions; it does NOT represent full
    # model estimation or independent sector/data source uncertainty.
    seed = BOOTSTRAP_SEED
    differences = []
    for _ in range(BOOTSTRAP_ITERATIONS):
        error0, error1 = [], []
        for _ in sectors:
            seed = (1664525 * seed + 1013904223) % (2 ** 32)
            chosen = sectors[int(seed / (2 ** 32) * len(sectors))]
            error0.extend(sector_errors["M0"][chosen])
            error1.extend(sector_errors["M1_AIlevel"][chosen])
        differences.append(metrics(error0)["rmse"] - metrics(error1)["rmse"])
    differences.sort()

    return {
        "research_date": plan["date"],
        "source_urls": [entry["source_api_url"] for entry in bls["series"]],
        "source_file_sha256": {
            "btos": hashlib.sha256(BTOS_FILE.read_bytes()).hexdigest(),
            "bls": hashlib.sha256(BLS_FILE.read_bytes()).hexdigest(),
            "plan": hashlib.sha256(PLAN_FILE.read_bytes()).hexdigest(),
        },
        "units": "percentage points of monthly seasonally adjusted CES payroll job growth",
        "n_btos_source_records": len(btos["records"]),
        "n_bls_source_records": sum(len(s["observations"]) for s in bls["series"]),
        "n_joint_observations": len(rows),
        "n_training": len(train),
        "n_test": len(test),
        "holdout_outcome_months": ["2026-07", "2026-08", "2026-09"],
        "models": results,
        "rmse_improvement_m0_minus_m1_sector_resampling": {
            "lower_approx_2_5pct": differences[49],
            "median": differences[999],
            "upper_approx_97_5pct": differences[1949],
            "warning": "Fixed-fitted model sector resampling, not causal or full statistical CI",
        },
        "interpretation": ("Exploratory model comparison. Payroll headcount growth "
                           "is observed; AI adoption adds only negligible predictive "
                           "improvement on this short, selected-sector sample. "
                           "No causal identification or rho estimate."),
        "realtime_vintage_warning": ("Retrospective chronological split with as-of "
                                     "2026-10-17 revised CES values; not a real-time "
                                     "historical-release-vintage backtest."),
    }


if __name__ == "__main__":
    print(json.dumps(run(), indent=2, sort_keys=True, ensure_ascii=False, allow_nan=False))
