"""Export explicit UTF-8 changes from an offline source snapshot for GitHub review.

No network, credentials, Git metadata or shell commands are needed. The resulting
JSON is data for the GitHub connector, *not* an instruction to auto-commit it.
"""

import argparse
import hashlib
import json
from pathlib import Path, PurePosixPath
import re

MAX_FILES = 20
MAX_TOTAL_BYTES = 256_000


def _relative_path(name):
    if not isinstance(name, str) or not name or "\\" in name:
        raise ValueError("Expected a nonempty POSIX repository path")
    path = PurePosixPath(name)
    if (path.is_absolute() or str(path) != name or
            any(part in (".", "..") for part in name.split("/")) or
            any(part == ".git" or part == ".env" or part.startswith(".env.")
                for part in path.parts)):
        raise ValueError(f"Unsafe or private repository path: {name}")
    return path


def _read_regular_file(root, relative, required):
    target = root
    for part in relative.parts:
        target = target / part
        if target.is_symlink():
            raise ValueError(f"Symlink not supported: {relative}")
    if not target.exists():
        if required:
            raise ValueError(f"Missing proposed file: {relative}")
        return None
    if not target.is_file():
        raise ValueError(f"Not a regular file: {relative}")
    return target.read_bytes()


def build_manifest(baseline, working, base_commit, paths):
    """Return a small manifest tied to the immutable source-snapshot commit."""
    if not re.fullmatch(r"[a-f0-9]{40}", base_commit):
        raise ValueError("Base commit must be a full 40-character SHA-1")
    original = Path(baseline).resolve(strict=True)
    edited = Path(working).resolve(strict=True)
    if not original.is_dir() or not edited.is_dir() or original == edited:
        raise ValueError("Baseline and working directories must differ")
    if not paths or len(paths) > MAX_FILES or len(paths) != len(set(paths)):
        raise ValueError("Specify 1–20 distinct paths explicitly")

    changes = []
    total = 0
    for name in sorted(paths):
        relative = _relative_path(name)
        after = _read_regular_file(edited, relative, required=True)
        before = _read_regular_file(original, relative, required=False)
        if after == before:
            continue
        total += len(after)
        if total > MAX_TOTAL_BYTES or b"\0" in after:
            raise ValueError("Only small UTF-8 text changes are supported")
        try:
            content = after.decode("utf-8")
        except UnicodeDecodeError as exc:
            raise ValueError(f"Non-UTF-8 file: {name}") from exc
        changes.append({"path": name, "status": "added" if before is None else "modified",
                        "baseline_sha256": (hashlib.sha256(before).hexdigest()
                                            if before is not None else None),
                        "sha256": hashlib.sha256(after).hexdigest(), "content": content})
    if not changes:
        raise ValueError("No actual changes found")
    return {"format": "truthrail-offline-text-v1", "base_commit": base_commit,
            "files": changes}


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--baseline", required=True)
    parser.add_argument("--working", required=True)
    parser.add_argument("--base-commit", required=True)
    parser.add_argument("--file", action="append", required=True, dest="files")
    args = parser.parse_args()
    print(json.dumps(build_manifest(args.baseline, args.working,
                                    args.base_commit, args.files), ensure_ascii=False,
                     indent=2))


if __name__ == "__main__":
    main()
