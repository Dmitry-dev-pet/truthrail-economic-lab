"""Checks that Portugal's exploratory evidence never impersonates a calibrated model.

Executed with the exact pinned independent model on PYTHONPATH in normal CI.
No country simulations, network calls, provider tokens or installed services.
"""
from __future__ import annotations

from dataclasses import fields
import json
import math
from pathlib import Path
import unittest

from aiscen.params import Fixed, Scenario


PATH = (
    Path(__file__).resolve().parents[1]
    / "country_profiles" / "portugal" / "2024" / "calibration_audit.json"
)
STATUSES = {
    "national_statistic_candidate", "needs_crosswalk", "needs_estimation",
    "structural_review", "model_convention", "scenario_hypothesis",
}


class PortugalCalibrationAuditTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.audit = json.loads(PATH.read_text(encoding="utf-8"))

    def test_precisely_matches_all_pinned_original_model_dataclass_fields(self):
        # Every primitive source-model field must be accounted for. Derived
        # @property values must not be introduced as independent inputs.
        blocks = self.audit["parameter_inventory"]
        self.assertEqual(set(blocks), {"Fixed", "Scenario"})
        for name, target in (("Fixed", Fixed), ("Scenario", Scenario)):
            entries = blocks[name]
            self.assertEqual(
                {item["name"] for item in entries},
                {field.name for field in fields(target)},
            )
            self.assertEqual(len(entries), len(fields(target)))
            for item in entries:
                source_value = getattr(target, item["name"])
                reference = item["us_reference"]
                if reference in ("True", "False"):
                    self.assertIs(source_value, reference == "True")
                elif reference == "1.0 / 12.0":
                    self.assertAlmostEqual(source_value, 1.0 / 12.0)
                else:
                    self.assertAlmostEqual(float(reference), float(source_value))

    def test_audit_is_not_runnable_and_has_no_portuguese_model_assignments(self):
        a = self.audit
        self.assertEqual(a["country_code"], "PT")
        self.assertEqual(a["base_year"], 2024)
        self.assertEqual(a["status"], "audit_only_not_calibrated")
        self.assertIs(a["runnable"], False)
        self.assertEqual(
            a["upstream"]["commit"],
            "d4703b6ae0d19dca08fbde11a25c218fa4c7b7a6",
        )
        entries = [*a["parameter_inventory"]["Fixed"],
                   *a["parameter_inventory"]["Scenario"]]
        self.assertEqual(len(entries), 37)
        self.assertEqual(len({(x["name"], x["calibration_status"]) for x in entries}), 37)
        for entry in entries:
            self.assertEqual(
                set(entry),
                {"name", "us_reference", "calibration_status",
                 "candidate_sources", "mapping_note", "portugal_model_value"},
            )
            self.assertIsNone(entry["portugal_model_value"])
            self.assertIn(entry["calibration_status"], STATUSES)
            self.assertTrue(entry["mapping_note"])
            self.assertTrue(entry["candidate_sources"])
            for key in entry["candidate_sources"]:
                self.assertIn(key, a["sources"])
        self.assertEqual(len(a["calibration_gates"]), 7)

    def test_observations_are_source_grounded_and_never_model_inputs(self):
        a = self.audit
        o = {entry["id"]: entry for entry in a["verified_context_observations"]}
        self.assertEqual(set(o), {
            "PT_UNEMP_2024", "PT_EMPLOYED_2024",
            "PT_UNEMPLOYED_2024", "PT_UNEMP_2025",
            "PT_ENTERPRISE_AI_2025",
        })
        self.assertEqual(o["PT_UNEMP_2024"]["value"], 0.064)
        self.assertEqual(o["PT_EMPLOYED_2024"]["value"], 5_112_300)
        self.assertEqual(o["PT_UNEMPLOYED_2024"]["value"], 351_100)
        self.assertEqual(o["PT_UNEMP_2025"]["value"], 0.060)
        self.assertEqual(o["PT_ENTERPRISE_AI_2025"]["value"], 0.115)
        self.assertEqual(o["PT_UNEMP_2024"]["candidate_for"], "Fixed.U_bar")
        for item in o.values():
            self.assertIs(item["safe_to_assign_to_model"], False)
            self.assertIn(item["source_key"], a["sources"])
            self.assertIn(item["year"], (2024, 2025))
            self.assertTrue(math.isfinite(item["value"]))
        self.assertEqual(o["PT_ENTERPRISE_AI_2025"]["candidate_for"], None)

    def test_vital_non_equivalences_are_explicitly_blocked(self):
        entries = {item["name"]: item for block in self.audit["parameter_inventory"].values()
                   for item in block}
        self.assertEqual(entries["cog_share"]["calibration_status"], "needs_crosswalk")
        self.assertEqual(entries["eps"]["calibration_status"], "structural_review")
        self.assertEqual(entries["U_bar"]["calibration_status"], "national_statistic_candidate")
        self.assertEqual(entries["mu_bar"]["calibration_status"], "needs_estimation")
        self.assertEqual(entries["fill_bar"]["calibration_status"], "needs_estimation")
        for name in ("m_anchor", "d_anchor", "m_2030", "d_2030", "psi", "rho"):
            self.assertEqual(entries[name]["calibration_status"], "scenario_hypothesis")


if __name__ == "__main__":
    unittest.main()
