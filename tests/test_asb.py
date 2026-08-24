from __future__ import annotations

import json
import subprocess
import sys
import unittest
from pathlib import Path

from support import ROOT

from asb.allowlist import REQUIRED_REFUSED, allowed_ids, allowlist, classify, refused_ids
from asb.books import CANON_IDS, lookup_book
from asb.jsonutil import load, sha256_file
from asb.lookup import LookupFailure, get
from asb.mcp import handle
from asb.refs import ParseError, parse_ref
from asb.schema import SchemaError, validate

GOLDEN = {
    ("BSB", "John 3:16"): "For God so loved the world that He gave His one and only Son, that everyone who believes in Him shall not perish but have eternal life.",
    ("WEB", "John 3:16"): "For God so loved the world, that he gave his only born Son, that whoever believes in him should not perish, but have eternal life.",
    ("KJV", "John 3:16"): "For God so loved the world, that he gave his only begotten Son, that whosoever believeth in him should not perish, but have everlasting life.",
    ("BSB", "Genesis 1:1"): "In the beginning God created the heavens and the earth.",
    ("WEB", "Genesis 1:1"): "In the beginning, God created the heavens and the earth.",
    ("KJV", "Genesis 1:1"): "In the beginning God created the heaven and the earth.",
    ("BSB", "Psalm 23:1"): "The LORD is my shepherd;\nI shall not want.",
    ("WEB", "Psalm 23:1"): "The LORD is my shepherd;\nI shall lack nothing.",
    ("KJV", "Psalm 23:1"): "The LORD is my shepherd; I shall not want.",
    ("BSB", "Romans 8:28"): "And we know that God works all things together for the good of those who love Him, who are called according to His purpose.",
    ("WEB", "Romans 8:28"): "We know that all things work together for good for those who love God, for those who are called according to his purpose.",
    ("KJV", "Romans 8:28"): "And we know that all things work together for good to them that love God, to them who are the called according to his purpose.",
}

PASSAGE_SCHEMA = load(ROOT / "schemas" / "passage.v1.schema.json")
BOOK_SCHEMA = load(ROOT / "schemas" / "book.v1.schema.json")


class AllowlistTests(unittest.TestCase):
    def test_frozen_v0_ids(self) -> None:
        data = allowlist()
        self.assertEqual(data["default_translation"], "BSB")
        self.assertEqual(data["canon"], "protestant-66")
        self.assertEqual(allowed_ids(), {"BSB", "WEB", "KJV"})
        self.assertTrue(REQUIRED_REFUSED.issubset(refused_ids()))
        self.assertFalse(allowed_ids() & refused_ids())
        for row in data["translations"]:
            self.assertEqual(row["license"], "public-domain")
            self.assertTrue(row["source_url"])
            self.assertIn("helloao_id", row["ingest"])
            self.assertIn("complete_url", row["ingest"])
            self.assertNotIn(row["id"], REQUIRED_REFUSED)

    def test_classify(self) -> None:
        self.assertEqual(classify("bsb"), "allowed")
        self.assertEqual(classify("NIV"), "refused")
        self.assertEqual(classify("CSB"), "refused")
        self.assertEqual(classify("MSG"), "unknown")


class SchemaTests(unittest.TestCase):
    def test_fixtures_match_passage_v1(self) -> None:
        fixtures = sorted((ROOT / "data" / "fixtures").glob("*.json"))
        self.assertGreaterEqual(len(fixtures), 3)
        for path in fixtures:
            row = load(path)
            validate(row, PASSAGE_SCHEMA)
            self.assertEqual(row["kind"], "quotation")
            self.assertEqual(row["license"], "public-domain")
            self.assertIn(row["translation"], allowed_ids())

    def test_invalid_examples_are_rejected(self) -> None:
        invalid = sorted((ROOT / "tests" / "invalid").glob("*.json"))
        self.assertGreaterEqual(len(invalid), 3)
        for path in invalid:
            with self.subTest(path.name):
                with self.assertRaises(SchemaError):
                    validate(load(path), PASSAGE_SCHEMA)

    def test_commentary_cannot_live_in_kind_or_extra_field(self) -> None:
        with self.assertRaises(SchemaError):
            validate(load(ROOT / "tests" / "invalid" / "kind-interpretation.json"), PASSAGE_SCHEMA)
        with self.assertRaises(SchemaError):
            validate(load(ROOT / "tests" / "invalid" / "extra-commentary-field.json"), PASSAGE_SCHEMA)


