"""Small, bounded two-axis economic experiments over the existing local model.

The scenario assumptions are not forecasts and Anthropic Economic Index observations
are not used to calibrate them. No network activity or Mac authority is provided.
"""
from __future__ import annotations

from itertools import product
import json

from .api import BOUNDS, PRESETS, compute, validate_payload


# A demonstration of automation intensity versus labor reallocation, not new-task
# creation. Fixed arguments make the default CLI repeatable and reviewable.
DEMO = {
    "scenario": "substantial",
    "axes": {
        "psi": [0.25, 0.50, 0.75],
        "mu": [0.03, 0.06, 0.12],
    },
}
MAX_CELLS = 25


def validate_experiment_payload(payload):
    """Return normalized, bounded assumptions; never accept executable inputs."""
    if not isinstance(payload, dict):
        raise ValueError("Experiment must be a JSON object")
    if set(payload) - {"scenario", "axes", "baseline_overrides", "fixed"}:
        raise ValueError("Unknown experiment fields")

    scenario = payload.get("scenario", "substantial")
    if not isinstance(scenario, str) or scenario not in PRESETS:
        raise ValueError("Unknown scenario")
    axes = payload.get("axes")
    if not isinstance(axes, dict) or len(axes) != 2:
        raise ValueError("Exactly two parameter axes are required")
    if any(key not in BOUNDS for key in axes):
        raise ValueError("Unsupported experiment parameter")

    fixed = payload.get("fixed", {})
    baseline = payload.get("baseline_overrides", {})
    if not isinstance(fixed, dict) or not isinstance(baseline, dict):
        raise ValueError("Overrides must be objects")
    if set(axes) & set(baseline):
        raise ValueError("Axis parameters cannot also be baseline overrides")
    _, baseline, fixed = validate_payload({
        "scenario": scenario, "parameters": baseline, "fixed": fixed,
    })

    normalized_axes = {}
    for key, values in axes.items():
        if not isinstance(values, list) or not 2 <= len(values) <= 5:
            raise ValueError("Each axis needs between two and five values")
        checked = []
        for value in values:
            _, p, _ = validate_payload({"scenario": scenario, "parameters": {key: value}})
            checked.append(p[key])
        if len(set(checked)) != len(checked):
            raise ValueError("Axis values must be distinct")
        normalized_axes[key] = checked

    sizes = [len(values) for values in normalized_axes.values()]
    if sizes[0] * sizes[1] > MAX_CELLS:
        raise ValueError("Experiment exceeds the cell limit")
    return scenario, normalized_axes, baseline, fixed


def run_experiment(payload):
    """Compare grid cells to a single unmodified, same-preset reference."""
    scenario, axes, baseline_params, fixed = validate_experiment_payload(payload)
    base = compute({
        "scenario": scenario, "parameters": baseline_params, "fixed": fixed,
    })
    reference = base["summary_2030"]
    axis_names = list(axes)
    cells = []
    for values in product(*(axes[name] for name in axis_names)):
        coordinates = dict(zip(axis_names, values))
        result = compute({
            "scenario": scenario,
            "parameters": {**baseline_params, **coordinates},
            "fixed": fixed,
        })
        summary = result["summary_2030"]
        cells.append({
            "coordinates": coordinates,
            "summary_2030": summary,
            "delta_vs_baseline_pp": {
                key: round(summary[key] - reference[key], 6) for key in reference
            },
        })
    metadata = dict(base["metadata"])
    metadata["experiment"] = "two_axis_parameter_grid"
    metadata["model_runs"] = len(cells) + 1
    metadata["interpretation"] = "Conditional US scenarios, not forecasts or calibrated country estimates"
    return {
        "metadata": metadata,
        "assumptions": {
            "scenario": scenario,
            "axes": axes,
            "baseline_overrides": baseline_params,
            "fixed_overrides": fixed,
        },
        "baseline": {
            "summary_2030": reference,
            "resolved_scenario": base["inputs"]["parameters"],
            "resolved_fixed": base["inputs"]["fixed"],
        },
        "cells": cells,
    }


def main():
    # CLI deliberately has no user-selectable flags. It is an example and not
    # an approved Mac control-plane command.
    import sys
    if len(sys.argv) != 1:
        raise SystemExit("This demo takes no command-line arguments")
    print(json.dumps(run_experiment(DEMO), ensure_ascii=False, separators=(",", ":"), allow_nan=False))


if __name__ == "__main__":
    main()
