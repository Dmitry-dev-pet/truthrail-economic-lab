"""Check hypothesis provenance and both posthoc path-dependence falsification steps."""
import unittest

from ops.research_adoption_timing import run_research


class AdoptionTimingResearchTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.r = run_research()

    def test_preregistered_nine_path_model_reproduction(self):
        r = self.r
        self.assertEqual(r["provenance"]["total_simulations"], 15)
        self.assertEqual(len(r["primary"]["results"]), 9)
        self.assertTrue(r["provenance"]["first_plan_before_simulation"])
        self.assertTrue(r["provenance"]["controls_added_posthoc"])
        self.assertTrue(r["primary"]["H1_direction_supported"])
        self.assertTrue(r["primary"]["H2_direction_supported"])
        d = r["primary"]["front_minus_back_2030"]
        self.assertAlmostEqual(d["Unemployment rate, cognitive, pct"],
                               -1.55645498176109, places=5)
        self.assertAlmostEqual(d["GDP, pct above no-AI"],
                               1.11982756526796, places=5)

    def test_full_shared_early_history_and_2030_endpoints(self):
        for key in ("control_1", "control_2"):
            group = self.r["posthoc_controls"][key]
            self.assertTrue(group["posthoc"])
            self.assertEqual(len(group["results"]), 3)
            paths = group["results"]
            for index in (0, 1, 5):
                for metric in ("m", "d", "a"):
                    numbers = [p["snapshots"][index][metric] for p in paths]
                    self.assertLess(max(numbers)-min(numbers), 1e-10)
            for index in (0, 1):
                for metric in ("l_c", "U_c"):
                    numbers = [p["snapshots"][index][metric] for p in paths]
                    self.assertLess(max(numbers)-min(numbers), 1e-10)

    def test_strict_endpoint_slope_control_retains_history_effect(self):
        c = self.r["posthoc_controls"]["control_2"]
        d = c["front_minus_back_2030"]
        self.assertAlmostEqual(d["Unemployment rate, cognitive, pct"],
                               -1.055580493469859, places=5)
        self.assertAlmostEqual(d["Unemployment rate, all workers, pct"],
                               -0.610766236181522, places=5)
        self.assertAlmostEqual(d["GDP, pct above no-AI"],
                               0.686287200126089, places=5)
        self.assertLess(d["Labor share, pct of income"], 0)
        front = next(r for r in c["results"] if r["alpha"] == 2.5)
        late = next(r for r in c["results"] if r["alpha"] == -2.5)
        # In the same 2030 target, actual labor stocks still differ by history.
        self.assertAlmostEqual(front["snapshots"][-1]["l_c_frictionless"],
                               late["snapshots"][-1]["l_c_frictionless"],
                               places=9)
        self.assertLess(front["snapshots"][3]["u_c"],
                        front["snapshots"][4]["u_c"] + 0.0)
        self.assertGreater(front["snapshots"][3]["u_c"],
                           late["snapshots"][3]["u_c"])
        self.assertLess(front["snapshots"][-1]["u_c"],
                        late["snapshots"][-1]["u_c"])


if __name__ == "__main__":
    unittest.main()
