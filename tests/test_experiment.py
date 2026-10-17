"""Offline tests for bounded research experiments (no upstream clone needed)."""
import math
import unittest
from unittest.mock import patch

from lab.experiment import DEMO, run_experiment, validate_experiment_payload


class ExperimentValidation(unittest.TestCase):
    def test_demo_contract(self):
        name, axes, baseline, fixed = validate_experiment_payload(DEMO)
        self.assertEqual(name, "substantial")
        self.assertEqual(len(axes["psi"]), 3)
        self.assertEqual(len(axes["mu"]), 3)
        self.assertEqual(baseline, {})
        self.assertEqual(fixed, {})

    def test_rejects_unsafe_or_ambiguous_inputs(self):
        base = {"axes": {"psi": [0.2, 0.6], "mu": [0.03, 0.1]}}
        bad = [
            {**base, "script": "python x.py"},
            {**base, "axes": {"psi": [0.2, 0.6]}},
            {**base, "axes": {"psi": [0.2, 0.6], "command": [0.1, 0.2]}},
            {**base, "axes": {"psi": [0.2, 0.2], "mu": [0.03, 0.1]}},
            {**base, "axes": {"psi": [0.2, True], "mu": [0.03, 0.1]}},
            {**base, "axes": {"psi": [0.2, math.inf], "mu": [0.03, 0.1]}},
            {**base, "axes": {"psi": [0.2, 2.0], "mu": [0.03, 0.1]}},
            {**base, "axes": {"psi": [0.2, 0.6], "mu": [0.03]}},
            {**base, "baseline_overrides": {"psi": 0.7}},
            {**base, "fixed": {"extra": 1}},
            {**base, "axes": {"psi": [0.1] * 6, "mu": [0.03, 0.1]}},
        ]
        for item in bad:
            with self.subTest(item=item), self.assertRaises(ValueError):
                validate_experiment_payload(item)

    def test_grid_and_deltas(self):
        def fake_compute(payload):
            p = payload.get("parameters", {})
            psi = p.get("psi", 0.5)
            mu = p.get("mu", 0.06)
            return {
                "metadata": {"source_commit": "pinned", "geography": "USA"},
                "inputs": {"parameters": {"psi": psi, "mu": mu}, "fixed": {"eps": 6.0}},
                "summary_2030": {
                    "gdp_gain_pct": round(10 * psi, 6),
                    "labor_share_pct": round(60 - 5 * psi + mu, 6),
                },
            }

        request = {"axes": {"psi": [0.25, 0.75], "mu": [0.03, 0.12]}}
        with patch("lab.experiment.compute", side_effect=fake_compute) as mock_compute:
            output = run_experiment(request)
        self.assertEqual(mock_compute.call_count, 5)
        self.assertEqual(output["metadata"]["model_runs"], 5)
        self.assertEqual(output["metadata"]["source_commit"], "pinned")
        self.assertEqual(len(output["cells"]), 4)
        self.assertEqual(output["cells"][0]["coordinates"], {"psi": 0.25, "mu": 0.03})
        self.assertEqual(output["cells"][0]["delta_vs_baseline_pp"]["gdp_gain_pct"], -2.5)
        self.assertEqual(output["cells"][3]["delta_vs_baseline_pp"]["gdp_gain_pct"], 2.5)


if __name__ == "__main__":
    unittest.main()
