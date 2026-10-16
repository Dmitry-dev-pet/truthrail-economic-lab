"""Offline static contract of the fixed, credential-free Mac action."""
from pathlib import Path
import ast
import unittest

ROOT = Path(__file__).resolve().parents[1]

class MacActionMetadataTests(unittest.TestCase):
    def test_source_pin_is_literal(self):
        text = (ROOT / "ops/mac/economic_lab_verify/verify.py").read_text(encoding="utf-8")
        tree = ast.parse(text)
        constants = {
            target.id: node.value.value
            for node in tree.body if isinstance(node, ast.Assign)
            and isinstance(node.value, ast.Constant)
            for target in node.targets if isinstance(target, ast.Name)
        }
        self.assertEqual(constants["UPSTREAM_TAG"], "v1.0")
        self.assertEqual(constants["UPSTREAM_SHA"], "d4703b6ae0d19dca08fbde11a25c218fa4c7b7a6")
        for forbidden in ("docker compose", "docker run", "ssh -", "sudo ", "GITHUB_TOKEN", "GH_TOKEN"):
            self.assertNotIn(forbidden, text)
    def test_action_has_no_dynamic_inputs(self):
        action = (ROOT / "ops/mac/economic_lab_verify/action.yml").read_text()
        preflight = (ROOT / "ops/mac/action.yml").read_text()
        self.assertNotIn("inputs:", action)
        self.assertNotIn("inputs:", preflight)
        self.assertIn("outputs:", action)
        self.assertIn("ready:", preflight)
        self.assertIn("UPSTREAM_SHA", preflight)
        self.assertIn("economic-lab-verify", (ROOT / "ops/mac/economic_lab_verify/verify.py").read_text())

if __name__ == "__main__":
    unittest.main()
