"""Tests for the networkless ChatGPT-to-GitHub change manifest."""
import hashlib
from pathlib import Path
import tempfile
import unittest

from ops.offline_changes import build_manifest


class OfflineChangesTests(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        self.addCleanup(self.temp.cleanup)
        root = Path(self.temp.name)
        self.original, self.edited = root / "original", root / "edited"
        self.original.mkdir()
        self.edited.mkdir()
        self.sha = "a" * 40

    def write(self, directory, name, text):
        path = directory / name
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(text, encoding="utf-8")
        return path

    def export(self, *paths):
        return build_manifest(self.original, self.edited, self.sha, list(paths))

    def test_modified_and_added_files_with_content_hashes(self):
        self.write(self.original, "module.py", "a = 1\n")
        self.write(self.edited, "module.py", "a = 2\n")
        self.write(self.edited, "new.txt", "new\n")
        result = self.export("new.txt", "module.py")
        self.assertEqual(result["base_commit"], self.sha)
        self.assertEqual([x["status"] for x in result["files"]], ["modified", "added"])
        self.assertEqual(result["files"][0]["sha256"],
                         hashlib.sha256(b"a = 2\n").hexdigest())
        self.assertEqual(result["files"][1]["content"], "new\n")

    def test_unchanged_files_cannot_make_empty_manifest(self):
        self.write(self.original, "a.py", "same")
        self.write(self.edited, "a.py", "same")
        with self.assertRaisesRegex(ValueError, "No actual changes"):
            self.export("a.py")

    def test_rejects_traversal_and_private_paths(self):
        for path in ("../outside", "/absolute", "dir/../secret", ".env", "dir/.env.local", ".git/config"):
            with self.subTest(path=path), self.assertRaises(ValueError):
                self.export(path)

    def test_rejects_symlinks(self):
        outside = Path(self.temp.name) / "outside.txt"
        outside.write_text("private", encoding="utf-8")
        (self.edited / "link.txt").symlink_to(outside)
        with self.assertRaisesRegex(ValueError, "Symlink"):
            self.export("link.txt")

    def test_rejects_binary_and_large_files(self):
        (self.edited / "binary.dat").write_bytes(b"a\0b")
        with self.assertRaisesRegex(ValueError, "UTF-8"):
            self.export("binary.dat")
        (self.edited / "huge.txt").write_text("x" * 256001, encoding="utf-8")
        with self.assertRaisesRegex(ValueError, "UTF-8"):
            self.export("huge.txt")

    def test_rejects_duplicate_paths_and_invalid_sha(self):
        self.write(self.edited, "a.txt", "updated")
        with self.assertRaisesRegex(ValueError, "distinct"):
            self.export("a.txt", "a.txt")
        with self.assertRaisesRegex(ValueError, "SHA-1"):
            build_manifest(self.original, self.edited, "not-a-sha", ["a.txt"])


if __name__ == "__main__":
    unittest.main()
