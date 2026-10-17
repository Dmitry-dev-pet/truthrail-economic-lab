# Offline ChatGPT → GitHub changes

The existing `verify.yml` run provides a checksummed source snapshot that can
be downloaded into a temporary ChatGPT Python environment. Verify `SHA256SUMS`
and keep the unpacked `project/` unchanged as a baseline. Copy it to a separate
working directory before editing; retain the `project.sha` from that snapshot.

`ops/offline_changes.py` emits a **bounded, explicit, UTF-8-only** JSON change
manifest with the base commit, exact paths, SHA-256 hashes and proposed text.
It does not contact GitHub, run generated code or publish anything.

Example for a prepared snapshot and one intentionally edited file:

```sh
python work/ops/offline_changes.py \
  --baseline project --working work --base-commit "$(cat project.sha)" \
  --file lab/api.py > changes.json
```

Alfred reviews the manifest, checks that `main` still matches `base_commit`,
then uses the already-connected GitHub API to create a **separate branch and PR**.
Never write directly to `main` or auto-merge. If `main` advanced, rebase or
rebuild against a new snapshot instead of silently applying stale changes.

This pilot supports 1–20 explicitly named added/modified regular text files,
up to 256 KB total, no deletes, symlinks, binary files or `.env` paths.
It does not scan for all secrets; review every manifest before publishing to a
public repo. It uses no new MCP, VPS, credentials, CI workflow or Mac runner.
