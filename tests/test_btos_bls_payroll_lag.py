"""Data integrity and holdout reproduction of Census-BLS payroll lag test."""
import math
import unittest

from ops.btos_bls_payroll_lag import (
    load_study, make_rows, month_offset, run
)


class TestCensusBlsActualPayrollLag(unittest.TestCase):
    def test_sources_and_publication_boundary(self):
        plan, btos, bls, btos_idx, bls_idx = load_study()
        self.assertEqual(len(btos["records"]), 120)
        self.assertEqual(sum(len(s["observations"]) for s in bls["series"]), 210)
        self.assertEqual(len(bls_idx), 10)
        self.assertEqual(sorted(plan["held_out_exposure_waves"]), [102, 104, 106])
        self.assertEqual(max(m for s in bls_idx.values() for m in s), "2026-09")
        self.assertNotIn("2026-10", bls_idx["51"])
        self.assertAlmostEqual(bls_idx["51"]["2026-09"], 2739.0)
        self.assertAlmostEqual(bls_idx["51"]["2025-11"], 2848.0)

    def test_temporal_alignment_includes_cross_month_surveys(self):
        plan, _, _, btos_idx, bls_idx = load_study()
        rows = make_rows(plan, btos_idx, bls_idx)
        self.assertEqual(len(rows), 90)
        mapping = {(r["sector"], r["wave"]): r for r in rows}
        self.assertEqual(mapping["51", 90]["origin_month"], "2025-12")
        self.assertEqual(mapping["51", 90]["outcome_month"], "2026-01")
        self.assertEqual(mapping["51", 104]["origin_month"], "2026-07")
        self.assertEqual(mapping["51", 104]["outcome_month"], "2026-08")
        self.assertEqual(mapping["51", 106]["origin_month"], "2026-08")
        self.assertEqual(mapping["51", 106]["outcome_month"], "2026-09")
        for row in rows:
            self.assertEqual(month_offset(row["origin_month"], 1), row["outcome_month"])
            self.assertLessEqual(row["outcome_month"], "2026-09")
            self.assertTrue(math.isfinite(row["future_payroll_growth"]))

    def test_fixed_train_and_holdout_results(self):
        receipt = run()
        self.assertEqual(receipt["n_training"], 60)
        self.assertEqual(receipt["n_test"], 30)
        self.assertEqual(receipt["holdout_outcome_months"],
                         ["2026-07", "2026-08", "2026-09"])
        expected = {"persistence": 0.200278, "M0": 0.158549,
                    "M1_AIlevel": 0.158173, "M2_AIchange": 0.157846}
        for model, rmse in expected.items():
            res = receipt["models"][model]["holdout"]
            self.assertEqual(res["n"], 30)
            self.assertAlmostEqual(res["rmse"], rmse, places=4)
            self.assertTrue(math.isfinite(res["mae"]))
        self.assertLess(receipt["models"]["M1_AIlevel"]["holdout"]["rmse"],
                        receipt["models"]["M0"]["holdout"]["rmse"])
        self.assertLess(receipt["models"]["M2_AIchange"]["holdout"]["rmse"],
                        receipt["models"]["M0"]["holdout"]["rmse"])
        self.assertLess(receipt["models"]["M0"]["holdout"]["rmse"],
                        receipt["models"]["persistence"]["holdout"]["rmse"])


if __name__ == "__main__":
    unittest.main()
