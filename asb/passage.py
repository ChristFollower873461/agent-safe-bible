"""passage.v1 objects."""

from __future__ import annotations

from typing import Any

from .books import canon_name


def make_passage(
    *,
    translation: str,
    book_id: str,
    chapter: int,
    verse: int,
    text: str,
    source: str,
) -> dict[str, Any]:
    name = canon_name(book_id)
    return {
        "schema": "agent-safe-bible.passage.v1",
        "ref": f"{name} {chapter}:{verse}",
        "usfm": f"{book_id} {chapter}:{verse}",
        "book": name,
        "chapter": chapter,
        "verse": verse,
        "translation": translation,
        "text": text,
        "license": "public-domain",
        "kind": "quotation",
        "source": source,
    }


def make_passages(
    *,
    translation: str,
    ref: str,
    passages: list[dict[str, Any]],
) -> dict[str, Any]:
    if len(passages) == 1:
        return passages[0]
    return {
        "schema": "agent-safe-bible.passages.v1",
        "ref": ref,
        "translation": translation,
        "passages": passages,
    }
