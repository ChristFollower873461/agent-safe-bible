# Agent contract

This repository is Scripture infrastructure, not a chat persona. You may help humans look up, cite, and study public-domain Bible text. You may not become a substitute Bible.

## Prime directive

If you need Bible text, look it up with `python3 -m asb get`. If lookup fails, do not quote it.

## Required moves

- Read `data/allowlist.json` before choosing a translation.
- Default to `BSB` unless the human names another **allowed** translation (`WEB` or `KJV`).
- Run `python3 -m asb get "REF" --tr ID` from this repository. Do not quote from model memory, even for John 3:16.
- Return or cite the `passage.v1` object: `ref`, `usfm`, `translation`, `text`, `license`, `kind`.
- Keep interpretation in ordinary prose, after the quote, never inside `text`.
- On a miss: say the reference was not found, or the translation is refused. Do not guess the verse.
- MCP users should call `get_passage` on `python3 -m asb mcp`. That tool is the same local lookup.

## Forbidden moves

- Do not quote from model memory.
- Do not paraphrase a verse and call it Scripture, BSB, WEB, KJV, or "the Bible."
- Do not silently correct, modernize, or "improve" wording.
- Do not fetch NIV, ESV, NASB, NLT, CSB, NKJV, or any translation marked `refused`.
- Do not invent books, chapters, or verses (no "Hezekiah 4:12", no extra Beatitude).
- Do not claim God told you something through weights or a system prompt.
- Do not call HelloAO, bible-api.com, or any other remote Bible API from an agent using this project. Runtime is the hashed corpus in `data/corpus/`.

## Fail closed

Unknown reference, missing file, hash mismatch, refused translation, or omitted verse in an edition → no quotation. Uncertainty is a valid answer.

## Commands

```sh
python3 -m asb get "John 3:16"
python3 -m asb get "Psalm 23:1" --tr KJV
python3 -m asb get "Romans 8:28" --tr WEB
python3 -m asb verify
```

## Tone

Be plain and exact. "I could not verify that verse in this corpus" is better than a confident misquote.
