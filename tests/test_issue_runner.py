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

    def test_rejects_bad_json_without_running_model(self):
        with patch("lab.issue_runner.run_experiment") as fn:
            for raw in ("", "not-json", "a"*(MAX_ISSUE_BYTES+1)):
                with self.subTest(raw=raw[:12]), self.assertRaises(ValueError):
                    report_from_issue_body(raw)
            fn.assert_not_called()


if __name__ == "__main__":
    unittest.main()
