"""Read and verify the hashed local corpus."""

from __future__ import annotations

from pathlib import Path
from typing import Any, Iterator

from . import ROOT
from .books import CANON_IDS
from .jsonutil import load, sha256_file

CORPUS_ROOT = ROOT / "data" / "corpus"


class CorpusError(LookupError):
    """The local corpus cannot satisfy the request."""


def translation_dir(translation: str, root: Path = CORPUS_ROOT) -> Path:
    return root / translation.upper()


def manifest_path(translation: str, root: Path = CORPUS_ROOT) -> Path:
    return translation_dir(translation, root) / "manifest.json"


def book_path(translation: str, book_id: str, root: Path = CORPUS_ROOT) -> Path:
    return translation_dir(translation, root) / f"{book_id}.json"


def load_manifest(translation: str, root: Path = CORPUS_ROOT) -> dict[str, Any]:
    path = manifest_path(translation, root)
    if not path.is_file():
        raise CorpusError(f"no corpus for {translation}")
    return load(path)


def verify_book_file(translation: str, book_id: str, root: Path = CORPUS_ROOT) -> dict[str, Any]:
    manifest = load_manifest(translation, root)
    files = {row["path"]: row["sha256"] for row in manifest["files"]}
    relative = f"{book_id}.json"
    expected = files.get(relative)
    path = book_path(translation, book_id, root)
    if expected is None or not path.is_file():
        raise CorpusError(f"{translation} has no book {book_id}")
    digest = sha256_file(path)
    if digest != expected:
        raise CorpusError(f"hash mismatch for {translation}/{relative}")
    return load(path)


def iter_verses(
    book: dict[str, Any],
    chapter: int,
    verse_start: int | None = None,
    verse_end: int | None = None,
) -> Iterator[tuple[int, int, str]]:
    chapters = {row["chapter"]: row for row in book["chapters"]}
    row = chapters.get(chapter)
    if row is None:
        raise CorpusError(f"no chapter {chapter} in {book['id']}")
    verses = list(row["verses"])
    if verse_start is None:
        for item in verses:
            yield chapter, int(item["verse"]), item["text"]
        return
    wanted = {item["verse"]: item["text"] for item in verses}
    last = verse_end if verse_end is not None else verse_start
    for number in range(verse_start, last + 1):
        if number not in wanted:
            raise CorpusError(f"no {book['id']} {chapter}:{number}")
        yield chapter, number, wanted[number]


def source_for(translation: str, root: Path = CORPUS_ROOT) -> str:
    manifest = load_manifest(translation, root)
    source = manifest.get("source") or {}
    return str(source.get("url") or source.get("name") or "local-corpus")


def has_corpus(translation: str, root: Path = CORPUS_ROOT) -> bool:
    path = manifest_path(translation, root)
    if not path.is_file():
        return False
    manifest = load(path)
    return len(manifest.get("files", [])) == len(CANON_IDS)
