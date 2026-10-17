"""Guardrails on the owner-only public experiment workflow."""
from pathlib import Path
import unittest


WORKFLOW = Path(__file__).resolve().parents[1] / ".github/workflows/owner-experiment.yml"


class OwnerExperimentWorkflowGuard(unittest.TestCase):
    def test_exact_owner_command_and_no_mac_execution(self):
        text = WORKFLOW.read_text(encoding="utf-8")
        self.assertIn("issues:\n    types: [opened]", text)
        self.assertIn("github.event.issue.user.login == github.repository_owner", text)
        self.assertIn("github.event.issue.title == '[econ] experiment'", text)
        self.assertIn("runs-on: ubuntu-latest", text)
        self.assertIn("timeout-minutes: 10", text)
        self.assertIn("persist-credentials: false", text)
        self.assertNotIn("self-hosted", text)
        self.assertNotIn("workflow_dispatch", text)
        self.assertNotIn("secrets.", text)
        self.assertIn("python -m lab.issue_runner", text)

    def test_model_computation_does_not_receive_report_token(self):
        text = WORKFLOW.read_text(encoding="utf-8")
        execute, report = text.split("      - name: Publish bounded issue result", 1)
        self.assertNotIn("GH_TOKEN:", execute)
        self.assertIn("ECON_ISSUE_JSON: ${{ github.event.issue.body }}", execute)
        self.assertIn("GH_TOKEN: ${{ github.token }}", report)
        self.assertIn("gh issue comment", report)


if __name__ == "__main__":
    unittest.main()