class RefTests(unittest.TestCase):
    def test_aliases(self) -> None:
        self.assertEqual(parse_ref("Jn 3:16").book_id, "JHN")
        self.assertEqual(parse_ref("1 John 3:16").book_id, "1JN")
        self.assertEqual(parse_ref("Psalm 23").whole_chapter, True)
        self.assertEqual(parse_ref("John3:16").verse, 16)
        self.assertEqual(parse_ref("John 3:16-18").verse_end, 18)
        self.assertEqual(parse_ref("John 3:16-4:2").chapter_end, 4)
        self.assertEqual(lookup_book("song of solomon"), "SNG")

    def test_unknown_book(self) -> None:
        with self.assertRaises(ParseError):
            parse_ref("Hezekiah 4:12")


class CorpusTests(unittest.TestCase):
    def test_manifests_and_hashes(self) -> None:
        for translation in ("BSB", "WEB", "KJV"):
            manifest = load(ROOT / "data" / "corpus" / translation / "manifest.json")
            self.assertEqual(manifest["books"], 66)
            self.assertEqual(len(manifest["files"]), 66)
            ids = [Path(row["path"]).stem for row in manifest["files"]]
            self.assertEqual(ids, list(CANON_IDS))
            for row in manifest["files"]:
                path = ROOT / "data" / "corpus" / translation / row["path"]
                self.assertEqual(sha256_file(path), row["sha256"])
                book = load(path)
                validate(book, BOOK_SCHEMA)
                self.assertEqual(book["translation"], translation)

    def test_book_schema_has_no_commentary_field(self) -> None:
        book = load(ROOT / "data" / "corpus" / "BSB" / "JHN.json")
        for chapter in book["chapters"]:
            for verse in chapter["verses"]:
                self.assertEqual(set(verse), {"verse", "text"})


class LookupTests(unittest.TestCase):
    def test_golden_verses(self) -> None:
        for (translation, ref), text in GOLDEN.items():
            row = get(ref, translation)
            self.assertEqual(row["kind"], "quotation")
            self.assertEqual(row["text"], text)
            self.assertEqual(row["translation"], translation)
            validate(row, PASSAGE_SCHEMA)

    def test_fixtures_match_lookup(self) -> None:
        for translation, filename in (("BSB", "john-3-16.bsb.json"), ("WEB", "john-3-16.web.json"), ("KJV", "john-3-16.kjv.json")):
            fixture = load(ROOT / "data" / "fixtures" / filename)
            row = get("John 3:16", translation)
            self.assertEqual(row["text"], fixture["text"])

    def test_range(self) -> None:
        row = get("John 3:16-18")
        self.assertEqual(row["schema"], "agent-safe-bible.passages.v1")
        self.assertEqual(len(row["passages"]), 3)
        self.assertEqual(row["passages"][0]["verse"], 16)

    def test_fail_closed_fake_book(self) -> None:
        with self.assertRaises(LookupFailure) as caught:
            get("Hezekiah 4:12")
        self.assertEqual(caught.exception.code, "bad_reference")

    def test_fail_closed_missing_verse(self) -> None:
        with self.assertRaises(LookupFailure) as caught:
            get("Psalm 23:99")
        self.assertEqual(caught.exception.code, "not_found")

    def test_fail_closed_refused(self) -> None:
        for translation in ("NIV", "ESV", "NASB", "NLT", "CSB", "NKJV"):
            with self.assertRaises(LookupFailure) as caught:
                get("John 3:16", translation)
            self.assertEqual(caught.exception.code, "refused_translation")
            self.assertNotIn("For God so loved", json.dumps(caught.exception.as_dict()))

    def test_omitted_web_verse_is_a_miss(self) -> None:
        with self.assertRaises(LookupFailure) as caught:
            get("Luke 17:36", "WEB")
        self.assertEqual(caught.exception.code, "not_found")


