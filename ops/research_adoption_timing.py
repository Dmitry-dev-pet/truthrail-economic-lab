"""Self-selected Economic Lab research: US AI adoption-path dependence.

Reproduces one preregistered 3x3 grid and two separately disclosed POST-HOC
mechanism controls. Original model equations, parameters, matching, GDP and
ideas logic remain untouched. This is mathematical scenario research, not a
forecast or causal empirical study. Python standard library + pinned aiscen.
"""
from __future__ import annotations

from dataclasses import replace
from itertools import product
import json
import math
from pathlib import Path
from unittest.mock import patch

from aiscen.params import Fixed, SUBSTANTIAL
from aiscen.paths import Paths
from aiscen import simulate
from aiscen.report import table3_column


ROOT = Path(__file__).resolve().parents[1]
PLAN = ROOT / "research/data/2026-10-18-adoption-timing-plan.json"
CONTROLS = ROOT / "research/data/2026-10-18-adoption-timing-controls.json"
METRICS = (
    "GDP, pct above no-AI", "Labor share, pct of income",
    "Average wage, pct above no-AI", "Unemployment rate, all workers, pct",
    "Unemployment rate, cognitive, pct", "Ideas stock A, pct above no-AI",
)


class WarpedPaths:
    """Only exogenous m,d timing differs; keep base model's other paths."""
    def __init__(self, original: Paths, alpha: float, second: bool):
        self.original = original
        self.alpha = alpha
        self.second = second

    def at(self, t: float) -> dict:
        default = self.original.at(t)
        f = self.original.fixed
        if not (f.t_anchor < t < f.t_target):
            return default
        s = (t - f.t_anchor) / (f.t_target - f.t_anchor)
        if self.second:
            tau = s + self.alpha * s*s*(1-s)*(1-s)
        else:
            tau = s + self.alpha * s*(1-s)
        if not 0.0 <= tau <= 1.0:
            raise ValueError("Invalid exogenous adoption clock")
        observed = self.original.at(f.t_anchor + (f.t_target-f.t_anchor)*tau)
        return {**default, "m": observed["m"], "d": observed["d"],
                "md": observed["m"] * observed["d"]}


def describe(sim: simulate.Result, path: Paths) -> dict:
    table = table3_column(sim)
    snapshots = []
    for t in (2024.0, 2026.5, 2027.5, 2028.0, 2029.0, 2030.0):
        m = sim.at(t)
        ex = path.at(t)
        snapshots.append({
            "t": t, "m": ex["m"], "d": ex["d"], "a": ex["a"],
            "u_c": m.u_rate_C * 100, "u_all": m.u_rate * 100,
            "l_c": m.l_C, "U_c": m.U_C,
            "l_c_frictionless": m.l_C_star,
            "monthly_C_hires": m.H_C,
            "GDP_vs_noAI_pct": math.expm1(m.dlnY) * 100,
        })
    return {"metrics_2030": {key: table[key] for key in METRICS},
            "snapshots": snapshots}


def differences(front: dict, back: dict) -> dict:
    return {k: front["metrics_2030"][k]-back["metrics_2030"][k]
            for k in METRICS}


def validate_identical_endpoints(rows: list[dict], require_stocks: bool) -> None:
    for index in (0, 1, 5):
        snaps = [r["snapshots"][index] for r in rows]
        for field in ("m", "d", "a"):
            if max(s[field] for s in snaps)-min(s[field] for s in snaps)>1e-10:
                raise AssertionError("Technology endpoint mismatch: " + field)
        if require_stocks and index < 5:
            for field in ("l_c", "U_c"):
                if max(s[field] for s in snaps)-min(s[field] for s in snaps)>1e-10:
                    raise AssertionError("Labor-market initial state mismatch")


def run_research() -> dict:
    primary_plan = json.loads(PLAN.read_text())
    controls = json.loads(CONTROLS.read_text())
    f = Fixed()
    original_path = Paths.build(f, SUBSTANTIAL)
    core = []
    for m, d in product(primary_plan["vary_only"]["m_anchor"],
                        primary_plan["vary_only"]["d_anchor"]):
        scenario = replace(SUBSTANTIAL, name=f"path_{m:.2f}_{d:.2f}",
                           m_anchor=m, d_anchor=d)
        sim = simulate.run(f, scenario)
        record = describe(sim, Paths.build(f, scenario))
        record["m_anchor"], record["d_anchor"] = m, d
        core.append(record)
    assert len(core)==9
    for r in core:
        for k, target in (("m", .30), ("d", .40), ("a", .448)):
            if abs(r["snapshots"][-1][k]-target)>1e-10:
                raise AssertionError("2030 technology is not constant")
    pick = lambda m,d: next(r for r in core if r["m_anchor"]==m and r["d_anchor"]==d)
    original = pick(.14,.10)
    if abs(original["metrics_2030"]["GDP, pct above no-AI"]-8.283225887409596)>1e-8:
        raise AssertionError("Original substantially scenario no longer reproducible")
    control_results = {}
    for name, second in (("control_1",False), ("control_2",True)):
        profiles = []
        for alpha in controls[name]["alpha_values"]:
            wrapper = WarpedPaths(original_path, alpha, second)
            with patch.object(simulate.Paths, "build",
                              staticmethod(lambda fixed,scen: wrapper)):
                sim = simulate.run(f, SUBSTANTIAL)
            outcome = describe(sim, wrapper)
            outcome["alpha"] = alpha
            profiles.append(outcome)
        assert len(profiles)==3
        validate_identical_endpoints(profiles, require_stocks=True)
        unwarped = next(x for x in profiles if x["alpha"]==0)
        for field in METRICS:
            if abs(unwarped["metrics_2030"][field]-original["metrics_2030"][field])>1e-8:
                raise AssertionError("Unmodified paths no longer match")
        first, last = min(profiles,key=lambda x:x["alpha"]),max(profiles,key=lambda x:x["alpha"])
        control_results[name] = {
            "posthoc": True, "results": profiles,
            "front_minus_back_2030": differences(last, first),
        }
    for alpha in controls["control_2"]["alpha_values"]:
        for j in range(101):
            s=j/100.0
            if 1+alpha*2*s*(1-s)*(1-2*s)<=0:
                raise AssertionError("Second control is not monotone")
    comparison = differences(pick(.21,.20),pick(.07,.05))
    return {
        "provenance": {
            "pinned_source_sha":primary_plan["source"]["independent_model_sha"],
            "snapshot_lab_sha":primary_plan["source"]["economic_lab_snapshot"],
            "first_plan_before_simulation": True,
            "controls_added_posthoc": True,
            "total_simulations":15,
        },
        "primary": {
            "results":core, "front_minus_back_2030":comparison,
            "H1_direction_supported":comparison["Unemployment rate, cognitive, pct"] < -.05,
            "H2_direction_supported":comparison["GDP, pct above no-AI"] > .05,
        },
        "posthoc_controls":control_results,
        "scientific_limits":controls["disclaimer"],
    }


if __name__ == "__main__":
    print(json.dumps(run_research(), ensure_ascii=False, indent=2,
                     sort_keys=True, allow_nan=False))
