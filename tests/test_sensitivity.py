"""Offline controls for a fixed sensitivity audit (no model package needed)."""
import math
import unittest
from unittest.mock import patch

from lab.api import BOUNDS, FIXED_BOUNDS, COMMIT
from lab.sensitivity import (
    MAX_EVALUATIONS, METRICS, PARAMETERS, RANGE_FRACTION,
    bounded_window, prepare_sensitivity, run_sensitivity, validate_request,
)


class SensitivityValidation(unittest.TestCase):
    def setUp(self):
        self.catalog = {
            "model_commit": COMMIT,
            "presets": {"substantial": {
                "m_2030": 0.14,
                "d_2030": 0.50,
                "a_2030": 0.70,
                "psi": 0.75,
                "rho": 0.25,
                "mu": 0.08,
                "theta_H": 0.40,
            }},
            "fixed_defaults": {"eps": 6.0, "xi": 0.75},
        }

    def test_strict_request(self):
        self.assertEqual(
            validate_request({"analysis": "sensitivity", "scenario": "substantial"}),
            "substantial",
        )
        invalid = [
            {}, {"analysis": "sensitivity"}, {"scenario": "substantial"},
            {"analysis": "sensitivity", "scenario": "substantial", "cmd": "echo x"},
            {"analysis": "run everything", "scenario": "substantial"},
            {"analysis": "sensitivity", "scenario": "Portugal"},
            {"analysis": "sensitivity", "scenario": True},
            {"analysis": False, "scenario": "substantial"},
            ["sensitivity", "substantial"],
        ]
        for request in invalid:
            with self.subTest(request=request), self.assertRaises(ValueError):
                validate_request(request)

    def test_equal_width_and_boundaries(self):
        samples = [
            (0.14, BOUNDS["m_2030"]),
            (0.95, BOUNDS["m_2030"]),
            (0.50, BOUNDS["psi"]),
            (0.001, BOUNDS["mu"]),
            (10.0, FIXED_BOUNDS["eps"]),
        ]
        for baseline, bounds in samples:
            low, high = bounded_window(baseline, bounds)
            self.assertGreaterEqual(low, bounds[0])
            self.assertLessEqual(high, bounds[1])
            self.assertLessEqual(low, baseline)
            self.assertGreaterEqual(high, baseline)
            self.assertAlmostEqual(
                high - low, (bounds[1] - bounds[0]) * RANGE_FRACTION,
            )
        with self.assertRaises(ValueError):
            bounded_window(math.nan, BOUNDS["psi"])
        with self.assertRaises(ValueError):
            bounded_window(1.01, BOUNDS["psi"])

    def test_precomputed_fingerprint_and_exact_budget(self):
        with patch("lab.sensitivity.presets", return_value=self.catalog):
            a = prepare_sensitivity({"analysis": "sensitivity", "scenario": "substantial"})
            b = prepare_sensitivity({"analysis": "sensitivity", "scenario": "substantial"})
        self.assertEqual(a["plan_sha256"], b["plan_sha256"])
        self.assertEqual(len(a["plan_sha256"]), 64)
        self.assertEqual(a["planned_model_evaluations"], MAX_EVALUATIONS)
        self.assertEqual(MAX_EVALUATIONS, 19)
        self.assertEqual(len(a["plan"]["sampling"]), 9)
        self.assertEqual({x["parameter"] for x in a["plan"]["sampling"]}, set(PARAMETERS))
        self.assertEqual(a["plan"]["sampling"][0]["parameter"], "m_2030")
        self.assertEqual(a["plan"]["sampling"][-1]["parameter"], "xi")

    def test_one_parameter_per_call_and_per_metric_ranking(self):
        request = {"analysis": "sensitivity", "scenario": "substantial"}
        nominal = {**self.catalog["presets"]["substantial"],
                   **self.catalog["fixed_defaults"]}
        coefficients = {
            "gdp_gain_pct": {"m_2030": 5, "psi": 1, "rho": 2},
            "labor_share_pct": {"m_2030": 1, "rho": 50},
            "unemployment_total_pct": {"mu": -5},
            "unemployment_sensitive_pct": {"mu": -40, "psi": 1},
            "wage_gain_pct": {"a_2030": 5},
        }
        calls = []

        def fake_model(payload):
            calls.append(payload)
            params = {**nominal, **payload.get("parameters", {}),
                      **payload.get("fixed", {})}
            metrics = {
                name: 10 + sum(params[key] * coeff for key, coeff in terms.items())
                for name, terms in coefficients.items()
            }
            return {"metadata": {"source_commit": COMMIT},
                    "summary_2030": metrics}

        with patch("lab.sensitivity.presets", return_value=self.catalog), \
             patch("lab.sensitivity.compute", side_effect=fake_model):
            result = run_sensitivity(request)
        self.assertEqual(len(calls), MAX_EVALUATIONS)
        self.assertEqual(calls[0], {"scenario": "substantial"})
        for request in calls[1:]:
            self.assertEqual(len(request.get("parameters", {})) +
                             len(request.get("fixed", {})), 1)
        self.assertEqual(result["metadata"]["model_evaluations"], 19)
        self.assertEqual(len(result["measurements"]), 9)
        self.assertEqual(set(result["rankings"]), set(METRICS))
        self.assertEqual(result["rankings"]["labor_share_pct"][0]["parameter"], "rho")
        self.assertEqual(result["rankings"]["unemployment_sensitive_pct"][0]["parameter"], "mu")
        self.assertGreater(
            result["rankings"]["labor_share_pct"][0]["absolute_change_pp"],
            result["rankings"]["labor_share_pct"][1]["absolute_change_pp"],
        )
        self.assertTrue(all(
            entry["absolute_change_pp"] >= 0
            for rows in result["rankings"].values() for entry in rows
        ))


if __name__ == "__main__":
    unittest.main()
