"""Parse human Bible references into USFM book/chapter/verse ranges."""

from __future__ import annotations

import re
from dataclasses import dataclass

from .books import aliases_longest_first, lookup_book

_SPACE = re.compile(r"\s+")
_PUNCT = re.compile(r"[.]")
_LETTER_DIGIT = re.compile(r"([a-z])(\d)")
_DIGIT_LETTER = re.compile(r"(\d)([a-z])")


class ParseError(ValueError):
    """The reference string is not a usable Bible reference."""


@dataclass(frozen=True)
class ParsedRef:
    book_id: str
    chapter: int
    verse: int | None = None
    verse_end: int | None = None
    chapter_end: int | None = None
    raw: str = ""

    @property
    def whole_chapter(self) -> bool:
        return self.verse is None

    @property
    def single_verse(self) -> bool:
        return (
            self.verse is not None
            and self.verse_end == self.verse
            and (self.chapter_end is None or self.chapter_end == self.chapter)
        )


def _normalize(raw: str) -> str:
    text = raw.strip().lower().replace("\u2013", "-").replace("\u2014", "-")
    text = _PUNCT.sub("", text)
    text = _DIGIT_LETTER.sub(r"\1 \2", text)
    text = _LETTER_DIGIT.sub(r"\1 \2", text)
    text = text.replace(":", " : ")
    text = text.replace("-", " - ")
    return _SPACE.sub(" ", text).strip()


def parse_ref(raw: str) -> ParsedRef:
    if not raw or not raw.strip():
        raise ParseError("empty reference")
    text = _normalize(raw)
    book_id = None
    rest = text
    for alias in aliases_longest_first():
        if text == alias or text.startswith(alias + " "):
            book_id = lookup_book(alias)
            rest = text[len(alias) :].strip()
            break
    if book_id is None:
        raise ParseError(f"unknown book in {raw!r}")
    if not rest:
        raise ParseError(f"missing chapter in {raw!r}")
    parts = rest.split(" ")
    try:
        if ":" in parts:
            # chapter : verse [ - verse] or chapter : verse - chapter : verse
            tokens = parts
            if tokens[0] == ":":
                raise ParseError(f"missing chapter in {raw!r}")
            chapter = int(tokens[0])
            if len(tokens) < 3 or tokens[1] != ":":
                raise ParseError(f"expected chapter:verse in {raw!r}")
            verse = int(tokens[2])
            if len(tokens) == 3:
                return ParsedRef(book_id, chapter, verse, verse, chapter, raw)
            if tokens[3] != "-" or len(tokens) < 5:
                raise ParseError(f"bad range in {raw!r}")
            # John 3 : 16 - 18
            if len(tokens) == 5:
                end = int(tokens[4])
                if end < verse:
                    raise ParseError(f"verse range runs backward in {raw!r}")
                return ParsedRef(book_id, chapter, verse, end, chapter, raw)
            # John 3 : 16 - 4 : 2
            if len(tokens) == 7 and tokens[5] == ":":
                chapter_end = int(tokens[4])
                verse_end = int(tokens[6])
                if chapter_end < chapter or (chapter_end == chapter and verse_end < verse):
                    raise ParseError(f"range runs backward in {raw!r}")
                return ParsedRef(book_id, chapter, verse, verse_end, chapter_end, raw)
            raise ParseError(f"bad range in {raw!r}")
        chapter = int(parts[0])
        if len(parts) != 1:
            raise ParseError(f"bad chapter reference in {raw!r}")
        if chapter < 1:
            raise ParseError(f"chapter must be >= 1 in {raw!r}")
        return ParsedRef(book_id, chapter, None, None, chapter, raw)
    except ValueError as exc:
        raise ParseError(f"bad numbers in {raw!r}") from exc
