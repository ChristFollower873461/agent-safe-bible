"""Fail-closed local lookup."""

from __future__ import annotations

from dataclasses import dataclass
from typing import Any

from .allowlist import classify, default_translation
from .corpus import CorpusError, iter_verses, source_for, verify_book_file
from .passage import make_passage, make_passages
from .refs import ParseError, ParsedRef, parse_ref


@dataclass
class LookupFailure(Exception):
    code: str
    message: str
    details: dict[str, Any]

    def as_dict(self) -> dict[str, Any]:
        payload = {"ok": False, "error": self.code, "message": self.message}
        payload.update(self.details)
        return payload


def get(ref: str, translation: str | None = None) -> dict[str, Any]:
    tr = (translation or default_translation()).strip()
    if not tr:
        raise LookupFailure("missing_translation", "translation is required", {})
    status = classify(tr)
    if status == "refused":
        raise LookupFailure(
            "refused_translation",
            f"{tr} is copyrighted or otherwise restricted; this corpus will not quote it.",
            {"translation": tr.upper()},
        )
    if status != "allowed":
        raise LookupFailure(
            "unknown_translation",
            f"{tr} is not on the allowlist.",
            {"translation": tr},
        )
    tr = tr.upper()
    try:
        parsed = parse_ref(ref)
    except ParseError as exc:
        raise LookupFailure("bad_reference", str(exc), {"ref": ref}) from exc
    try:
        passages = list(_passages(parsed, tr))
    except CorpusError as exc:
        raise LookupFailure("not_found", str(exc), {"ref": ref, "translation": tr}) from exc
    if not passages:
        raise LookupFailure("not_found", f"no verses for {ref}", {"ref": ref, "translation": tr})
    label = parsed.raw.strip() or ref
    return make_passages(translation=tr, ref=label, passages=passages)


def _passages(parsed: ParsedRef, translation: str) -> list[dict[str, Any]]:
    book = verify_book_file(translation, parsed.book_id)
    source = source_for(translation)
    chapter_end = parsed.chapter_end or parsed.chapter
    out: list[dict[str, Any]] = []
    for chapter in range(parsed.chapter, chapter_end + 1):
        numbers = [item["verse"] for item in _chapter(book, chapter)]
        if parsed.whole_chapter or (chapter != parsed.chapter and chapter != chapter_end):
            start, end = None, None
        elif parsed.chapter == chapter_end:
            start, end = parsed.verse, parsed.verse_end
        elif chapter == parsed.chapter:
            start, end = parsed.verse, max(numbers)
        else:
            start, end = min(numbers), parsed.verse_end
        for ch, verse, text in iter_verses(book, chapter, start, end):
            out.append(
                make_passage(
                    translation=translation,
                    book_id=parsed.book_id,
                    chapter=ch,
                    verse=verse,
                    text=text,
                    source=source,
                )
            )
    return out


def _chapter(book: dict[str, Any], chapter: int) -> list[dict[str, Any]]:
    for row in book["chapters"]:
        if row["chapter"] == chapter:
            return list(row["verses"])
    raise CorpusError(f"no chapter {chapter} in {book['id']}")
