"""No-network owner issue adapter tests."""
import unittest
from unittest.mock import patch
from lab.issue_runner import MAX_ISSUE_BYTES, format_report, report_from_issue_body


class OwnerIssueReportTests(unittest.TestCase):
    def test_renders_bounded_report(self):
        demo = {
            "metadata": {"model_runs": 2, "source_commit": "pinned"},
            "assumptions": {"scenario": "substantial", "axes": {"psi": [0.2, 0.5], "mu": [0.03, 0.06]}},
            "baseline": {"summary_2030": {
                "gdp_gain_pct": 8.28, "labor_share_pct": 56.10,
                "unemployment_total_pct": 4.52, "unemployment_sensitive_pct": 4.49,
                "wage_gain_pct": 2.5,
            }},
            "cells": [{"coordinates": {"psi": 0.2, "mu": 0.03},
                       "summary_2030": {"gdp_gain_pct": 6.0, "labor_share_pct": 58,
                                        "unemployment_total_pct": 4, "unemployment_sensitive_pct": 4.3,
                                        "wage_gain_pct": 2.0}}],
        }
        with patch("lab.issue_runner.run_experiment", return_value=demo) as fn:
            msg = report_from_issue_body('{"axes":{"psi":[0.2,0.5],"mu":[0.03,0.06]}}')
        fn.assert_called_once()
        self.assertIn("pinned", msg)
        self.assertIn("| 0.200 | 0.030 |", msg)
        self.assertIn("not forecasts", msg)
        self.assertIn("No Mac access", msg)

    def test_research_issue_routes_to_pinned_planner(self):
        mock_report = {
            "research": {
                "plan": {
                    "selected": {
                        "question": "How are tasks reinstated?",
                        "hypothesis": "Labor share rises as rho increases",
                        "alternative": "No monotonic change",
                        "scientific_note": "rho is new tasks",
                        "predictions": [{"axis": "rho", "metric": "labor_share_pct", "direction": "increase"}],
                    },
                    "selection_reason": "Predeclared score",
                    "scenario": "substantial",
                },
                "plan_sha256": "0" * 64,
                "candidate_ranking": [{"id": "new_tasks_vs_automation", "score": 9}],
            },
            "experiment": {
                "assumptions": {"axes": {"psi": [0.5, 0.9], "rho": [0, 0.5]}},
                "metadata": {"source_commit": "upstream-pinned", "model_runs": 5},
                "baseline": {"summary_2030": {
                    "gdp_gain_pct": 8.3, "labor_share_pct": 56,
                    "unemployment_total_pct": 4.5, "unemployment_sensitive_pct": 4.5,
                    "wage_gain_pct": 2.1,
                }},
                "cells": [{"coordinates": {"psi": 0.5, "rho": 0.0},
                           "summary_2030": {
                               "gdp_gain_pct": 8, "labor_share_pct": 55,
                               "unemployment_total_pct": 4.4,
                               "unemployment_sensitive_pct": 4.2, "wage_gain_pct": 2,
                           }}],
            },
            "tests": [{
                "axis": "rho", "metric": "labor_share_pct",
                "threshold_pp": 0.02, "outcome": "consistent_with_prediction_in_grid",
                "controlled_comparisons": [{
                    "held_axis": "psi", "held_value": 0.5,
                    "observed_delta_pp": 1.2,
                }],
            }],
            "limitations": ["Not a forecast"],
        }
        with patch("lab.issue_runner.run_research", return_value=mock_report) as fn:
            with patch("lab.issue_runner.run_experiment") as old:
                message = report_from_issue_body('{"research":"auto"}')
        fn.assert_called_once_with({"research": "auto"})
        old.assert_not_called()
        self.assertIn("fingerprint", message)
        self.assertIn("written before computation", message)
        self.assertIn("consistent_with_prediction_in_grid", message)
        self.assertIn("| 0.500 | 0.000 |", message)
        self.assertIn("Not a forecast", message)

    def test_rejects_bad_json_without_running_model(self):
        with patch("lab.issue_runner.run_experiment") as fn:
            for raw in ("", "not-json", "a"*(MAX_ISSUE_BYTES+1)):
                with self.subTest(raw=raw[:12]), self.assertRaises(ValueError):
                    report_from_issue_body(raw)
            fn.assert_not_called()


if __name__ == "__main__":
    unittest.main()
