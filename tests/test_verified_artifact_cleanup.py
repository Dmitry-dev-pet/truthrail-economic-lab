"""Fail-closed contract tests for owner-attested artifact cleanup."""
from __future__ import annotations

import copy
from datetime import datetime, timedelta, timezone
import json
import unittest
from urllib.error import HTTPError

from ops.verified_artifact_cleanup import (
    OWNER, REPO, TITLE, FREECAD_BINARY_SHA256, POLICIES,
    parse_claim, verify_provenance, validate_owner_event,
    delete_verified_artifact,
)

NOW = datetime.now(timezone.utc)
DIGEST = "sha256:" + "a" * 64


def claim(name="chat-blender-4.5.14-linux-x64"):
    full = FREECAD_BINARY_SHA256 if name.startswith("chat-freecad-") else "b" * 64
    return {
        "producer_run_id": 345,
        "artifact_id": 678,
        "artifact_name": name,
        "artifact_digest": DIGEST,
        "verified_payload_sha256": "c" * 64 if name.startswith("chat-freecad-") else full,
        "verified_binary_sha256": full,
        "consumer_receipt": {
            "consumer_id": "chatgpt-ephemeral",
            "sha256_checked": True,
            "functional_test": POLICIES[name][3],
            "functional_test_passed": True,
            "destination_accepted": True,
            "all_consumers_acknowledged": True,
            "test_receipt": "Verified actual headless binary smoke test output",
            "verified_at": NOW.isoformat(),
        },
    }


def provenance(c):
    name = c["artifact_name"]
    workflow_name, workflow_file, branch, _ = POLICIES[name]
    return (
        {"id": c["artifact_id"], "name": name, "digest": DIGEST,
         "expired": False, "size_in_bytes": 400_000_000,
         "created_at": (NOW - timedelta(minutes=2)).isoformat(),
         "workflow_run": {"id": 345, "head_sha": "9" * 40}},
        {"id": 345, "name": workflow_name,
         "path": ".github/workflows/" + workflow_file,
         "head_branch": branch, "status": "completed", "conclusion": "success",
         "event": "push", "actor": {"login": OWNER},
         "repository": {"full_name": REPO}, "head_sha": "9" * 40},
    )


