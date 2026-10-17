"""Regression checks for the frozen, 2025-26, 10-sector public BTOS panel."""
import math
import unittest

from ops.btos_lag_study import DATA, PERIODS, SECTORS, load_panel, observations, run


class TestBtosSectorLeadLag(unittest.TestCase):
    def test_snapshot_complete_and_bounded(self):
        self.assertTrue(DATA.is_file())
        payload, panel = load_panel()
        self.assertEqual(len(panel), 120)
        self.assertEqual(payload["status"], "complete snapshot (no inference yet)")
        self.assertEqual((PERIODS[0], PERIODS[-1]), (88, 110))
        self.assertEqual(len(SECTORS), 10)
        self.assertAlmostEqual(panel["51", 88]["ai_pct"], 41.0)
        self.assertAlmostEqual(panel["51", 110]["ai_pct"], 50.2)

    def test_pairs_have_strictly_future_outcomes(self):
        _, panel = load_panel()
        obs = observations(panel)
        self.assertEqual(len(obs), 100)
        self.assertTrue(all(row["next_period"] == PERIODS[row["t"] + 1]
                            for row in obs))
        self.assertTrue(all(0 <= row["ai"] <= 100 for row in obs))
        self.assertEqual(sum(row["t"] <= 7 for row in obs), 70)
        self.assertEqual(sum(row["t"] > 7 for row in obs), 30)

    def test_reproduce_fixed_holdout_comparison(self):
        receipt = run()
        self.assertEqual(receipt["records"], 120)
        self.assertEqual(receipt["training_observations"], 70)
        self.assertEqual(receipt["holdout_observations"], 30)
        self.assertEqual(receipt["holdout_outcome_periods"], [106, 108, 110])
        self.assertAlmostEqual(receipt["equal_weight_sector_ai_pct_start"], 18.57, places=2)
        self.assertAlmostEqual(receipt["equal_weight_sector_ai_pct_end"], 25.48, places=2)
        self.assertAlmostEqual(receipt["holdout_persistence"]["rmse"], 1.588815, places=4)
        self.assertAlmostEqual(receipt["models"]["no_ai"]["holdout"]["rmse"], 2.574525, places=4)
        self.assertAlmostEqual(receipt["models"]["ai_level"]["holdout"]["rmse"], 2.609539, places=4)
        self.assertAlmostEqual(receipt["models"]["ai_change"]["holdout"]["rmse"], 2.559676, places=4)
        self.assertGreater(receipt["models"]["ai_level"]["holdout"]["rmse"],
                           receipt["models"]["no_ai"]["holdout"]["rmse"])
        for obj in receipt["models"].values():
            self.assertTrue(math.isfinite(obj["holdout"]["rmse"]))
            self.assertEqual(obj["holdout"]["n"], 30)


if __name__ == "__main__":
    unittest.main()
