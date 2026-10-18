# Cleanup of temporary ChatGPT tool archives

This **repository-scoped** adapter implements the owner policy: **no GitHub Actions Artifacts by default; after verified consumption, delete the temporary transfer envelope**. It handles only the reviewed **single-consumer**, one-day Blender 4.5.14 and FreeCAD 1.1.4 chat experiments. It cannot delete arbitrary artifacts, research snapshots, caches, Pages deployment inputs or GitHub Releases.

The producer workflows live on experiment branches. They validate upstream release checksums and set `retention-days: 1`. Expiry is a fallback for incomplete transfers, **not** proof of delivery. Never delete on upload success.

## Consumer verification before deletion

1. Download the exact artifact ID from the expected producer run; compute SHA-256 of the extracted payload against its producer checksum or manifest. The GitHub `sha256:...` ZIP digest is a **separate** object identity.
2. For split FreeCAD, check the individual parts against `SHA256PARTS`, reconstruct the complete AppImage and verify the pinned full SHA-256 from `SHA256SUMS`: `f6dc6ba676e5ac96a565ebc8d657232f94c6158e85b4352141bd1a46f6b43434`. **Neither part may be acknowledged until the complete reconstructed binary passes.**
3. Run an actual headless Blender or FreeCAD smoke test in the consumer environment. Keep a concrete bounded result. Accept the destination and verify that *all* declared consumers (here exactly `chatgpt-ephemeral`) have acknowledged it. HTTP 200 and a successful download are insufficient.
4. **Only after steps 1–3**, an authenticated repository owner may open an Issue with the exact title `[artifact] handoff-consumed` and a JSON body in this shape. Each artifact needs its own Issue; substitute real verified values for the synthetic placeholders.

    {
      "producer_run_id": 123,
      "artifact_id": 456,
      "artifact_name": "chat-blender-4.5.14-linux-x64",
      "artifact_digest": "sha256:aaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaa",
      "verified_payload_sha256": "bbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbb",
      "verified_binary_sha256": "bbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbb",
      "consumer_receipt": {
        "consumer_id": "chatgpt-ephemeral",
        "sha256_checked": true,
        "functional_test": "blender-headless",
        "functional_test_passed": true,
        "destination_accepted": true,
        "all_consumers_acknowledged": true,
        "test_receipt": "Synthetic example, not a real verified run",
        "verified_at": "2026-10-18T03:00:00Z"
      }
    }

For FreeCAD, change `functional_test` to `freecad-headless` and use the verified SHA-256 of the **complete AppImage** for `verified_binary_sha256`, including for each part's deletion. The `verified_payload_sha256` is the verified individual part's digest. For Blender both verified digest fields refer to the same official tar.xz payload.

## Scope and security

The workflow on the default branch accepts **only a freshly opened, still-unchanged owner Issue**. Its job uses its own producer-repository `GITHUB_TOKEN` with `actions: write` and `issues: write`; there is no cross-repository deleter, general PAT or token handoff to the consumer. The script verifies exact artifact ID, name, ZIP digest, run ID, source commit, successful owner-triggered workflow and expected branch. Immediately before deleting the named ID it rechecks the live GitHub Issue and producer metadata. Deletion requires HTTP 204 followed by GET 404. It posts a bounded receipt and closes the Issue only if deletion succeeds. Unverified transfers remain available until the one-day fallback expiry.

**Truth boundary:** GitHub can independently prove producer/artifact metadata and that the owner authorized deletion. GitHub **cannot** inspect files or execution inside an ephemeral ChatGPT runtime. The consumer's SHA-256 and successful functional test are therefore an explicit, authenticated **owner attestation**, not cryptographic proof of local execution. An Issue must never claim verification without an actual local test. Do not post secrets, personal data or local file paths in this public Issue.

Adding this handler does **not** delete existing archives or automatically alter a producer workflow. For an additional tool version, project or multi-consumer transfer, review a separate project-owned contract and tests before extending the allowlist. CI tests cover the rejected and successful metadata paths using a mocked GitHub API. Live deletion should first be exercised on a separately authorized **small synthetic transfer** after genuine consumer verification.
