"""Low-cost regression checks for the offline, bounded feasibility protocol."""
import json
import unittest
from aiscen.report import no_ai_column
from aiscen.params import Fixed
from lab.api import compute
from ops.feasibility_scan import PLAN_FILE, FOLLOWUP_GAINS, success, evaluate


class FeasibilityStudyTests(unittest.TestCase):
    def test_plan_is_bounded_and_not_portugal(self):
        plan = json.loads(PLAN_FILE.read_text())
        self.assertEqual(plan["geography"], "USA")
        n = 1
        for values in plan["scan_axes"].values():
            n *= len(values)
        self.assertEqual(n, 240)
        self.assertLessEqual(n + plan["validation"]["draws"] + 1,
                             plan["budget_max_model_runs"])
        self.assertEqual(FOLLOWUP_GAINS, (0.55, 0.65, 0.8))

    def test_success_requires_all_three(self):
        limits = {"gdp_gain_pct_min": 5, "labor_share_pct_min": 60,
                  "unemployment_total_pct_max": 3.8}
        passing = {"gdp_gain_pct": 5, "labor_share_pct": 60,
                   "unemployment_total_pct": 3.8}
        self.assertTrue(success(passing, limits))
        for key, failing in (("gdp_gain_pct", 4.9),
                             ("labor_share_pct", 59.9),
                             ("unemployment_total_pct", 3.9)):
            self.assertFalse(success({**passing, key: failing}, limits))

    def test_reproduce_stronger_cognitive_guard_candidate(self):
        reference = no_ai_column(Fixed())["Unemployment rate, cognitive, pct"]
        plan = json.loads(PLAN_FILE.read_text())
        candidate = evaluate({"psi": 0.75, "rho": 1.0, "mu": 0.34,
                              "theta_H": 0.5, "a_2030": 0.8},
                             plan["criteria"], reference)
        self.assertTrue(candidate["meets_three"])
        self.assertTrue(candidate["also_meets_sensitive_unemployment"])
        self.assertAlmostEqual(candidate["summary_2030"]["gdp_gain_pct"], 5.1658, places=3)
        self.assertAlmostEqual(candidate["summary_2030"]["unemployment_total_pct"],
                               3.748529, places=3)
        self.assertEqual(compute({"scenario": "substantial"})["inputs"]["scenario"],
                         "substantial")


if __name__ == "__main__":
    unittest.main()
