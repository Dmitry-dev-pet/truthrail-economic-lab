#!/usr/bin/env python3
"""Owner-attested, source-repository-scoped cleanup of chat transfer artifacts.

This is not a cross-repository garbage collector. A trusted owner must first
record the *consumer's* verified SHA-256 and functional acceptance in an Issue.
GitHub itself can verify artifact/run identity and the uploaded ZIP digest,
but cannot independently attest execution in an ephemeral ChatGPT container.
"""
from __future__ import annotations

from datetime import datetime, timezone, timedelta
import json
import os
import re
from urllib.error import HTTPError
from urllib.request import Request, urlopen

REPO = "Dmitry-dev-pet/truthrail-economic-lab"
OWNER = "Dmitry-dev-pet"
TITLE = "[artifact] handoff-consumed"
SHA = re.compile(r"[0-9a-f]{64}\Z")
CHECKSUM = re.compile(r"sha256:[0-9a-f]{64}\Z")
FREECAD_BINARY_SHA256 = "f6dc6ba676e5ac96a565ebc8d657232f94c6158e85b4352141bd1a46f6b43434"
MAX_ARTIFACT_SIZE = 2 * 1024**3
# Deliberately only the existing single-consumer experiments, not research
# snapshots, CI-to-CI handoffs or Pages deployment inputs.
POLICIES = {
    "chat-blender-4.5.14-linux-x64": (
        "Chat Blender portable transfer", "chat-blender-portable.yml",
        "experiment/chat-blender-portable-20261017", "blender-headless"
    ),
    "chat-freecad-1.1.4-linux-x64": (
        "Chat FreeCAD portable transfer", "chat-freecad-portable.yml",
        "experiment/chat-freecad-portable-20261018", "freecad-headless"
    ),
    "chat-freecad-1.1.4-part-00": (
        "Chat FreeCAD portable transfer (chunked)", "chat-freecad-portable.yml",
        "experiment/chat-freecad-portable-20261018", "freecad-headless"
    ),
    "chat-freecad-1.1.4-part-01": (
        "Chat FreeCAD portable transfer (chunked)", "chat-freecad-portable.yml",
        "experiment/chat-freecad-portable-20261018", "freecad-headless"
    ),
}


def strict_keys(obj: object, expected: set[str], name: str) -> dict:
    if not isinstance(obj, dict) or set(obj) != expected:
        raise ValueError(f"{name}: missing, additional or malformed fields")
    return obj


def parse_claim(raw: str) -> dict:
    if not isinstance(raw, str) or len(raw) > 4096:
        raise ValueError("Owner issue body must be a bounded JSON string")
    claim = strict_keys(json.loads(raw), {
        "producer_run_id", "artifact_id", "artifact_name", "artifact_digest",
        "verified_payload_sha256", "verified_binary_sha256", "consumer_receipt",
    }, "claim")
    for key in ("producer_run_id", "artifact_id"):
        if type(claim[key]) is not int or claim[key] <= 0:
            raise ValueError(f"{key}: expected positive integer")
    name = claim["artifact_name"]
    if not isinstance(name, str) or name not in POLICIES:
        raise ValueError("Artifact is outside the reviewed single-consumer allowlist")
    for key in ("verified_payload_sha256", "verified_binary_sha256"):
        if not isinstance(claim[key], str) or not SHA.fullmatch(claim[key]):
            raise ValueError(f"{key}: expected lowercase SHA-256")
    if not isinstance(claim["artifact_digest"], str) or not CHECKSUM.fullmatch(claim["artifact_digest"]):
        raise ValueError("artifact_digest: expected GitHub sha256:<hex> digest")
    receipt = strict_keys(claim["consumer_receipt"], {
        "consumer_id", "sha256_checked", "functional_test", "functional_test_passed",
        "destination_accepted", "all_consumers_acknowledged", "test_receipt", "verified_at",
    }, "consumer_receipt")
    if receipt["consumer_id"] != "chatgpt-ephemeral":
        raise ValueError("Only the declared ChatGPT handoff consumer may acknowledge")
    for key in ("sha256_checked", "functional_test_passed", "destination_accepted",
                "all_consumers_acknowledged"):
        if receipt[key] is not True:
            raise ValueError(f"Consumer did not verify: {key}")
    if receipt["functional_test"] != POLICIES[name][3]:
        raise ValueError("Functional test is not the declared consumer test")
    evidence = receipt["test_receipt"]
    if not isinstance(evidence, str) or not 8 <= len(evidence) <= 300 or "\n" in evidence:
        raise ValueError("Concrete bounded test receipt is required")
    timestamp = receipt["verified_at"]
    if not isinstance(timestamp, str):
        raise ValueError("Consumer verification time is required")
    try:
        dt = datetime.fromisoformat(timestamp.replace("Z", "+00:00"))
    except ValueError as exc:
        raise ValueError("Invalid consumer verification timestamp") from exc
    if dt.tzinfo is None or not datetime(2026, 10, 17, tzinfo=timezone.utc) <= dt <= datetime.now(timezone.utc) + timedelta(minutes=5):
        raise ValueError("Untrusted consumer verification timestamp")
    if name.startswith("chat-freecad-") and claim["verified_binary_sha256"] != FREECAD_BINARY_SHA256:
        raise ValueError("Reassembled FreeCAD binary does not match pinned upstream SHA-256")
    if name == "chat-blender-4.5.14-linux-x64" and claim["verified_payload_sha256"] != claim["verified_binary_sha256"]:
        raise ValueError("Blender binary archive hash differs from verified payload")
    return claim


