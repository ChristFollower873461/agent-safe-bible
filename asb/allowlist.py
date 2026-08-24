"""Translation allowlist and refuse-list."""

from __future__ import annotations

from pathlib import Path
from typing import Any

from . import ROOT
from .jsonutil import load

ALLOWLIST_PATH = ROOT / "data" / "allowlist.json"
REQUIRED_REFUSED = frozenset({"NIV", "ESV", "NASB", "NLT", "CSB", "NKJV"})


def allowlist(path: Path = ALLOWLIST_PATH) -> dict[str, Any]:
    return load(path)


def default_translation(data: dict[str, Any] | None = None) -> str:
    data = data or allowlist()
    return str(data["default_translation"])


def allowed_ids(data: dict[str, Any] | None = None) -> set[str]:
    data = data or allowlist()
    return {row["id"] for row in data["translations"] if row["status"] == "allowed"}


def refused_ids(data: dict[str, Any] | None = None) -> set[str]:
    data = data or allowlist()
    return {row["id"] for row in data["refused"]}


def translation_row(translation_id: str, data: dict[str, Any] | None = None) -> dict[str, Any] | None:
    data = data or allowlist()
    needle = translation_id.upper()
    for row in data["translations"]:
        if row["id"].upper() == needle:
            return row
    return None


def classify(translation_id: str, data: dict[str, Any] | None = None) -> str:
    """Return 'allowed', 'refused', or 'unknown'."""
    data = data or allowlist()
    needle = translation_id.upper()
    if any(row["id"].upper() == needle for row in data["refused"]):
        return "refused"
    if any(row["id"].upper() == needle and row["status"] == "allowed" for row in data["translations"]):
        return "allowed"
    return "unknown"