class TestReceipt(unittest.TestCase):
    def test_accepts_owner_blender_and_chunked_freecad(self):
        for name in POLICIES:
            with self.subTest(name=name):
                c = claim(name)
                self.assertEqual(parse_claim(json.dumps(c)), c)
                verify_provenance(c, *provenance(c))

    def test_requires_real_ack_fields(self):
        for key in ("sha256_checked", "functional_test_passed", "destination_accepted",
                    "all_consumers_acknowledged"):
            c = claim()
            c["consumer_receipt"][key] = False
            with self.subTest(key=key), self.assertRaises(ValueError):
                parse_claim(json.dumps(c))

    def test_rejects_unknown_consumers_and_artifacts(self):
        c = claim()
        c["consumer_receipt"]["consumer_id"] = "unlisted-other-session"
        with self.assertRaises(ValueError):
            parse_claim(json.dumps(c))
        c = claim()
        c["artifact_name"] = "economic-source-issue-33"
        with self.assertRaises(ValueError):
            parse_claim(json.dumps(c))

    def test_rejects_extra_fields_bools_as_ids_bad_digests(self):
        c = claim()
        c["extra"] = "unsafe"
        with self.assertRaises(ValueError):
            parse_claim(json.dumps(c))
        c = claim()
        c["artifact_id"] = True
        with self.assertRaises(ValueError):
            parse_claim(json.dumps(c))
        c = claim()
        c["artifact_digest"] = "sha256:" + "Z" * 64
        with self.assertRaises(ValueError):
            parse_claim(json.dumps(c))

    def test_no_premature_or_future_receipt(self):
        c = claim()
        c["consumer_receipt"]["verified_at"] = "2026-10-01T12:00:00Z"
        with self.assertRaises(ValueError):
            parse_claim(json.dumps(c))
        c = claim()
        c["consumer_receipt"]["verified_at"] = (NOW + timedelta(days=1)).isoformat()
        with self.assertRaises(ValueError):
            parse_claim(json.dumps(c))

    def test_freecad_full_source_must_be_verified(self):
        c = claim("chat-freecad-1.1.4-part-00")
        c["verified_binary_sha256"] = "f" * 64
        with self.assertRaises(ValueError):
            parse_claim(json.dumps(c))

    def test_wrong_run_name_branch_digest_sha_fail_closed(self):
        c = claim()
        a, r = provenance(c)
        for target, key, val in (
            ("artifact", "digest", "sha256:" + "d" * 64),
            ("artifact", "name", "other"),
            ("run", "head_branch", "main"),
            ("run", "name", "Wrong workflow"),
            ("run", "conclusion", "failure"),
            ("run", "path", ".github/workflows/unknown.yml"),
            ("run", "head_sha", "f" * 40),
        ):
            aa, rr = copy.deepcopy((a, r))
            (aa if target == "artifact" else rr)[key] = val
            with self.subTest(target=target, key=key), self.assertRaises(ValueError):
                verify_provenance(c, aa, rr)

    def test_bad_producer_run_relation_and_bad_chronology(self):
        c = claim()
        a, r = provenance(c)
        a["workflow_run"]["id"] = 5
        with self.assertRaises(ValueError):
            verify_provenance(c, a, r)
        a, r = provenance(c)
        a["created_at"] = (NOW + timedelta(minutes=2)).isoformat()
        with self.assertRaises(ValueError):
            verify_provenance(c, a, r)

    def test_owner_only_event_and_exact_title(self):
        env = {"GITHUB_REPOSITORY": REPO, "GITHUB_ACTOR": OWNER,
               "GITHUB_EVENT_NAME": "issues", "GITHUB_REF": "refs/heads/main"}
        event = {"action": "opened", "issue": {"title": TITLE, "number": 70,
                  "user": {"login": OWNER}, "state": "open", "body": json.dumps(claim())}}
        self.assertEqual(validate_owner_event(env, event)[0], 70)
        for mutation in (lambda e, v: e.update(GITHUB_ACTOR="intruder"),
                         lambda e, v: v["issue"].update(title="[artifact] please-delete"),
                         lambda e, v: v["issue"]["user"].update(login="intruder"),
                         lambda e, v: v.update(action="edited")):
            ee, vv = copy.deepcopy((env, event))
            mutation(ee, vv)
            with self.assertRaises(ValueError):
                validate_owner_event(ee, vv)

    def test_successful_delete_only_after_two_live_reads_and_404(self):
        c = claim()
        a, r = provenance(c)
        raw = json.dumps(c)
        events = []
        def request(method, path, token, body=None):
            events.append((method, path))
            self.assertEqual(token, "test-token")
            if method == "GET" and path == "/issues/70":
                return {"number": 70, "body": raw, "title": TITLE,
                        "state": "open", "user": {"login": OWNER}}
            if method == "GET" and path == "/actions/runs/345":
                return r
            if method == "GET" and path == "/actions/artifacts/678":
                if ("DELETE", "/actions/artifacts/678") in events:
                    raise HTTPError(path, 404, "Not found", {}, None)
                return a
            if method == "DELETE" and path == "/actions/artifacts/678":
                return 204
            self.fail("Unrecognized GitHub request")
        receipt = delete_verified_artifact(c, 70, raw, "test-token", request)
        self.assertEqual(receipt["delete_http_status"], 204)
        self.assertEqual([action[0] for action in events],
                         ["GET", "GET", "GET", "DELETE", "GET"])

    def test_no_delete_if_issue_edited(self):
        c = claim()
        events = []
        def request(method, path, token, body=None):
            events.append(method)
            return {"number": 70, "body": "modified", "title": TITLE,
                    "state": "open", "user": {"login": OWNER}}
        with self.assertRaises(ValueError):
            delete_verified_artifact(c, 70, json.dumps(c), "test-token", request)
        self.assertNotIn("DELETE", events)

    def test_no_delete_if_run_changed(self):
        c = claim()
        a, r = provenance(c)
        r["conclusion"] = "failure"
        events = []
        def request(method, path, token, body=None):
            events.append(method)
            if path.startswith("/issues/"):
                return {"number": 70, "body": "x", "title": TITLE,
                        "state": "open", "user": {"login": OWNER}}
            if path.startswith("/actions/artifacts/"):
                return a
            return r
        with self.assertRaises(ValueError):
            delete_verified_artifact(c, 70, "x", "test-token", request)
        self.assertNotIn("DELETE", events)


if __name__ == "__main__":
    unittest.main()
