"""Checks for the transparent, non-calibrated market-demand mechanism."""
import unittest

from ops.demand_productivity_mechanism import (
    check_bls_rows, implied_hours_growth, market_response,
    equilibrium_elasticity_threshold,
)


class TestDemandProductivityMechanism(unittest.TestCase):
    def test_bls_rounded_accounting_identity(self):
        result = check_bls_rows()
        self.assertEqual(len(result["rows"]), 10)
        self.assertLess(result["max_abs_rounding_residual_pp"], 0.05)
        by_naics = {r["naics"]: r for r in result["rows"]}
        self.assertLess(by_naics["5112"]["reported_hours_growth_pct"], 0)
        self.assertGreater(by_naics["7132"]["reported_hours_growth_pct"], 0)
        self.assertLess(by_naics["3369"]["reported_hours_growth_pct"], -10)

    def test_model_boundary_and_demand_contrast(self):
        low = market_response(productivity_gain_pct=10,
                              price_pass_through=0.8, demand_price_elasticity=0.5)
        balanced = market_response(productivity_gain_pct=10,
                                   price_pass_through=0.8, demand_price_elasticity=1.25)
        high = market_response(productivity_gain_pct=10,
                               price_pass_through=0.8, demand_price_elasticity=2)
        self.assertAlmostEqual(low["labor_hours_growth_pct"], -5.558, places=2)
        self.assertAlmostEqual(balanced["labor_hours_growth_pct"], 0, places=9)
        self.assertAlmostEqual(high["labor_hours_growth_pct"], 5.885, places=2)
        self.assertAlmostEqual(
            equilibrium_elasticity_threshold(productivity_gain_pct=10,
                                             price_pass_through=0.8), 1.25)

    def test_autonomous_demand_and_work_hours_affect_workers(self):
        args = dict(productivity_gain_pct=10, price_pass_through=0,
                    demand_price_elasticity=2)
        no_demand = market_response(**args)
        shifted = market_response(**args, autonomous_real_demand_growth_pct=20)
        self.assertLess(no_demand["worker_count_growth_pct"], 0)
        self.assertGreater(shifted["worker_count_growth_pct"], 0)
        hours_change = market_response(**args, autonomous_real_demand_growth_pct=20,
                                       hours_per_worker_growth_pct=10)
        self.assertLess(hours_change["worker_count_growth_pct"],
                        shifted["worker_count_growth_pct"])
        self.assertIsNone(equilibrium_elasticity_threshold(
            productivity_gain_pct=10, price_pass_through=0))

    def test_invalid_inputs_fail_closed(self):
        with self.assertRaises(ValueError):
            market_response(productivity_gain_pct=-5, price_pass_through=1,
                            demand_price_elasticity=1)
        with self.assertRaises(ValueError):
            market_response(productivity_gain_pct=10, price_pass_through=1.5,
                            demand_price_elasticity=1)
        with self.assertRaises(ValueError):
            implied_hours_growth(1, -100)


if __name__ == "__main__":
    unittest.main()
