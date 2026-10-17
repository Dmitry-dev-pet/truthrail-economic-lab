"""Classification-only source audit for SOC2010 vs ISCO08; never a PT model.

The mapping is from a third-party CSV linked to the official BLS XLS.
Its many-to-many row counts are *not* employment counts or weights.
"""
from __future__ import annotations

import json
from pathlib import Path
import unittest


ROOT = Path(__file__).resolve().parents[1] / "country_profiles" / "portugal" / "2024"


class SOCToISCOAuditTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.mapping = json.loads(
            (ROOT / "soc2010_isco08_crosswalk_audit.json").read_text(encoding="utf-8")
        )
        cls.country = json.loads(
            (ROOT / "calibration_audit.json").read_text(encoding="utf-8")
        )
        cls.occupations = json.loads(
            (ROOT / "isco_occupation_snapshot.json").read_text(encoding="utf-8")
        )

    def test_source_version_and_required_quality_warnings(self):
        m = self.mapping
        self.assertEqual(m["country_code"], "PT")
        self.assertEqual(m["reference_year"], 2024)
        self.assertEqual(m["target_partition"]["model"], "fhoces/opa-ai-macro-econ-scenarios")
        self.assertEqual(m["target_partition"]["commit"], self.country["upstream"]["commit"])
        self.assertFalse(m["runnable"])
        self.assertEqual(m["status"], "CLASSIFICATION_ONLY_NOT_EMPLOYMENT_ESTIMATE")
        self.assertIn("BINARY_NOT_PARSED", m["sources"]["official"]["verification"])
        self.assertIn("UNVERIFIED", m["sources"]["mirror"]["verification"])
        self.assertIsNone(m["portugal_2024_weight_data"]["all_employed_two_digit_counts"])
        self.assertEqual(m["extraction"]["csv_relationship_rows"], 1125)
        self.assertEqual(m["extraction"]["parse_failures"], [])
        self.assertEqual(m["extraction"]["distinct_ISCO_codes"], 438)
        self.assertEqual(m["extraction"]["distinct_four_digit_ISCO_codes"], 436)
        self.assertEqual(len(m["extraction"]["non_four_digit_ISCO_rows"]), 2)
        self.assertEqual(
            [v["isco"] for v in m["extraction"]["non_four_digit_ISCO_rows"]],
            ["211", "315"],
        )

    def test_submajors_are_complete_and_no_employment_weights_assumed(self):
        rows = self.mapping["submajor_mapping"]
        self.assertEqual(len(rows), 43)
        self.assertEqual(len({r["isco08_submajor"] for r in rows}), 43)
        n = {"all_mapped_C": 0, "all_mapped_N": 0, "mixed_or_ambiguous": 0}
        for r in rows:
            self.assertRegex(r["isco08_submajor"], r"^\d{2}$")
            self.assertIn(r["determination"], n)
            n[r["determination"]] += 1
            self.assertEqual(
                r["mapped_isco_unit_codes"],
                r["units_only_C"] + r["units_only_N"] + r["units_C_and_N"],
            )
            self.assertGreater(r["soc_links_unweighted"], 0)
        self.assertEqual(n, {
            "all_mapped_C": 13,
            "all_mapped_N": 13,
            "mixed_or_ambiguous": 17,
        })
        target = {r["isco08_submajor"]: r for r in rows}
        for code in ("31", "32", "33", "34", "52", "53", "54"):
            self.assertEqual(target[code]["determination"], "mixed_or_ambiguous")
        for code in ("11", "21", "35", "41", "43"):
            self.assertEqual(target[code]["determination"], "all_mapped_C")
        for code in ("61", "81", "91"):
            self.assertEqual(target[code]["determination"], "all_mapped_N")

    def test_country_model_stays_blocked_and_distinct_population_universes(self):
        self.assertFalse(self.country["runnable"])
        self.assertEqual(self.country["status"], "audit_only_not_calibrated")
        cog = next(x for x in self.country["parameter_inventory"]["Fixed"]
                   if x["name"] == "cog_share")
        self.assertIsNone(cog["portugal_model_value"])
        self.assertEqual(cog["calibration_status"], "needs_crosswalk")
        self.assertEqual(self.occupations["source"]["dataset"], "lfsa_egais")
        self.assertEqual(
            self.occupations["source"]["age"], "Y_GE15"
        )
        qp = self.mapping["portugal_2024_weight_data"]["alternative"]
        self.assertIn("Employer-reported", qp["coverage"])
        self.assertIn("FILE_NOT_RETRIEVED", qp["status"])


if __name__ == "__main__":
    unittest.main()
