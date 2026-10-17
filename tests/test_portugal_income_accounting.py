"""Verify the archived national-accounts identities without running a PT model."""
from decimal import Decimal
import json
from pathlib import Path
import unittest


ROOT = Path(__file__).resolve().parents[1]
PROFILE = ROOT / "country_profiles" / "portugal" / "2024"


class PortugalIncomeAccountingTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.audit = json.loads((PROFILE / "ameco_income_accounting_2024.json").read_text())
        cls.values = {key: Decimal(row["value_2024"])
                      for key, row in cls.audit["series"].items()}

    def test_published_income_components_reconcile_before_valuation_choice(self):
        v = self.values
        tolerance = Decimal("0.00002")  # billion EUR; rounded source components
        self.assertLessEqual(abs(v["UTVT"] - v["UYVT"] - v["UTVN"]), tolerance)
        self.assertLessEqual(abs(v["UVGD"] - v["UTVN"] - v["UYGD"]), tolerance)
        self.assertLessEqual(abs(v["UWCD"] + v["UOGD"] - v["UYGD"]), tolerance)
        self.assertEqual(v["NETD"] - v["NWTD"], v["NSTD"])

    def test_self_employment_imputation_matches_adjusted_operating_surplus(self):
        v = self.values
        imputed = v["UWCD"] * v["NSTD"] / v["NWTD"]
        labor = v["UWCD"] * v["NETD"] / v["NWTD"]
        self.assertLessEqual(abs(v["UOGD"] - v["UQGD"] - imputed), Decimal("0.00002"))
        self.assertLessEqual(abs(labor + v["UQGD"] - v["UYGD"]), Decimal("0.00002"))
        self.assertAlmostEqual(labor, Decimal("162.69402307615445"), places=10)
        self.assertAlmostEqual(imputed, Decimal("24.72711307615445"), places=10)

    def test_both_published_wage_shares_follow_from_their_own_denominators(self):
        v = self.values
        labor = v["UWCD"] * v["NETD"] / v["NWTD"]
        for code, denominator in (("ALCD0", "UVGD"), ("ALCD2", "UYGD")):
            reconstructed = 100 * labor / v[denominator]
            self.assertLessEqual(abs(v[code] - reconstructed), Decimal("0.00001"))
        self.assertEqual(v["ALCD2"], Decimal("64.59205"))
        self.assertEqual(v["ALCD0"], Decimal("56.14314"))
        self.assertEqual(v["ALCD2"] - v["ALCD0"], Decimal("8.44891"))
        # Omitting self-employed labor or substituting a different employment
        # universe must fail these national-accounts reconstruction identities.
        for wrong_labor in (
            v["UWCD"],
            v["UWCD"] * v["NELN"] / v["NWTD"],
            v["UWCD"] * v["NETN"] / v["NWTD"],
        ):
            self.assertGreater(abs(100 * wrong_labor / v["UYGD"] - v["ALCD2"]), Decimal("0.1"))

    def test_source_formats_and_series_units_remain_distinguishable(self):
        a = self.audit
        self.assertEqual(a["reference_year"], 2024)
        self.assertEqual(a["publication_vintage"], "Spring 2026, download page updated 2026-06-03")
        check = a["cross_format_verification"]
        self.assertEqual(check["compared_cells"], len(check["series"]) * (2027 - 1960 + 1))
        self.assertEqual(check["unequal_cells"], 0)
        for key in check["series"]:
            row = a["series"][key]
            self.assertEqual(row["value_2024"], row["txt_value_2024"])
            self.assertEqual(row["series_code"], "PRT.1.0.0.0." + key)
        self.assertEqual(a["series"]["ALCD2"]["unit_as_published"], "Percentage of GDP at factor cost")
        self.assertEqual(a["series"]["ALCD0"]["unit_as_published"], "Percentage of GDP")
        for key in ("NETD", "NWTD", "NSTD", "NETN", "NELN"):
            self.assertEqual(a["series"][key]["unit_as_published"], "1000 persons")

    def test_official_accounting_observations_do_not_enable_country_execution(self):
        a = self.audit
        self.assertIs(a["runnable"], False)
        self.assertIsNone(a["model_mapping"]["model_value"])
        self.assertIs(a["model_mapping"]["safe_to_assign_to_model"], False)
        registry = json.loads((PROFILE / "calibration_audit.json").read_text())
        self.assertIs(registry["runnable"], False)
        fields = [entry for block in registry["parameter_inventory"].values()
                  for entry in block]
        self.assertEqual(len(fields), 37)
        self.assertTrue(all(entry["portugal_model_value"] is None for entry in fields))
        self.assertEqual(registry["sources"]["AMECO_WAGE_SHARE"]["snapshot_file"],
                         "ameco_income_accounting_2024.json")


if __name__ == "__main__":
    unittest.main()
