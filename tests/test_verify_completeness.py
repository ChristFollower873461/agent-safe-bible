from __future__ import annotations

import hashlib
import json
import shutil
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path

from support import ROOT

from asb.books import CANON_IDS


class VerifyCompletenessTests(unittest.TestCase):
    """Execute the real CLI against synthetic corpora, never the shipped text."""

    def setUp(self) -> None:
        temporary = tempfile.TemporaryDirectory(prefix="asb-verify-completeness-")
        self.addCleanup(temporary.cleanup)
        self.root = Path(temporary.name)
        (self.root / "asb").mkdir()
        (self.root / "data").mkdir()
        # Only modules required by `verify`; no ingest/network or MCP entry point.
        for name in (
            "__init__.py", "__main__.py", "allowlist.py", "books.py", "corpus.py",
            "jsonutil.py", "lookup.py", "passage.py", "refs.py",
        ):
            shutil.copyfile(ROOT / "asb" / name, self.root / "asb" / name)
        policy = (ROOT / "data" / "allowlist.json").read_bytes()
        (self.root / "data" / "allowlist.json").write_bytes(policy)
        self.translations = sorted(
            row["id"] for row in json.loads(policy)["translations"] if row["status"] == "allowed"
        )
        self.manifests = {}
        for translation in self.translations:
            directory = self.root / "data" / "corpus" / translation
            directory.mkdir(parents=True)
            files = []
            for book_id in CANON_IDS:
                # Hash-check fixtures are explicitly not Scripture or book-schema fixtures.
                content = json.dumps({"synthetic_hash_fixture": book_id}).encode("utf-8")
                relative = f"{book_id}.json"
                (directory / relative).write_bytes(content)
                files.append({"path": relative, "sha256": hashlib.sha256(content).hexdigest()})
            self.manifests[translation] = {"books": len(CANON_IDS), "files": files}
            self.write_manifest(translation)
        self.translation = self.translations[-1]

    def write_manifest(self, translation: str) -> None:
        path = self.root / "data" / "corpus" / translation / "manifest.json"
        path.write_text(json.dumps(self.manifests[translation]), encoding="utf-8")

    def verify(self) -> subprocess.CompletedProcess[str]:
        return subprocess.run(
            [sys.executable, "-m", "asb", "verify"],
            cwd=self.root,
            env={"PYTHONDONTWRITEBYTECODE": "1", "PYTHONNOUSERSITE": "1"},
            capture_output=True,
            text=True,
            timeout=10,
            check=False,
        )

    def assert_invalid_manifest(self, translation: str) -> None:
        self.write_manifest(translation)
        process = self.verify()
        self.assertEqual(process.returncode, 2, process.stderr)
        self.assertEqual(process.stdout, "")
        self.assertIn(f"{translation}: manifest must declare {len(CANON_IDS)} books and list each canonical book exactly once", process.stderr)
        self.assertNotIn("Traceback", process.stderr)

    def test_complete_canonical_manifests_succeed(self) -> None:
        process = self.verify()
        self.assertEqual(process.returncode, 0, process.stderr)
        self.assertEqual(process.stdout, "ok corpus hashes\n")
        self.assertEqual(process.stderr, "")

    def test_complete_reordered_manifests_remain_valid(self) -> None:
        for translation in self.translations:
            self.manifests[translation]["files"].reverse()
            self.write_manifest(translation)
        process = self.verify()
        self.assertEqual(process.returncode, 0, process.stderr)
        self.assertEqual(process.stdout, "ok corpus hashes\n")
        self.assertEqual(process.stderr, "")

    def test_empty_manifests_fail_for_every_allowed_translation(self) -> None:
        for translation in self.translations:
            directory = self.root / "data" / "corpus" / translation
            for row in self.manifests[translation]["files"]:
                (directory / row["path"]).unlink()
            self.manifests[translation]["files"] = []
            self.write_manifest(translation)
        process = self.verify()
        self.assertEqual(process.returncode, 2, process.stderr)
        self.assertEqual(process.stdout, "")
        for translation in self.translations:
            self.assertIn(f"{translation}: manifest must declare", process.stderr)

    def test_omitted_book_fails_even_when_every_listed_hash_matches(self) -> None:
        row = self.manifests[self.translation]["files"].pop()
        (self.root / "data" / "corpus" / self.translation / row["path"]).unlink()
        self.assert_invalid_manifest(self.translation)

    def test_duplicate_replacing_a_book_fails_despite_correct_count(self) -> None:
        files = self.manifests[self.translation]["files"]
        files[-1] = dict(files[0])
        self.assert_invalid_manifest(self.translation)

    def test_extra_duplicate_fails_despite_all_canonical_paths_being_present(self) -> None:
        files = self.manifests[self.translation]["files"]
        files.append(dict(files[0]))
        self.assert_invalid_manifest(self.translation)

    def test_wrong_declared_book_count_fails(self) -> None:
        self.manifests[self.translation]["books"] -= 1
        self.assert_invalid_manifest(self.translation)

    def test_unexpected_book_path_fails_despite_correct_count_and_hashes(self) -> None:
        files = self.manifests[self.translation]["files"]
        directory = self.root / "data" / "corpus" / self.translation
        (directory / files[-1]["path"]).rename(directory / "EXTRA.json")
        files[-1]["path"] = "EXTRA.json"
        self.assert_invalid_manifest(self.translation)

    def test_non_object_manifest_row_fails_without_traceback(self) -> None:
        self.manifests[self.translation]["files"][0] = "GEN.json"
        self.write_manifest(self.translation)
        process = self.verify()
        self.assertEqual(process.returncode, 2, process.stderr)
        self.assertEqual(process.stdout, "")
        self.assertIn(f"{self.translation}: ", process.stderr)
        self.assertNotIn("Traceback", process.stderr)

    def test_non_string_manifest_path_fails_without_traceback(self) -> None:
        self.manifests[self.translation]["files"][0]["path"] = []
        self.write_manifest(self.translation)
        process = self.verify()
        self.assertEqual(process.returncode, 2, process.stderr)
        self.assertEqual(process.stdout, "")
        self.assertIn(f"{self.translation}: ", process.stderr)
        self.assertNotIn("Traceback", process.stderr)

    def test_listed_missing_file_still_fails(self) -> None:
        (self.root / "data" / "corpus" / self.translation / "GEN.json").unlink()
        process = self.verify()
        self.assertEqual(process.returncode, 2, process.stderr)
        self.assertEqual(process.stdout, "")
        self.assertIn(f"hash mismatch {self.translation}/GEN.json", process.stderr)

    def test_changed_file_hash_still_fails(self) -> None:
        (self.root / "data" / "corpus" / self.translation / "GEN.json").write_text("altered synthetic fixture", encoding="utf-8")
        process = self.verify()
        self.assertEqual(process.returncode, 2, process.stderr)
        self.assertEqual(process.stdout, "")
        self.assertIn(f"hash mismatch {self.translation}/GEN.json", process.stderr)

    def test_listed_missing_file_fails_even_when_expected_hash_is_null(self) -> None:
        (self.root / "data" / "corpus" / self.translation / "GEN.json").unlink()
        self.manifests[self.translation]["files"][0]["sha256"] = None
        self.write_manifest(self.translation)
        process = self.verify()
        self.assertEqual(process.returncode, 2, process.stderr)
        self.assertEqual(process.stdout, "")
        self.assertIn(f"hash mismatch {self.translation}/GEN.json", process.stderr)


if __name__ == "__main__":
    unittest.main()
