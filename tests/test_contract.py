#!/usr/bin/env python3
"""Contract tests for allowlist, fixtures, and passage.v1 shape."""

from __future__ import annotations

import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
REQUIRED = {
    "schema",
    "ref",
    "usfm",
    "translation",
    "text",
    "license",
    "kind",
}
GOLDEN = {
    "BSB": "For God so loved the world that He gave His one and only Son, that everyone who believes in Him shall not perish but have eternal life.",
    "WEB": "For God so loved the world, that he gave his one and only Son, that whoever believes in him should not perish, but have eternal life.",
    "KJV": "For God so loved the world, that he gave his only begotten Son, that whosoever believeth in him should not perish, but have everlasting life.",
}
REFUSED = {"NIV", "ESV", "NASB", "NLT", "CSB", "NKJV"}


def load(path: Path) -> object:
    return json.loads(path.read_text(encoding="utf-8"))


def main() -> int:
    errors: list[str] = []
    allowlist = load(ROOT / "data" / "allowlist.json")
    allowed = {row["id"] for row in allowlist["translations"] if row["status"] == "allowed"}
    refused = {row["id"] for row in allowlist["refused"]}

    if allowlist["default_translation"] != "BSB":
        errors.append("default_translation must be BSB")
    if allowed != {"BSB", "WEB", "KJV"}:
        errors.append(f"unexpected allowlist: {sorted(allowed)}")
    if not REFUSED.issubset(refused):
        errors.append(f"missing refused ids: {sorted(REFUSED - refused)}")
    if allowed & refused:
        errors.append(f"ids both allowed and refused: {sorted(allowed & refused)}")

    fixtures = sorted((ROOT / "data" / "fixtures").glob("*.json"))
    if len(fixtures) < 3:
        errors.append("expected at least three fixtures")

    for path in fixtures:
        row = load(path)
        missing = REQUIRED - row.keys()
        extra_kind = row.get("kind") != "quotation"
        if missing:
            errors.append(f"{path.name}: missing {sorted(missing)}")
        if row.get("schema") != "agent-safe-bible.passage.v1":
            errors.append(f"{path.name}: bad schema")
        if row.get("license") != "public-domain":
            errors.append(f"{path.name}: license must be public-domain")
        if extra_kind:
            errors.append(f"{path.name}: kind must be quotation")
        if row.get("translation") not in allowed:
            errors.append(f"{path.name}: translation {row.get('translation')!r} not allowed")
        if row.get("translation") in refused:
            errors.append(f"{path.name}: refused translation")
        expected = GOLDEN.get(row.get("translation"))
        if expected and row.get("text") != expected:
            errors.append(f"{path.name}: text does not match golden {row.get('translation')}")

    if errors:
        print("FAIL")
        for item in errors:
            print(f"- {item}")
        return 1
    print(f"ok {len(fixtures)} fixtures, {len(allowed)} allowed translations")
    return 0


if __name__ == "__main__":
    sys.exit(main())
