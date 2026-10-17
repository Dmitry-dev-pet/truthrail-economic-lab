"""Small transparent market-demand/labor-hours mechanism, with no AI attribution.

This is a deliberately *hypothetical* partial-equilibrium phenomenological model.
It does not estimate any parameters from the BLS data; BLS output/productivity/
hours form an accounting identity, not an independent predictive validation.
No network, model changes, or runner permissions.
"""
from __future__ import annotations

import json
import math
from pathlib import Path
from typing import Any

DATA = (Path(__file__).resolve().parents[1] / "research" / "data"
        / "2026-10-18-bls-output-productivity-hours-2025.json")


def implied_hours_growth(output_growth_pct: float,
                         productivity_growth_pct: float) -> float:
    """Identity H=Q/A, for matching output-per-hour productivity and hours."""
    if output_growth_pct <= -100 or productivity_growth_pct <= -100:
        raise ValueError("Real output and productivity must remain positive")
    return 100 * ((1 + output_growth_pct / 100)
                  / (1 + productivity_growth_pct / 100) - 1)


def market_response(*, productivity_gain_pct: float,
                    price_pass_through: float,
                    demand_price_elasticity: float,
                    autonomous_real_demand_growth_pct: float = 0.0,
                    hours_per_worker_growth_pct: float = 0.0) -> dict[str, float]:
    """Conditional scenario, NOT estimated elasticities.

    A1/A0 = 1+g_A, P1/P0 = (A1/A0)**(-tau),
    Q1/Q0 = (1+g_D)*(P1/P0)**(-epsilon),
    H1/H0=(Q1/Q0)/(A1/A0), N1/N0=(H1/H0)/(h1/h0).

    tau is output-price response to productivity, not a direct observed price
    pass-through of costs; epsilon is a price-demand elasticity, g_D is a
    shift in willingness to purchase quantities at a given price. The latter
    cannot automatically be called new human tasks or rho.
    """
    vals = [productivity_gain_pct, price_pass_through,
            demand_price_elasticity, autonomous_real_demand_growth_pct,
            hours_per_worker_growth_pct]
    if any(not math.isfinite(v) for v in vals):
        raise ValueError("Non-finite model input")
    if (productivity_gain_pct < 0 or productivity_gain_pct > 300
            or not (0 <= price_pass_through <= 1)
            or not (0 <= demand_price_elasticity <= 10)
            or not (-99 < autonomous_real_demand_growth_pct <= 300)
            or not (-99 < hours_per_worker_growth_pct <= 300)):
        raise ValueError("Inputs outside documented exploratory bounds")
    a = 1 + productivity_gain_pct / 100
    p = a ** (-price_pass_through)
    q = (1 + autonomous_real_demand_growth_pct / 100) * p ** (-demand_price_elasticity)
    hours = q / a
    per_worker = 1 + hours_per_worker_growth_pct / 100
    jobs = hours / per_worker
    return {"price_change_pct": 100 * (p - 1),
            "real_output_growth_pct": 100 * (q - 1),
            "labor_hours_growth_pct": 100 * (hours - 1),
            "worker_count_growth_pct": 100 * (jobs - 1),
            "effective_demand_compensation": price_pass_through * demand_price_elasticity}


def equilibrium_elasticity_threshold(*, productivity_gain_pct: float,
                                     price_pass_through: float,
                                     autonomous_real_demand_growth_pct: float = 0,
                                     hours_per_worker_growth_pct: float = 0) -> float | None:
    """Price elasticity at which employment change is exactly zero.

    Returns None when productivity gain and pass-through do not identify an
    elasticity threshold; in that case solve using other assumptions.
    Can be negative when exogenous demand growth alone already suffices.
    """
    # Validation shares mechanism's numerical assumptions and bounds.
    market_response(productivity_gain_pct=productivity_gain_pct,
                    price_pass_through=price_pass_through,
                    demand_price_elasticity=0,
                    autonomous_real_demand_growth_pct=autonomous_real_demand_growth_pct,
                    hours_per_worker_growth_pct=hours_per_worker_growth_pct)
    if not productivity_gain_pct or not price_pass_through:
        return None
    ln_a = math.log1p(productivity_gain_pct / 100)
    ln_d = math.log1p(autonomous_real_demand_growth_pct / 100)
    ln_h = math.log1p(hours_per_worker_growth_pct / 100)
    return (1 + (ln_h - ln_d) / ln_a) / price_pass_through


def check_bls_rows() -> dict[str, Any]:
    payload = json.loads(DATA.read_text(encoding="utf-8"))
    rows = payload["rows"]
    if len(rows) != 10 or len({r["naics"] for r in rows}) != 10:
        raise ValueError("Source snapshot must contain 10 distinct NAICS rows")
    comparisons = []
    for row in rows:
        predicted = implied_hours_growth(row["output_growth_pct"],
                                         row["labor_productivity_growth_pct"])
        residual = predicted - row["hours_growth_pct"]
        if abs(residual) > 0.11:
            raise ValueError("Reported BLS identity mismatch > rounding: " + row["naics"])
        comparisons.append({"naics": row["naics"], "industry": row["industry"],
                            "reported_output_growth_pct": row["output_growth_pct"],
                            "reported_productivity_growth_pct": row["labor_productivity_growth_pct"],
                            "reported_hours_growth_pct": row["hours_growth_pct"],
                            "implied_hours_growth_pct": predicted,
                            "rounding_residual_pp": residual})
    return {"source_release_year": 2025, "rows": comparisons,
            "max_abs_rounding_residual_pp": max(abs(r["rounding_residual_pp"])
                                                 for r in comparisons),
            "note": "Identity check only: cannot independently validate labor-demand theory"}


def report() -> dict[str, Any]:
    scenarios = [
        ("weak demand response", 0.5, 0.8),
        ("neutral hours boundary", 1.25, 0.8),
        ("strong demand response", 2.0, 0.8),
    ]
    return {"question": "When can productivity growth preserve or expand labor hours?",
            "method": "conditional partial equilibrium with constant price elasticity, not an AI effect estimate",
            "bls_2025_identity_audit": check_bls_rows(),
            "illustrative_productivity_shock_pct": 10.0,
            "price_elasticity_threshold_no_external_demand_or_hours_change": 1.25,
            "scenarios": [{"label": name, "epsilon": e, "tau": t,
                           **market_response(productivity_gain_pct=10,
                                             demand_price_elasticity=e,
                                             price_pass_through=t)}
                          for name, e, t in scenarios],
            "inference_boundary": ("No elasticity, price pass-through or autonomous demand shift "
                                   "is estimated. Output and hours are jointly measured; "
                                   "BLS labor productivity is defined as their ratio. "
                                   "Employment persons need separately harmonized hours per worker. "
                                   "Cannot calibrate Anthropic rho from this data.")}


if __name__ == "__main__":
    print(json.dumps(report(), sort_keys=True, indent=2, ensure_ascii=False,
                     allow_nan=False))
