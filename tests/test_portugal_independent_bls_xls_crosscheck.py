"""Guard independently crosschecked SOC2010–ISCO08 source mapping provenance.

An archived GitHub-hosted BLS-branded binary workbook is compared to another
repository's CSV transcription, NOT to bytes from the official BLS server.
All counts here describe *occupational code mappings* rather than workers.
"""
from __future__ import annotations

import json
from pathlib import Path
import unittest

ROOT = Path(__file__).resolve().parents[1] / "country_profiles" / "portugal" / "2024"


def read(name):
    return json.loads((ROOT / name).read_text(encoding="utf-8"))


class CrosswalkIndependentBinaryEvidence(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.check = read("independent_xls_vs_csv_verification_2024.json")
        cls.classification = read("soc2010_isco08_crosswalk_audit.json")
        cls.weighted = read("soc_isco_employment_weighted_review_2024.json")
        cls.country = read("calibration_audit.json")

    def test_exact_agreement_but_not_direct_official_source_equality(self):
        d = self.check
        s = d["sources"]
        stats = d["validation"]
        self.assertFalse(d["runnable"])
        self.assertEqual(d["status"], "INDEPENDENT_XLS_COPY_CROSSCHECK_NOT_DIRECT_BLS_HOST_VERIFICATION")
        self.assertFalse(d["original_host_reference"]["direct_byte_comparison_performed"])
        self.assertEqual(s["workbook_copy"]["bytes"], 433152)
        self.assertEqual(s["workbook_copy"]["blob_sha"],
                         "6d8f2d6777ed2462376bcb91bf5492a3350520da")
        self.assertEqual(s["csv_copy"]["blob_sha"],
                         "f6a72a3519f9cd53104b2b89dedc562d8b31bcb9")
        self.assertEqual(s["workbook_copy"]["relationship_rows"], 1125)
        self.assertEqual(s["csv_copy"]["relationship_rows"], 1125)
        self.assertEqual(s["workbook_copy"]["sheets"], [
            "ISCO-08 to 2010 SOC", "2010 SOC to ISCO-08", "match",
        ])
        self.assertEqual(stats["code_pair_matches"], 1125)
        self.assertEqual(stats["code_pair_mismatches"], 0)
        self.assertEqual(stats["isco_titles_equal"], 1125)
        self.assertEqual(stats["soc_titles_equal"], 1125)
        self.assertEqual(stats["unique_mapping_pairs"], 1125)
        self.assertEqual(stats["distinct_ISCO_codes"], 438)
        self.assertTrue(stats["no_employment_weights_obtained_from_source"])

    def test_parent_level_codes_are_in_both_sources(self):
        short = self.check["validation"]["unusual_3digit_ISCO_codes"]
        self.assertEqual([x["code"] for x in short], ["211", "315"])
        self.assertEqual([x["excel_workbook_row"] for x in short], [80, 380])
        self.assertEqual([x["csv_line"] for x in short], [74, 374])
        self.assertEqual(self.classification["extraction"]["non_four_digit_ISCO_rows"][0]["isco"],
                         "211")
        self.assertTrue(all("both copies" in x["note"] for x in short))

    def test_ambiguous_units_and_weighted_submajors_remain_distinct(self):
        d = self.check
        stats = d["validation"]
        self.assertEqual(stats["code_units_C_only"], 221)
        self.assertEqual(stats["code_units_N_only"], 191)
        self.assertEqual(stats["code_units_both"], 26)
        units = d["ambiguous_four_digit_ISCO_units"]
        self.assertEqual(len(units), 26)
        self.assertEqual(len({x["isco08"] for x in units}), 26)
        for item in units:
            self.assertRegex(item["isco08"], r"^\d{4}$")
            self.assertTrue(item["C_major_groups"])
            self.assertTrue(item["N_major_groups"])
            self.assertGreater(item["C_link_count"], 0)
            self.assertGreater(item["N_link_count"], 0)
        subgroups = d["mixed_submajors_prioritized_by_official_2024_employment"]
        self.assertEqual(len(subgroups), 17)
        self.assertEqual(subgroups[0]["isco2"], "OC52")
        self.assertEqual(subgroups[0]["employment_thousands"], 374.3)
        self.assertEqual(subgroups[0]["mixed_four_digit_codes"], ["5212"])
        self.assertEqual(subgroups[1]["isco2"], "OC33")
        self.assertEqual(subgroups[1]["mixed_four_digit_codes"], ["3344", "3351"])
        grouped = [g for g in subgroups if g["mixed_four_digit_count"] > 0]
        separable = [g for g in subgroups if g["mixed_four_digit_count"] == 0]
        self.assertEqual((len(grouped), len(separable)), (12, 5))
        self.assertAlmostEqual(sum(x["employment_thousands"] for x in grouped), 1676.9)
        self.assertAlmostEqual(sum(x["employment_thousands"] for x in separable), 686.7)
        official = self.weighted["breakdown"]
        self.assertEqual(
            {x["isco2"] for x in subgroups},
            {x["code"] for x in official
             if x["provisional_mirror_determination"] == "mixed_or_ambiguous"},
        )

    def test_portugal_cog_share_and_national_simulation_still_blocked(self):
        self.assertFalse(self.country["runnable"])
        self.assertEqual(self.country["status"], "audit_only_not_calibrated")
        values = [v for group in self.country["parameter_inventory"].values() for v in group]
        self.assertEqual(len(values), 37)
        self.assertTrue(all(v["portugal_model_value"] is None for v in values))
        cog = next(v for v in values if v["name"] == "cog_share")
        self.assertEqual(cog["calibration_status"], "needs_crosswalk")
        self.assertIsNone(self.weighted["final_portugal_cog_share"])
        self.assertFalse(self.weighted["sources"]["official_crosswalk"]["parsed_and_verified"])
        self.assertTrue(
            self.weighted["sources"]["provisional_crosswalk"]["verified_against_independent_BLS_branded_XLS_copy"]
        )
        self.assertFalse(
            self.weighted["sources"]["provisional_crosswalk"]["direct_official_BLS_binary_verified"]
        )


if __name__ == "__main__":
    unittest.main()
