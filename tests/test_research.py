"""Outcome-blind proposal selection and controlled direction checks."""
import unittest
from unittest.mock import patch

from lab.research import (
    CANDIDATES, MAX_MODEL_EVALUATIONS, evaluate_predeclared_test,
    prepare, proposals, run_research,
)


def synthetic_experiment(plan):
    axes = plan["axes"]
    a, b = list(axes)
    cells = []
    for first in axes[a]:
        for second in axes[b]:
            x = {a: first, b: second}
            rho = x.get("rho", 0.25)
            psi = x.get("psi", 0.75)
            mu = x.get("mu", 0.08)
            cells.append({
                "coordinates": x,
                "summary_2030": {
                    "gdp_gain_pct": 8 + psi,
                    "labor_share_pct": 60 + 5 * rho - 2 * psi,
                    "unemployment_sensitive_pct": 7 - 2 * rho + psi - 3 * mu,
                    "unemployment_total_pct": 4,
                    "wage_gain_pct": 2,
                },
            })
    return {
        "metadata": {"model_runs": 1 + len(cells), "source_commit": "fixture"},
        "assumptions": {"scenario": plan["scenario"], "axes": axes},
        "cells": cells,
    }


class ResearchPlanningTests(unittest.TestCase):
    def test_catalogue_is_ranked_without_running_the_model(self):
        with patch("lab.research.run_experiment") as compute:
            prepared = prepare({"research": "auto"})
            choices = proposals()
        compute.assert_not_called()
        self.assertEqual(prepared["plan"]["selected"]["id"], "new_tasks_vs_automation")
        self.assertEqual([c["priority_score"] for c in choices], [9, 8, 7])
        self.assertEqual(prepared["planned_model_evaluations"], 10)
        self.assertEqual(len(prepared["plan_sha256"]), 64)
        self.assertLessEqual(prepared["planned_model_evaluations"], MAX_MODEL_EVALUATIONS)

    def test_plan_is_repeatable_and_choice_is_explicit(self):
        first = prepare({"research": "auto"})
        second = prepare({"research": "auto"})
        self.assertEqual(first["plan_sha256"], second["plan_sha256"])
        selected = prepare({"research": "new_tasks_vs_mobility"})
        self.assertEqual(selected["plan"]["selected"]["id"], "new_tasks_vs_mobility")
        self.assertNotEqual(first["plan_sha256"], selected["plan_sha256"])
        other_preset = prepare({"research": "auto", "scenario": "modest"})
        self.assertNotEqual(first["plan_sha256"], other_preset["plan_sha256"])

    def test_rejects_unreviewed_free_form_or_execution_inputs(self):
        cases = (
            None, "new tasks", {"research": None}, {"research": 123},
            {"research": "run all models"},
            {"research": "auto", "script": "curl whatever"},
            {"research": "auto", "axes": {"rho": [0, 1]}},
            {"research": "auto", "scenario": "Portugal"},
            {"research": "auto", "scenario": True},
        )
        for request in cases:
            with self.subTest(request=request), self.assertRaises(ValueError):
                prepare(request)
        self.assertEqual(len(CANDIDATES), 3)

    def test_controlled_comparisons_support_and_opposition(self):
        experiment = synthetic_experiment(prepare({"research": "auto"})["plan"]["experiment"])
        first = evaluate_predeclared_test(
            experiment,
            {"axis": "rho", "metric": "labor_share_pct", "direction": "increase"},
            0.02,
        )
        self.assertEqual(first["outcome"], "consistent_with_prediction_in_grid")
        self.assertEqual(len(first["controlled_comparisons"]), 3)
        self.assertEqual(first["controlled_comparisons"][0]["held_axis"], "psi")
        opposite = evaluate_predeclared_test(
            experiment,
            {"axis": "rho", "metric": "labor_share_pct", "direction": "decrease"},
            0.02,
        )
        self.assertEqual(opposite["outcome"], "opposite_to_prediction_in_grid")

    def test_selection_precedes_one_bounded_call(self):
        plan = prepare({"research": "auto"})["plan"]["experiment"]
        with patch("lab.research.run_experiment", return_value=synthetic_experiment(plan)) as compute:
            result = run_research({"research": "auto"})
        compute.assert_called_once_with(plan)
        self.assertEqual(len(result["tests"]), 3)
        self.assertTrue(all(
            t["outcome"] == "consistent_with_prediction_in_grid"
            for t in result["tests"]
        ))
        self.assertIn("model mechanisms", result["limitations"][0])


if __name__ == "__main__":
    unittest.main()
