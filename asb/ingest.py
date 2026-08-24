"""Ingest HelloAO simplified translations into the hashed local corpus."""

from __future__ import annotations

import sys
import urllib.request
from pathlib import Path
from typing import Any

from . import ROOT
from .allowlist import allowlist, allowed_ids
from .books import CANON_IDS, canon_name
from .jsonutil import dump, sha256_file

API_ROOT = "https://bible.helloao.org/api"
CACHE = ROOT / ".cache" / "helloao"
USER_AGENT = "agent-safe-bible/0.1 (+https://github.com/ChristFollower873461/agent-safe-bible)"


def strip_leading_pilcrow(text: str) -> str:
    cleaned = text.replace("\u00b6", "", 1) if text.startswith("\u00b6") else text
    if cleaned != text:
        return cleaned.lstrip(" \t")
    return text


def _download(url: str, dest: Path) -> Path:
    dest.parent.mkdir(parents=True, exist_ok=True)
    if dest.is_file() and dest.stat().st_size > 0:
        return dest
    tmp = dest.with_suffix(dest.suffix + ".part")
    req = urllib.request.Request(url, headers={"User-Agent": USER_AGENT})
    with urllib.request.urlopen(req, timeout=300) as response, tmp.open("wb") as out:
        while True:
            chunk = response.read(1024 * 256)
            if not chunk:
                break
            out.write(chunk)
    tmp.replace(dest)
    return dest


def _extract_book(raw_book: dict[str, Any], translation: str) -> dict[str, Any]:
    book_id = raw_book["id"]
    chapters = []
    for raw_chapter in raw_book["chapters"]:
        chapter = raw_chapter["chapter"]
        number = int(chapter["number"])
        verses = []
        seen: set[int] = set()
        for item in chapter.get("content") or []:
            if item.get("type") != "verse":
                continue
            verse_no = int(item["number"])
            if verse_no in seen:
                raise ValueError(f"duplicate {book_id} {number}:{verse_no}")
            seen.add(verse_no)
            text = strip_leading_pilcrow(str(item.get("text") or ""))
            if not text.strip():
                # Some editions keep a verse number for a reading they omit.
                # Do not invent wording; skip so lookup fails closed.
                print(f"skip empty {translation} {book_id} {number}:{verse_no}", file=sys.stderr)
                continue
            verses.append({"verse": verse_no, "text": text})
        if not verses:
            raise ValueError(f"no verses in {book_id} {number}")
        chapters.append({"chapter": number, "verses": verses})
    return {
        "schema": "agent-safe-bible.book.v1",
        "translation": translation,
        "id": book_id,
        "name": canon_name(book_id),
        "chapters": chapters,
    }


def ingest_translation(translation: str, *, force: bool = False) -> dict[str, Any]:
    data = allowlist()
    row = next(item for item in data["translations"] if item["id"] == translation)
    source = row["ingest"]
    helloao_id = source["helloao_id"]
    url = source["complete_url"]
    cache_path = CACHE / f"{helloao_id}.complete.simple.json"
    if force and cache_path.is_file():
        cache_path.unlink()
    print(f"downloading {url}", file=sys.stderr)
    _download(url, cache_path)
    import json

    complete = json.loads(cache_path.read_text(encoding="utf-8"))
    by_id = {book["id"]: book for book in complete["books"]}
    missing = [book_id for book_id in CANON_IDS if book_id not in by_id]
    extra = [book_id for book_id in by_id if book_id not in CANON_IDS]
    if missing:
        raise SystemExit(f"{translation}: missing books {missing}")
    if extra:
        raise SystemExit(f"{translation}: extra non-canon books {extra}")

    out_dir = ROOT / "data" / "corpus" / translation
    out_dir.mkdir(parents=True, exist_ok=True)
    files = []
    verse_count = 0
    for book_id in CANON_IDS:
        book = _extract_book(by_id[book_id], translation)
        verse_count += sum(len(ch["verses"]) for ch in book["chapters"])
        path = out_dir / f"{book_id}.json"
        dump(book, path)
        files.append(
            {
                "path": f"{book_id}.json",
                "sha256": sha256_file(path),
                "verses": sum(len(ch["verses"]) for ch in book["chapters"]),
                "chapters": len(book["chapters"]),
            }
        )
        print(f"wrote {translation}/{book_id}.json", file=sys.stderr)

    manifest = {
        "schema": "agent-safe-bible.manifest.v1",
        "translation": translation,
        "canon": "protestant-66",
        "books": len(CANON_IDS),
        "verses": verse_count,
        "normalization": ["strip-leading-pilcrow"],
        "source": {
            "name": "HelloAO Free Use Bible API",
            "helloao_id": helloao_id,
            "url": url,
            "license_url": row.get("source_url"),
            "cache_file": str(cache_path.relative_to(ROOT)),
        },
        "files": files,
    }
    dump(manifest, out_dir / "manifest.json")
    print(f"{translation}: {verse_count} verses in {len(files)} books", file=sys.stderr)
    return manifest


def ingest(translations: list[str] | None = None, *, force: bool = False) -> None:
    wanted = translations or sorted(allowed_ids())
    for translation in wanted:
        if translation not in allowed_ids():
            raise SystemExit(f"{translation} is not allowed")
        ingest_translation(translation, force=force)