def verify_provenance(claim: dict, artifact: dict, run: dict) -> None:
    name = claim["artifact_name"]
    run_name, workflow_file, branch, _ = POLICIES[name]
    metadata_run = artifact.get("workflow_run") or {}
    if (artifact.get("id") != claim["artifact_id"]
            or artifact.get("name") != name
            or artifact.get("digest") != claim["artifact_digest"]
            or artifact.get("expired") is not False
            or metadata_run.get("id") != claim["producer_run_id"]):
        raise ValueError("GitHub artifact ID, name, digest or producer run mismatch")
    size = artifact.get("size_in_bytes")
    if type(size) is not int or not 0 < size <= MAX_ARTIFACT_SIZE:
        raise ValueError("Artifact has invalid or excessive size")
    if (run.get("id") != claim["producer_run_id"]
            or run.get("name") != run_name
            or run.get("path") != ".github/workflows/" + workflow_file
            or run.get("head_branch") != branch
            or run.get("status") != "completed"
            or run.get("conclusion") != "success"
            or run.get("event") not in {"push", "workflow_dispatch"}
            or (run.get("actor") or {}).get("login") != OWNER
            or (run.get("repository") or {}).get("full_name") != REPO):
        raise ValueError("Producer is not the reviewed successful owner workflow")
    if metadata_run.get("head_sha") != run.get("head_sha"):
        raise ValueError("Artifact source commit does not match producer run")
    try:
        created = datetime.fromisoformat(artifact["created_at"].replace("Z", "+00:00"))
        verified = datetime.fromisoformat(claim["consumer_receipt"]["verified_at"].replace("Z", "+00:00"))
    except (ValueError, TypeError, KeyError) as exc:
        raise ValueError("Cannot verify handoff chronology") from exc
    if verified < created:
        raise ValueError("Consumer cannot verify an artifact before it exists")


def github_request(method: str, path: str, token: str, body: dict | None = None):
    if not token:
        raise ValueError("Missing GitHub token")
    if not path.startswith("/"):
        raise ValueError("Invalid GitHub API path")
    data = json.dumps(body).encode("utf-8") if body is not None else None
    req = Request("https://api.github.com/repos/" + REPO + path,
                  data=data, method=method, headers={
                      "Authorization": "Bearer " + token,
                      "Accept": "application/vnd.github+json",
                      "X-GitHub-Api-Version": "2022-11-28",
                      "User-Agent": "truthrail-scoped-chat-artifact-cleanup",
                      "Content-Type": "application/json",
                  })
    with urlopen(req, timeout=30) as res:
        if method == "DELETE":
            if res.status != 204:
                raise RuntimeError("GitHub did not return 204 for artifact deletion")
            return 204
        return json.load(res)


