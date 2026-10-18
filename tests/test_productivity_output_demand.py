"""Small offline regression checks for published-vintage output and hours study."""
import math
import unittest

from ops.productivity_output_demand import (
    DATA, PLAN, load, observations, classify_2025, run
)


class TestBlsPhenomenologicalOutputDemand(unittest.TestCase):
    def test_data_complete_no_overlapping_industries(self):
        data, plan, lookup = load()
        self.assertTrue(DATA.exists() and PLAN.exists())
        self.assertEqual(len(data["selected_naics"]), 28)
        self.assertEqual(len(data["rows"]), 112)
        self.assertEqual(len(lookup), 112)
        self.assertEqual(plan["training_years"], [2023, 2024])
        self.assertEqual(plan["heldout_year"], 2025)
        self.assertAlmostEqual(lookup["5112", 2025]["real_output_pct"], 12.1)
        self.assertAlmostEqual(lookup["5112", 2025]["total_hours_pct"], -0.7)
        self.assertAlmostEqual(lookup["5112", 2025]["labor_productivity_pct"], 12.9)

    def test_2025_industry_quadrants(self):
        data, _, lookup = load()
        r = [x for x in observations(data, lookup) if x["year"] == 2025]
        self.assertEqual(len(r), 28)
        quadrants = classify_2025(r)
        self.assertEqual(quadrants["output_up_hours_up"], 11)
        self.assertEqual(quadrants["output_up_hours_down"], 7)
        self.assertEqual(quadrants["output_down_hours_up"], 6)
        self.assertEqual(quadrants["output_down_hours_down"], 4)
        self.assertEqual(quadrants["boundary_zero"], 0)

    def test_2025_held_out_models_and_honest_negative_result(self):
        r = run()
        self.assertEqual(r["n_annual_source_rows"], 112)
        self.assertEqual(r["n_train"], 56)
        self.assertEqual(r["n_holdout"], 28)
        self.assertEqual(r["holdout_year"], 2025)
        scores = r["next_year_real_output_forecast"]
        self.assertAlmostEqual(scores["persistence"]["holdout"]["rmse_pp"], 4.328807, places=4)
        self.assertAlmostEqual(scores["M0"]["holdout"]["rmse_pp"], 4.794902, places=4)
        self.assertAlmostEqual(scores["M1"]["holdout"]["rmse_pp"], 4.744653, places=4)
        self.assertLess(scores["M1"]["holdout"]["rmse_pp"], scores["M0"]["holdout"]["rmse_pp"])
        self.assertLess(scores["persistence"]["holdout"]["rmse_pp"],
                        scores["M1"]["holdout"]["rmse_pp"])
        hours = r["next_year_hours_forecast"]
        self.assertAlmostEqual(hours["hours_persistence"]["holdout"]["rmse_pp"], 4.068476, places=4)
        self.assertAlmostEqual(hours["hours_M0"]["holdout"]["rmse_pp"], 4.128450, places=4)
        self.assertAlmostEqual(hours["hours_M1"]["holdout"]["rmse_pp"], 4.149842, places=4)
        self.assertLess(hours["hours_persistence"]["holdout"]["rmse_pp"],
                        hours["hours_M1"]["holdout"]["rmse_pp"])
        for metric in (scores, hours):
            self.assertTrue(all(math.isfinite(v["holdout"]["rmse_pp"]) for v in metric.values()))
        self.assertEqual(len(r["holdout_observations"]), 28)


if __name__ == "__main__":
    unittest.main()
