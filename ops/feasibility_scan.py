"""Reproduce one-model US 2030 growth/workers feasibility exploration offline.

This is a bounded research script, NOT an authenticated API or issue command.
Exploratory post-hoc gain levels are explicitly separate from the locked plan.
"""
from __future__ import annotations

import itertools
import json
from pathlib import Path
import random
import sys

from aiscen import Fixed
from aiscen.report import no_ai_column
from lab.api import compute

PLAN_FILE = (Path(__file__).resolve().parents[1] / "research" / "data"
             / "2026-10-17-ai-worker-frontier-plan.json")
FOLLOWUP_GAINS = (0.55, 0.65, 0.8)  # Selected AFTER seeing first-grid results.


def success(summary: dict, criteria: dict) -> bool:
    return (summary["gdp_gain_pct"] >= criteria["gdp_gain_pct_min"]
            and summary["labor_share_pct"] >= criteria["labor_share_pct_min"]
            and summary["unemployment_total_pct"] <= criteria["unemployment_total_pct_max"])


def evaluate(params: dict, criteria: dict, sensitive_reference: float) -> dict:
    results = compute({"scenario": "substantial", "parameters": params})["summary_2030"]
    matched = success(results, criteria)
    return {"assumptions": params, "summary_2030": results, "meets_three": matched,
            "also_meets_sensitive_unemployment": (matched and
                results["unemployment_sensitive_pct"] <= sensitive_reference)}


def run(*, include_all: bool = False) -> dict:
    import hashlib
    plan_bytes = PLAN_FILE.read_bytes()
    plan = json.loads(plan_bytes)
    axes = plan["scan_axes"]
    criteria = plan["criteria"]
    sensitive_reference = no_ai_column(Fixed())["Unemployment rate, cognitive, pct"]

    combos = [dict(zip(axes, coords)) for coords in itertools.product(*axes.values())]
    if len(combos) != 240:
        raise ValueError("Unexpected scan size; review fixed study protocol")
    grid = [evaluate(p, criteria, sensitive_reference) for p in combos]

    rng = random.Random(plan["validation"]["seed"])
    off_grid = [evaluate({key: round(rng.uniform(*limits), 8)
                for key, limits in plan["validation"]["bounds"].items()},
                criteria, sensitive_reference)
                for _ in range(plan["validation"]["draws"])]
    if len(grid) + len(off_grid) + 1 > plan["budget_max_model_runs"]:
        raise ValueError("Primary model-run budget exceeded")

    followup = [evaluate({**p, "a_2030": a}, criteria, sensitive_reference)
                for a in FOLLOWUP_GAINS for p in combos]
    valid_grid = [v for v in grid if v["meets_three"]]
    valid_off_grid = [v for v in off_grid if v["meets_three"]]
    valid_followup = [v for v in followup if v["meets_three"]]
    valid_sensitive = [v for v in valid_followup if v["also_meets_sensitive_unemployment"]]
    good_labor_grid = [v for v in grid if
         v["summary_2030"]["labor_share_pct"] >= criteria["labor_share_pct_min"]
         and v["summary_2030"]["unemployment_total_pct"] <= criteria["unemployment_total_pct_max"]]

    answer = {
        "study": plan["study"], "scope": "conditional United States model, 2030, not a forecast",
        "source_model_sha": plan["model_source_sha"],
        "lab_source_snapshot_sha": plan["lab_source_sha"],
        "locked_primary_plan_sha256": hashlib.sha256(plan_bytes).hexdigest(),
        "no_ai_sensitive_unemployment_pct": sensitive_reference,
        "default_substantial": compute({"scenario": "substantial"})["summary_2030"],
        "first_scan": {
            "combinations": len(grid), "passed": len(valid_grid),
            "best_gdp_given_both_worker_constraints": max(
                good_labor_grid, key=lambda v: v["summary_2030"]["gdp_gain_pct"])
                if good_labor_grid else None,
            "off_grid_combinations": len(off_grid), "off_grid_passed": len(valid_off_grid),
        },
        "posthoc_followup": {
            "not_preregistered": True, "gain_levels": list(FOLLOWUP_GAINS),
            "combinations": len(followup), "passed": len(valid_followup),
            "also_protect_sensitive_unemployment": len(valid_sensitive),
            "by_gain": {str(a): sum(v["meets_three"] for v in followup
                        if v["assumptions"]["a_2030"] == a) for a in FOLLOWUP_GAINS},
            "highest_gdp_three": max(valid_followup,
                key=lambda v: v["summary_2030"]["gdp_gain_pct"])
                if valid_followup else None,
            "highest_gdp_four": max(valid_sensitive,
                key=lambda v: v["summary_2030"]["gdp_gain_pct"])
                if valid_sensitive else None,
        },
    }
    if include_all:
        answer["all_grid_cells"] = grid
        answer["all_off_grid_cells"] = off_grid
        answer["all_followup_cells"] = followup
    return answer


def main() -> None:
    if sys.argv[1:] not in ([], ["--all"]):
        raise SystemExit("Usage: python ops/feasibility_scan.py [--all]")
    print(json.dumps(run(include_all="--all" in sys.argv[1:]),
                     ensure_ascii=False, sort_keys=True, indent=2, allow_nan=False))


if __name__ == "__main__":
    main()
