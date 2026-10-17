"""Predeclared, bounded hypotheses over the independently reproduced US model.

This is transparent *model exploration*, not forecasting or free-form agent
execution. Hypothesis selection and directional tests are fixed BEFORE any
model computation. Alfred may propose a different reviewed catalogue later.
"""
from __future__ import annotations

from copy import deepcopy
from hashlib import sha256
import json

from .api import COMMIT, PRESETS
from .experiment import run_experiment, validate_experiment_payload


# The rubric is deliberately explicit and does not depend on model outcomes.
# The preceding project experiment tested psi x mu, not rho x psi.
# Each proposal has one no-AI baseline + nine controlled scenario cells.
CANDIDATES = (
    {
        "id": "new_tasks_vs_automation",
        "question": "Can new human tasks offset the distributional effects of automation?",
        "hypothesis": "At the same automation intensity, greater reinstatement of human tasks improves labor outcomes in the US model.",
        "alternative": "No consistent directional improvement across the chosen automation levels.",
        "scientific_note": "rho counts new AI-sensitive labor tasks per automated task; psi is the fraction of AI usage that replaces rather than augments labor.",
        "axes": {"psi": [0.50, 0.75, 0.90], "rho": [0.00, 0.25, 0.50]},
        "predictions": [
            {"axis": "rho", "metric": "labor_share_pct", "direction": "increase"},
            {"axis": "rho", "metric": "unemployment_sensitive_pct", "direction": "decrease"},
            {"axis": "psi", "metric": "labor_share_pct", "direction": "decrease"},
        ],
        "rubric": {"previously_untested_mechanism": 3, "worker_relevance": 3, "controlled_contrast": 3},
    },
    {
        "id": "new_tasks_vs_mobility",
        "question": "Are new tasks and worker mobility different buffers against displacement?",
        "hypothesis": "New tasks increase the labor share, while easier occupational transitions reduce AI-sensitive unemployment.",
        "alternative": "Either assumed relationship does not hold consistently across the explored levels.",
        "scientific_note": "rho creates labor tasks inside AI-sensitive occupations; mu controls ease of finding work in a different occupation group.",
        "axes": {"rho": [0.00, 0.25, 0.50], "mu": [0.04, 0.08, 0.17]},
        "predictions": [
            {"axis": "rho", "metric": "labor_share_pct", "direction": "increase"},
            {"axis": "mu", "metric": "unemployment_sensitive_pct", "direction": "decrease"},
        ],
        "rubric": {"previously_untested_mechanism": 3, "worker_relevance": 3, "controlled_contrast": 2},
    },
    {
        "id": "automation_vs_mobility",
        "question": "Does occupational mobility buffer unemployment when automation expands?",
        "hypothesis": "Easier transitions reduce joblessness among workers in AI-sensitive occupations.",
        "alternative": "No consistent unemployment reduction across the selected automation levels.",
        "scientific_note": "This question partially replicates the previous psi x mu experiment and thus gets a lower novelty score.",
        "axes": {"psi": [0.50, 0.75, 0.90], "mu": [0.04, 0.08, 0.17]},
        "predictions": [
            {"axis": "mu", "metric": "unemployment_sensitive_pct", "direction": "decrease"},
            {"axis": "psi", "metric": "labor_share_pct", "direction": "decrease"},
        ],
        "rubric": {"previously_untested_mechanism": 1, "worker_relevance": 3, "controlled_contrast": 3},
    },
)
MIN_EFFECT_PP = 0.02
MAX_MODEL_EVALUATIONS = 10


def proposals():
    """Return predeclared hypotheses in transparent, outcome-blind order."""
    out = []
    for candidate in CANDIDATES:
        record = deepcopy(candidate)
        record["priority_score"] = sum(record["rubric"].values())
        out.append(record)
    return sorted(out, key=lambda h: (-h["priority_score"], h["id"]))


