"""Offline checks of public Portugal 2024 statistics, never model calibration.

These snapshots originate from Eurostat's dimension-filtered JSON API. This
test only checks the saved public data, labels and methodological safeguards.
"""
from __future__ import annotations

import json
from pathlib import Path
import unittest


ROOT = Path(__file__).resolve().parents[1] / "country_profiles" / "portugal" / "2024"


def read(name):
    return json.loads((ROOT / name).read_text(encoding="utf-8"))


class Portugal2024SourceSnapshots(unittest.TestCase):
    def test_isco_major_groups_and_reconciliation(self):
        d = read("isco_occupation_snapshot.json")
        a = read("calibration_audit.json")
        self.assertEqual(d["country_code"], "PT")
        self.assertEqual(d["year"], 2024)
        self.assertEqual(d["source"]["dataset"], "lfsa_egais")
        self.assertEqual(d["source"]["age"], "Y_GE15")
        self.assertEqual(d["source"]["unit"], "thousand persons")
        self.assertFalse(d["runnable"])
        counts = d["category_counts"]
        self.assertEqual(counts["TOTAL"]["thousands"], 5112.3)
        self.assertEqual(counts["OC1"]["thousands"], 309.8)
        self.assertEqual(counts["OC2"]["thousands"], 1178.3)
        self.assertEqual(counts["OC3"]["thousands"], 590.8)
        self.assertEqual(counts["OC4"]["thousands"], 478.0)
        self.assertEqual(counts["OC5"]["thousands"], 928.3)
        self.assertEqual(len(counts), 12)
        assert "NRP" in counts
        self.assertAlmostEqual(
            sum(counts[k]["thousands"] for k in counts if k not in ("TOTAL", "NRP")),
            counts["TOTAL"]["thousands"],
            delta=0.15,  # independent 0.1-thousand rounding
        )
        self.assertEqual(
            a["verified_context_observations"][1]["value"],
            5_112_300,
        )
        groups = d["coarse_subsets"]
        self.assertEqual(len(groups), 3)
        self.assertEqual(groups[0]["codes"], ["OC1", "OC2", "OC4"])
        self.assertEqual(groups[1]["codes"], ["OC1", "OC2", "OC3", "OC4"])
        self.assertEqual(groups[2]["codes"], ["OC1", "OC2", "OC3", "OC4", "OC5"])
        for item in groups:
            expected = sum(counts[k]["thousands"] for k in item["codes"])
            self.assertAlmostEqual(item["thousands"], expected, places=5)
            self.assertAlmostEqual(
                item["share_of_total"], expected / counts["TOTAL"]["thousands"], places=6,
            )
            self.assertTrue(item["notes"])
        self.assertLess(groups[0]["share_of_total"], groups[1]["share_of_total"])
        self.assertLess(groups[1]["share_of_total"], groups[2]["share_of_total"])
        self.assertEqual(
            d["us_model_definition"]["soc2010_major_groups"],
            ["11", "13", "15", "17", "19", "21", "23", "25", "27", "29", "41", "43"],
        )
        self.assertEqual(a["status"], "audit_only_not_calibrated")
        self.assertFalse(a["runnable"])
        cog = next(x for x in a["parameter_inventory"]["Fixed"] if x["name"] == "cog_share")
        self.assertEqual(cog["calibration_status"], "needs_crosswalk")
        self.assertIsNone(cog["portugal_model_value"])

    def test_annual_status_flow_matrix_and_not_occupational_switching(self):
        d = read("lfs_annual_status_flows.json")
        self.assertEqual(d["source"]["dataset"], "lfsi_long_a")
        self.assertEqual(d["source"]["period"], "2024")
        self.assertFalse(d["runnable"])
        entries = {item["code"]: item for item in d["matrix"]}
        self.assertEqual(set(entries), {
            "EMP_EMP", "EMP_UNE", "EMP_INAC",
            "UNE_EMP", "UNE_UNE", "UNE_INAC",
            "INAC_EMP", "INAC_UNE", "INAC_INAC",
        })
        for origin in ("EMP", "UNE", "INAC"):
            members = [x for name, x in entries.items() if name.startswith(origin + "_")]
            self.assertEqual(len(members), 3)
            self.assertAlmostEqual(
                sum(x["origin_share_pct"] for x in members), 100.0, delta=0.15,
            )
            origin_total = sum(x["count_thousand"] for x in members)
            for row in members:
                self.assertAlmostEqual(
                    row["count_thousand"] / origin_total * 100,
                    row["origin_share_pct"], delta=0.3,
                )
        self.assertEqual(entries["UNE_EMP"]["count_thousand"], 148)
        self.assertEqual(entries["UNE_EMP"]["origin_share_pct"], 42.2)
        self.assertEqual(entries["EMP_UNE"]["origin_share_pct"], 2.4)
        self.assertEqual(entries["EMP_EMP"]["origin_share_pct"], 94.5)
        self.assertIn("C-to-N occupational move", d["model_mapping"]["unobserved"])
        for field in ("mu_bar", "mu", "q_rel_C", "q_rel_N"):
            self.assertIn(field, d["model_mapping"]["cannot_calibrate_directly"])
        audit = read("calibration_audit.json")
        self.assertFalse(audit["runnable"])
        mu = next(x for x in audit["parameter_inventory"]["Fixed"] if x["name"] == "mu_bar")
        self.assertIsNone(mu["portugal_model_value"])
        self.assertEqual(mu["calibration_status"], "needs_estimation")


if __name__ == "__main__":
    unittest.main()