def validate_owner_event(env: dict, event: dict) -> tuple[int, str]:
    expected = {
        "GITHUB_REPOSITORY": REPO,
        "GITHUB_ACTOR": OWNER,
        "GITHUB_EVENT_NAME": "issues",
        "GITHUB_REF": "refs/heads/main",
    }
    for key, value in expected.items():
        if env.get(key) != value:
            raise ValueError(f"Untrusted cleanup event: {key}")
    issue = event.get("issue") or {}
    if (event.get("action") != "opened" or issue.get("title") != TITLE
            or (issue.get("user") or {}).get("login") != OWNER
            or issue.get("state") != "open"):
        raise ValueError("Cleanup requires a freshly opened owner Issue")
    number = issue.get("number")
    if type(number) is not int or number <= 0:
        raise ValueError("Missing valid owner Issue number")
    return number, issue.get("body")


def verify_live_issue(number: int, body: str, token: str, request=github_request) -> None:
    issue = request("GET", f"/issues/{number}", token)
    if (issue.get("number") != number or issue.get("body") != body
            or issue.get("title") != TITLE or issue.get("state") != "open"
            or (issue.get("user") or {}).get("login") != OWNER):
        raise ValueError("Owner cleanup Issue was edited or invalidated")


def read_provenance(claim: dict, token: str, request=github_request) -> None:
    artifact = request("GET", f"/actions/artifacts/{claim['artifact_id']}", token)
    run = request("GET", f"/actions/runs/{claim['producer_run_id']}", token)
    verify_provenance(claim, artifact, run)


def delete_verified_artifact(claim: dict, number: int, body: str, token: str,
                             request=github_request) -> dict:
    # The owner issue and GitHub artifact/run metadata are revalidated
    # immediately before the single allowed destructive operation.
    verify_live_issue(number, body, token, request)
    read_provenance(claim, token, request)
    status = request("DELETE", f"/actions/artifacts/{claim['artifact_id']}", token)
    if status != 204:
        raise RuntimeError("Artifact deletion was not acknowledged")
    try:
        request("GET", f"/actions/artifacts/{claim['artifact_id']}", token)
    except HTTPError as exc:
        if exc.code != 404:
            raise
    else:
        raise RuntimeError("Artifact remains available after DELETE")
    return {
        "producer_repo": REPO,
        "producer_run_id": claim["producer_run_id"],
        "artifact_id": claim["artifact_id"],
        "artifact_name": claim["artifact_name"],
        "artifact_digest": claim["artifact_digest"],
        "verification_status": "owner-attested-consumer-accepted",
        "delete_http_status": 204,
        "lookup_after_delete": 404,
        "deleted_at": datetime.now(timezone.utc).isoformat(),
    }


def main() -> None:
    with open(os.environ["GITHUB_EVENT_PATH"], encoding="utf-8") as fp:
        event = json.load(fp)
    number, raw = validate_owner_event(os.environ, event)
    claim = parse_claim(raw)
    token = os.environ.get("GH_TOKEN", "")
    receipt = delete_verified_artifact(claim, number, raw, token)
    print("VERIFIED_ARTIFACT_DELETION " + json.dumps(receipt, sort_keys=True), flush=True)
    summary = os.getenv("GITHUB_STEP_SUMMARY")
    if summary:
        with open(summary, "a", encoding="utf-8") as out:
            out.write("## Verified chat transfer artifact deleted\n\n")
            out.write(f"- Producer run: {receipt['producer_run_id']}\n")
            out.write(f"- Artifact ID: {receipt['artifact_id']}\n")
            out.write(f"- GitHub ZIP digest: {receipt['artifact_digest']}\n")
            out.write("- Owner attested consumer SHA check + functional acceptance\n")
            out.write("- Deletion: HTTP 204; lookup: HTTP 404\n")
    # Reporting is deliberately after deletion, never counted as acceptance.
    message = (
        "Verified consumer acknowledgement and deleted the exact transient chat handoff.\n\n"
        f"- Producer run: {receipt['producer_run_id']}\n"
        f"- Artifact ID: {receipt['artifact_id']}\n"
        f"- Artifact: {receipt['artifact_name']}\n"
        f"- ZIP digest: {receipt['artifact_digest']}\n"
        "- Verification: owner-attested SHA-256 check, functional test and consumer acceptance\n"
        "- Deletion: HTTP 204, confirmed by HTTP 404\n"
        "- No cache, Release or unrelated CI artifact was modified."
    )
    github_request("POST", f"/issues/{number}/comments", token, {"body": message})
    github_request("PATCH", f"/issues/{number}", token, {"state": "closed"})


if __name__ == "__main__":
    main()