def prepare(request):
    """Freeze the exact plan before calling the mathematical simulator."""
    if not isinstance(request, dict) or set(request) - {"research", "scenario"}:
        raise ValueError("Research request allows only research and scenario")
    chosen_id = request.get("research", "auto")
    scenario = request.get("scenario", "substantial")
    if not isinstance(scenario, str) or scenario not in PRESETS:
        raise ValueError("Unknown preset")
    ranked = proposals()
    if not isinstance(chosen_id, str):
        raise ValueError("Research id must be a string")
    if chosen_id == "auto":
        selected = ranked[0]
        selection = "Highest predeclared priority score, before examining any outputs"
    else:
        matched = [c for c in ranked if c["id"] == chosen_id]
        if not matched:
            raise ValueError("Unknown research id")
        selected = matched[0]
        selection = "Explicitly selected from the predeclared candidate catalogue"
    plan = {
        "selected": selected,
        "scenario": scenario,
        "selection_reason": selection,
        "experiment": {"scenario": scenario, "axes": selected["axes"]},
        "threshold_pp": MIN_EFFECT_PP,
        "model_commit": COMMIT,
        "interpretation": "Conditional model sensitivities, not forecasts or empirical causal tests",
    }
    validate_experiment_payload(plan["experiment"])
    model_runs = len(selected["axes"][next(iter(selected["axes"]))])
    for axis in list(selected["axes"])[1:]:
        model_runs *= len(selected["axes"][axis])
    if model_runs + 1 > MAX_MODEL_EVALUATIONS:
        raise ValueError("Research exceeds the fixed model-run budget")
    # The fingerprint is independent of outputs, making ex-post plan changes
    # observable when the complete, exact plan is retained alongside results.
    canonical = json.dumps(plan, sort_keys=True, ensure_ascii=True, separators=(",", ":"))
    fingerprint = sha256(canonical.encode("utf-8")).hexdigest()
    return {
        "plan": plan,
        "plan_sha256": fingerprint,
        "candidate_ranking": [{"id": c["id"], "score": c["priority_score"]} for c in ranked],
        "planned_model_evaluations": model_runs + 1,
    }


def evaluate_predeclared_test(experiment, prediction, threshold_pp):
    """Compare high-vs-low axis at EVERY level of the other controlled axis."""
    axes = experiment["assumptions"]["axes"]
    axis = prediction["axis"]
    other = next((key for key in axes if key != axis), None)
    if axis not in axes or other is None:
        raise ValueError("Prediction does not target a model axis")
    metric = prediction["metric"]
    sign = 1 if prediction["direction"] == "increase" else -1
    if prediction["direction"] not in ("increase", "decrease"):
        raise ValueError("Unknown predicted direction")
    low, high = min(axes[axis]), max(axes[axis])
    comparisons = []
    for fixed_level in axes[other]:
        matching = [
            cell for cell in experiment["cells"]
            if cell["coordinates"][other] == fixed_level
        ]
        low_matches = [c for c in matching if c["coordinates"][axis] == low]
        high_matches = [c for c in matching if c["coordinates"][axis] == high]
        if len(low_matches) != 1 or len(high_matches) != 1:
            raise ValueError("Missing or duplicated controlled model cell")
        delta = round(
            high_matches[0]["summary_2030"][metric]
            - low_matches[0]["summary_2030"][metric], 6
        )
        comparisons.append({"held_axis": other, "held_value": fixed_level,
                            "low": low, "high": high, "observed_delta_pp": delta})
    signed = [sign * c["observed_delta_pp"] for c in comparisons]
    if all(value >= threshold_pp for value in signed):
        outcome = "consistent_with_prediction_in_grid"
    elif all(value <= -threshold_pp for value in signed):
        outcome = "opposite_to_prediction_in_grid"
    else:
        outcome = "mixed_or_below_threshold_in_grid"
    return {
        **prediction,
        "threshold_pp": threshold_pp,
        "outcome": outcome,
        "controlled_comparisons": comparisons,
    }


def run_research(request):
    """Choose, run and audit one candidate only; never iterate autonomously."""
    prepared = prepare(request)
    # Selection and all directional tests are fixed before computing any values.
    experiment = run_experiment(prepared["plan"]["experiment"])
    if experiment["metadata"]["model_runs"] != prepared["planned_model_evaluations"]:
        raise ValueError("Actual calculation exceeded its preregistered budget")
    tests = [
        evaluate_predeclared_test(experiment, p, prepared["plan"]["threshold_pp"])
        for p in prepared["plan"]["selected"]["predictions"]
    ]
    return {
        "research": prepared,
        "tests": tests,
        "experiment": experiment,
        "limitations": [
            "These are conditional US model mechanisms, not probabilities or predictions for real economies.",
            "Model consistency is not independent empirical evidence or a statistical significance test.",
            "This one study explores only its disclosed grid and assumptions; untested values may behave differently.",
            "The Anthropic Economic Index MCP is separate and was not used as model input.",
        ],
    }


def main():
    import sys
    if len(sys.argv) != 1:
        raise SystemExit("Research demonstration accepts no CLI arguments")
    print(json.dumps(run_research({"research": "auto"}), ensure_ascii=False,
                     allow_nan=False, separators=(",", ":")))


if __name__ == "__main__":
    main()
