"""Bounded one-factor-at-a-time scenario sensitivity audit.

These are numerical comparisons across equal *fractions of parameter bounds*,
not probabilities, empirical estimates, standardized elasticities, or a causal
factor decomposition. Every parameter and contrast is planned BEFORE simulation.
No arbitrary issue inputs are forwarded as executable code.
"""
from __future__ import annotations

from hashlib import sha256
import json
import math

from .api import BOUNDS, FIXED_BOUNDS, PRESETS, COMMIT, compute, presets

# Exactly nine approved model inputs: seven scenario dials and two structural
# assumptions. Each gets a 10%-of-allowed-range interval containing the preset.
PARAMETER_BOUNDS = {**BOUNDS, **FIXED_BOUNDS}
PARAMETERS = tuple(PARAMETER_BOUNDS)
STRUCTURAL = frozenset(FIXED_BOUNDS)
METRICS = (
    "gdp_gain_pct",
    "labor_share_pct",
    "unemployment_total_pct",
    "unemployment_sensitive_pct",
    "wage_gain_pct",
)
RANGE_FRACTION = 0.10
MAX_EVALUATIONS = 19


def validate_request(payload):
    if not isinstance(payload, dict):
        raise ValueError("Sensitivity request must be a JSON object")
    if set(payload) != {"analysis", "scenario"}:
        raise ValueError("Only analysis and scenario keys are accepted")
    if payload["analysis"] != "sensitivity" or not isinstance(payload["analysis"], str):
        raise ValueError("Unsupported analysis")
    if not isinstance(payload["scenario"], str) or payload["scenario"] not in PRESETS:
        raise ValueError("Unknown scenario")
    return payload["scenario"]


def bounded_window(baseline, allowed):
    """Equal-length interval containing baseline, shifted at hard boundaries."""
    lo, hi = allowed
    baseline = float(baseline)
    if not math.isfinite(baseline) or baseline < lo - 1e-10 or baseline > hi + 1e-10:
        raise ValueError("Preset is outside declared parameter bounds")
    baseline = min(hi, max(lo, baseline))
    width = (hi - lo) * RANGE_FRACTION
    if not 0 < width < hi - lo:
        raise ValueError("Invalid sensitivity interval")
    lower = max(lo, min(baseline - width / 2, hi - width))
    upper = min(hi, lower + width)
    if not lower <= baseline <= upper or not upper > lower:
        raise ValueError("Invalid planned parameter contrast")
    return lower, upper


def prepare_sensitivity(payload):
    """Freeze the 19-model-call plan without running the simulator."""
    selected = validate_request(payload)
    catalog = presets()
    if catalog["model_commit"] != COMMIT:
        raise ValueError("Unexpected model provenance")
    current = catalog["presets"][selected]
    fixed = catalog["fixed_defaults"]
    plan = []
    for name in PARAMETERS:
        structural = name in STRUCTURAL
        center = float(fixed[name] if structural else current[name])
        low, high = bounded_window(center, PARAMETER_BOUNDS[name])
        plan.append({
            "parameter": name,
            "group": "structural" if structural else "scenario",
            "baseline_value": center,
            "low": low,
            "high": high,
            "allowed_min": PARAMETER_BOUNDS[name][0],
            "allowed_max": PARAMETER_BOUNDS[name][1],
        })
    if len(plan) * 2 + 1 != MAX_EVALUATIONS:
        raise ValueError("Sensitivity plan exceeds the hard calculation budget")
    frozen = {
        "analysis": "sensitivity",
        "scenario": selected,
        "model_commit": COMMIT,
        "range_fraction": RANGE_FRACTION,
        "method": "one_factor_at_a_time_equal_allowed_range_window",
        "sampling": plan,
        "interpretation": "U.S. model response to numerical assumptions, not estimated real-world importance",
    }
    packed = json.dumps(frozen, sort_keys=True, separators=(",", ":"), allow_nan=False)
    return {
        "plan": frozen,
        "plan_sha256": sha256(packed.encode("utf-8")).hexdigest(),
        "planned_model_evaluations": MAX_EVALUATIONS,
    }


def _validated_metrics(output):
    summary = output["summary_2030"]
    if not all(key in summary and
               isinstance(summary[key], (float, int)) and
               not isinstance(summary[key], bool) and
               math.isfinite(summary[key]) for key in METRICS):
        raise ValueError("Nonfinite or missing model outputs")
    return {key: float(summary[key]) for key in METRICS}


def run_sensitivity(payload):
    prepared = prepare_sensitivity(payload)
    frozen = prepared["plan"]
    scenario = frozen["scenario"]
    baseline_model = compute({"scenario": scenario})
    if baseline_model["metadata"]["source_commit"] != COMMIT:
        raise ValueError("Unexpected model source in baseline")
    baseline = _validated_metrics(baseline_model)
    measurements = []
    for setting in frozen["sampling"]:
        name = setting["parameter"]
        samples = []
        for value in (setting["low"], setting["high"]):
            override = {"fixed": {name: value}} if setting["group"] == "structural" else {"parameters": {name: value}}
            answer = compute({"scenario": scenario, **override})
            if answer["metadata"]["source_commit"] != COMMIT:
                raise ValueError("Unexpected model source in sensitivity sample")
            samples.append(_validated_metrics(answer))
        low_metrics, high_metrics = samples
        delta = {k: round(high_metrics[k] - low_metrics[k], 6) for k in METRICS}
        measurements.append({
            **setting,
            "low_2030": low_metrics,
            "high_2030": high_metrics,
            "high_minus_low_pp": delta,
            "absolute_change_pp": {k: round(abs(delta[k]), 6) for k in METRICS},
        })
    rankings = {
        metric: [
            {"parameter": x["parameter"],
             "absolute_change_pp": x["absolute_change_pp"][metric],
             "signed_change_pp": x["high_minus_low_pp"][metric]}
            for x in sorted(measurements,
                            key=lambda x: (-x["absolute_change_pp"][metric], x["parameter"]))
        ]
        for metric in METRICS
    }
    return {
        "research": prepared,
        "metadata": {
            **baseline_model["metadata"],
            "experiment": "bounded_one_factor_at_a_time_sensitivity",
            "model_evaluations": MAX_EVALUATIONS,
        },
        "baseline_2030": baseline,
        "measurements": measurements,
        "rankings": rankings,
        "limitations": [
            "Rankings compare 10% windows of allowed parameter bounds; the bounds are modeling choices, not uncertainty distributions.",
            "A window may be shifted near a preset boundary; it still contains the preset at the same numerical width.",
            "One-at-a-time contrasts do not reveal parameter interactions or identify causation.",
            "This is a U.S. conditional macroeconomic model, not a labor-market forecast, significance test, or Portugal estimate.",
            "Anthropic Economic Index observations are not used to calibrate any model input.",
        ],
    }


def main():
    import sys
    if len(sys.argv) != 1:
        raise SystemExit("Fixed sensitivity demonstration accepts no arguments")
    print(json.dumps(run_sensitivity({"analysis": "sensitivity", "scenario": "substantial"}),
                     separators=(",", ":"), ensure_ascii=False, allow_nan=False))


if __name__ == "__main__":
    main()