class AgentDocTests(unittest.TestCase):
    def test_lockstep_cli_and_refuse_list(self) -> None:
        for rel in ("AGENTS.md", "llms.txt", "skills/scripture-quote/SKILL.md", "README.md"):
            text = (ROOT / rel).read_text(encoding="utf-8")
            self.assertIn("python3 -m asb get", text, rel)
            self.assertIn("NIV", text, rel)
            self.assertIn("BSB", text, rel)


class CliTests(unittest.TestCase):
    def _run(self, *args: str) -> subprocess.CompletedProcess[str]:
        return subprocess.run(
            [sys.executable, "-m", "asb", *args],
            cwd=ROOT,
            capture_output=True,
            text=True,
            check=False,
        )

    def test_get_success(self) -> None:
        proc = self._run("get", "John 3:16", "--tr", "BSB")
        self.assertEqual(proc.returncode, 0, proc.stderr)
        row = json.loads(proc.stdout)
        self.assertEqual(row["text"], GOLDEN[("BSB", "John 3:16")])
        self.assertEqual(proc.stderr, "")

    def test_get_refused_prints_no_verse(self) -> None:
        proc = self._run("get", "John 3:16", "--tr", "NIV")
        self.assertEqual(proc.returncode, 2)
        self.assertEqual(proc.stdout, "")
        err = json.loads(proc.stderr)
        self.assertEqual(err["error"], "refused_translation")
        self.assertNotIn("For God so loved", proc.stderr)

    def test_get_hezekiah(self) -> None:
        proc = self._run("get", "Hezekiah 4:12")
        self.assertEqual(proc.returncode, 2)
        self.assertEqual(proc.stdout, "")

    def test_verify(self) -> None:
        proc = self._run("verify")
        self.assertEqual(proc.returncode, 0, proc.stderr)


class McpTests(unittest.TestCase):
    def test_initialize_and_get(self) -> None:
        init = handle({"jsonrpc": "2.0", "id": 1, "method": "initialize", "params": {}})
        self.assertEqual(init["result"]["serverInfo"]["name"], "agent-safe-bible")
        listed = handle({"jsonrpc": "2.0", "id": 2, "method": "tools/list"})
        names = {tool["name"] for tool in listed["result"]["tools"]}
        self.assertEqual(names, {"get_passage", "list_translations"})
        result = handle(
            {
                "jsonrpc": "2.0",
                "id": 3,
                "method": "tools/call",
                "params": {"name": "get_passage", "arguments": {"ref": "John 3:16", "translation": "KJV"}},
            }
        )
        payload = json.loads(result["result"]["content"][0]["text"])
        self.assertEqual(payload["text"], GOLDEN[("KJV", "John 3:16")])
        self.assertFalse(result["result"]["isError"])

    def test_mcp_refused(self) -> None:
        result = handle(
            {
                "jsonrpc": "2.0",
                "id": 4,
                "method": "tools/call",
                "params": {"name": "get_passage", "arguments": {"ref": "John 3:16", "translation": "ESV"}},
            }
        )
        self.assertTrue(result["result"]["isError"])
        payload = json.loads(result["result"]["content"][0]["text"])
        self.assertEqual(payload["error"], "refused_translation")
        self.assertNotIn("For God so loved", result["result"]["content"][0]["text"])


if __name__ == "__main__":
    unittest.main()
