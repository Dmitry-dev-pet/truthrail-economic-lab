# Offline ChatGPT → GitHub changes

Source code arrives **on demand**, not on every PR. From the repository owner's
GitHub account, open an Issue titled exactly `[source] snapshot`. The read-only
`.github/workflows/source-snapshot.yml` workflow publishes a three-day ZIP
artifact for the main-branch commit, including the pinned `aiscen` package.
Reuse an unexpired artifact for the same commit when available.

Download the artifact ZIP into a temporary ChatGPT Linux environment, extract
it, and run `sha256sum -c SHA256SUMS`. Keep the resulting `workspace/project/`
unchanged as a baseline and copy it to a separate working directory before
editing; retain `project.sha` from the artifact.

`ops/offline_changes.py` emits a **bounded, explicit, UTF-8-only** JSON change
manifest with the source commit, paths, original and proposed SHA-256 hashes,
and proposed text. `baseline_sha256` is `null` for added files. The hashes are
of the exact file bytes, so a reviewer can detect conflicts before updating.
The exporter itself cannot contact GitHub or publish anything.

Example after extracting the ZIP inside `snapshot/` and its two tarballs:

```sh
cd snapshot/workspace
cp -a project work
# Make an intentional edit in work/, then export it:
PYTHONPATH=work python work/ops/offline_changes.py \
  --baseline project --working work \
  --base-commit "$(cat ../project.sha)" \
  --file lab/api.py > ../changes.json
```

Alfred must compare the manifest's `base_commit` to GitHub `main`, and compare
the current GitHub file bytes to `baseline_sha256` before applying a modified
file. GitHub's **blob SHA** (required by its update-file API) differs from this
SHA-256 content digest; obtain the blob SHA from the current GitHub file.
For added files, verify the path does not already exist. Then submit reviewed
changes through an isolated branch and PR, never directly to `main`.
If the base commit changed, rebuild against a fresh source snapshot or review
and reconcile changes; do not silently overwrite newer work.

This pilot supports 1–20 explicitly selected added/modified regular UTF-8 text
files, up to 256 KB in proposed bytes. It rejects deletes, symlinks, binary
files and `.env` paths. It does **not** detect all possible secrets, so review
changes before publishing to a public repository. No new MCP, VPS, Mac runner,
model-provider key or extra CI workflow is required for returning changes.
