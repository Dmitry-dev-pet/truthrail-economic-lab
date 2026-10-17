"""Offline guards for population/year-safe Portugal source discovery.

Official 2024 Eurostat all-worker population is not interchangeable with
employer-only QP coverage, 2021 Census or a 2020-22 matched-worker cohort.
"""
from __future__ import annotations

import json
from pathlib import Path
import unittest


BASE = Path(__file__).resolve().parents[1] / "country_profiles" / "portugal" / "2024"


def read(filename):
    return json.loads((BASE / filename).read_text(encoding="utf-8"))


class DetailedOccupationSourceSafety(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.sources = read("detailed_occupation_and_mobility_sources.json")
        cls.calibration = read("calibration_audit.json")
        cls.official = read("isco_two_digit_employment_2024.json")

    def test_source_population_never_silently_switches_to_employer_sample(self):
        sources = self.sources
        self.assertFalse(sources["runnable"])
        self.assertFalse(sources["model_country_profile_running_allowed"])
        self.assertEqual(sources["status"], "PUBLIC_SOURCE_DISCOVERY_NOT_CALIBRATION")
        self.assertEqual(sources["country_code"], "PT")
        self.assertEqual(sources["target_year"], 2024)
        target = sources["target_population"]
        self.assertEqual(target["dataset"], "Eurostat LFSA_EGAI2D")
        self.assertEqual(target["count_thousands"], 5112.3)
        self.assertEqual(target["count_thousands"],
                         self.official["totals"]["employed_thousand"])
        inventory = {x["id"]: x for x in sources["detailed_occupation_evidence"]}
        self.assertEqual(len(inventory), 7)
        self.assertEqual(inventory["EUROSTAT_2024_ISCO2"]["occupational_resolution"],
                         "ISCO-08 2-digit")
        self.assertEqual(inventory["GEP_QUADROS_PESSOAL_2024"]["model_compatible_scope"],
                         False)
        self.assertEqual(inventory["BRIGHTER_FUTURE_2024_QP_OVERVIEW"]["approx_count_millions"],
                         3.65)
        self.assertIsNone(inventory["BRIGHTER_FUTURE_PROFESSIONS"]["reference_year"])
        self.assertEqual(inventory["BRIGHTER_FUTURE_PROFESSIONS"]["availability"],
                         "PUBLIC_OCCUPATION_PROFILE_DIRECTORY_ACCESSIBLE")
        self.assertIn("404", inventory["EUROSTAT_GUESSED_3D_4D"]["availability"])
        self.assertFalse(inventory["INE_CENSUS_2021_OCC"]["model_compatible_scope"])

    def test_matched_sample_two_year_switch_rate_is_not_model_mu(self):
        m = self.sources["observed_occupational_mobility"]
        self.assertEqual((m["starting_occupation_year"], m["ending_occupation_year"]),
                         (2020, 2022))
        self.assertEqual(m["duration_years"], 2)
        self.assertAlmostEqual(m["percent_changing_reported_occupation"], 15.5)
        self.assertAlmostEqual(m["percent_staying_in_reported_occupation"], 84.5)
        self.assertFalse(m["model_mu_bar_compatible"])
        self.assertFalse(m["model_mu_compatible"])
        self.assertIn("both", m["denominator"].lower())
        self.assertTrue(any("C→N" in s for s in m["limitations"]))

    def test_pt_parameter_registry_still_fails_closed(self):
        a = self.calibration
        self.assertEqual(a["status"], "audit_only_not_calibrated")
        self.assertFalse(a["runnable"])
        fields = [*a["parameter_inventory"]["Fixed"],
                  *a["parameter_inventory"]["Scenario"]]
        self.assertEqual(len(fields), 37)
        self.assertTrue(all(x["portugal_model_value"] is None for x in fields))
        by_name = {x["name"]: x for x in fields}
        self.assertEqual(by_name["cog_share"]["calibration_status"], "needs_crosswalk")
        self.assertEqual(by_name["mu_bar"]["calibration_status"], "needs_estimation")
        self.assertEqual(by_name["mu"]["calibration_status"], "scenario_hypothesis")
        for name in ("mu", "mu_bar"):
            self.assertIn("BRIGHTER_FUTURE_QP_OCCUPATIONAL_SWITCH_2020_2022",
                          by_name[name]["candidate_sources"])
        self.assertIn("BRIGHTER_FUTURE_QP_OCCUPATIONS_CATALOG",
                      by_name["cog_share"]["candidate_sources"])
        self.assertEqual(a["sources"]["BRIGHTER_FUTURE_QP_OCCUPATIONAL_SWITCH_2020_2022"]["reference_year"], 2022)


if __name__ == "__main__":
    unittest.main()
