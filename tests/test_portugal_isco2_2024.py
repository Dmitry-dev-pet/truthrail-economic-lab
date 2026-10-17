"""Reproduce the Portugal 2024 two-digit occupational-data audit offline.

Official counts (Eurostat LFSA_EGAI2D) are kept distinct from the UNVERIFIED
SOC–ISCO mirror's code classes. No calibration or PT model simulation.
"""
from __future__ import annotations

import json
from pathlib import Path
import unittest


ROOT = Path(__file__).resolve().parents[1] / "country_profiles" / "portugal" / "2024"


def load(name):
    return json.loads((ROOT / name).read_text(encoding="utf-8"))


class PortugalISCO2OfficialWeightsTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.official = load("isco_two_digit_employment_2024.json")
        cls.mapped = load("soc_isco_employment_weighted_review_2024.json")
        cls.coarse = load("isco_occupation_snapshot.json")
        cls.mirror = load("soc2010_isco08_crosswalk_audit.json")
        cls.audit = load("calibration_audit.json")

    def test_source_units_and_explicit_missing_low_reliability_flags(self):
        d = self.official
        self.assertFalse(d["runnable"])
        self.assertEqual(d["source"]["dataset"], "lfsa_egai2d")
        self.assertEqual(d["source"]["geo"], "PT")
        self.assertEqual(d["source"]["time"], "2024")
        self.assertEqual(d["source"]["unit"], "THS_PER")
        self.assertEqual(d["source"]["age"], "Y_GE15")
        self.assertEqual(d["source"]["updated"], "2026-09-10T23:00:00+0200")
        self.assertEqual(len(d["counts"]), 55)
        self.assertEqual(d["data_quality"]["missing_data"], ["OC63", "NRP"])
        flagged = {v["code"]: v["flag"] for v in d["data_quality"]["flagged_codes"]}
        self.assertEqual(flagged, {"OC01": "u", "OC02": "u", "OC03": "u", "OC95": "u"})
        counted = {entry["code"]: entry for entry in d["counts"]}
        self.assertIsNone(counted["OC63"]["thousands"])
        self.assertIsNone(counted["NRP"]["thousands"])
        self.assertEqual(counted["OC52"]["thousands"], 374.3)
        self.assertEqual(counted["OC35"]["thousands"], 51.0)
        self.assertEqual(counted["TOTAL"]["thousands"], self.coarse["category_counts"]["TOTAL"]["thousands"])
        self.assertEqual(d["totals"]["provisional_civilian_thousand"], 5090.0)

    def test_submajors_reconcile_to_major_totals_with_rounding(self):
        d = self.official
        for _, item in d["data_quality"]["major_reconciliation"].items():
            self.assertLessEqual(abs(item["rounding_difference_thousand"]), 0.11)
        self.assertEqual(
            d["data_quality"]["major_reconciliation"]["OC6"]["missing_codes"],
            ["OC63"],
        )
        self.assertAlmostEqual(
            d["data_quality"]["submajor_known_sum_thousand"], 5112.1, places=1
        )

    def test_unverified_mapping_weight_join_and_coverage(self):
        m = self.mapped
        self.assertFalse(m["runnable"])
        self.assertTrue(m["not_an_estimate"])
        self.assertIsNone(m["final_portugal_cog_share"])
        self.assertFalse(m["sources"]["provisional_crosswalk"]["verified_against_BLS"])
        self.assertFalse(m["sources"]["official_crosswalk"]["parsed_and_verified"])
        self.assertEqual(m["sources"]["provisional_crosswalk"]["source_blob_sha"],
                         self.mirror["sources"]["mirror"]["sha_git_blob"])
        blocks = m["breakdown"]
        self.assertEqual(len(blocks), 43)
        self.assertEqual(len({b["code"] for b in blocks}), 43)
        self.assertEqual({x["code"] for x in blocks if x["thousands"] is None},
                         {"OC63"})
        self.assertEqual(m["class_weights_thousand"], {
            "all_mapped_C": 1892.8, "all_mapped_N": 855.7,
            "mixed_or_ambiguous": 2363.6,
        })
        for category, number in m["class_weights_thousand"].items():
            recomputed = sum(x["thousands"] for x in blocks
                             if x["provisional_mirror_determination"] == category
                             and x["thousands"] is not None)
            self.assertAlmostEqual(number, recomputed, places=6)
        self.assertAlmostEqual(
            sum(m["provisional_code_class_shares_of_civilian"].values()),
            1, delta=0.001,
        )
        self.assertEqual(m["foremost_ambiguous_submajors"][0]["code"], "OC52")
        self.assertEqual(m["foremost_ambiguous_submajors"][0]["thousands"], 374.3)

    def test_pt_model_remains_disabled_with_no_calibrated_assignments(self):
        audit = self.audit
        self.assertEqual(audit["status"], "audit_only_not_calibrated")
        self.assertFalse(audit["runnable"])
        self.assertEqual(
            len(audit["parameter_inventory"]["Fixed"]) +
            len(audit["parameter_inventory"]["Scenario"]), 37
        )
        for segment in audit["parameter_inventory"].values():
            for p in segment:
                self.assertIsNone(p["portugal_model_value"])
        cog = next(p for p in audit["parameter_inventory"]["Fixed"]
                   if p["name"] == "cog_share")
        self.assertEqual(cog["calibration_status"], "needs_crosswalk")


if __name__ == "__main__":
    unittest.main()
