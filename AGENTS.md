# Agent contract

This repository is Scripture infrastructure, not a chat persona. You may help humans look up, cite, and study public-domain Bible text. You may not become a substitute Bible.

## Prime directive

If you need Bible text, look it up in this corpus. If you cannot look it up, do not quote it.

## Required moves

- Read `data/allowlist.json` before choosing a translation.
- Default to `BSB` unless the human names another **allowed** translation.
- Return or cite the `passage.v1` object: `ref`, `usfm`, `translation`, `text`, `license`, `kind`.
- Keep interpretation in ordinary prose, after the quote, never inside `text`.
- On a miss: say the reference was not found, or the translation is refused. Do not guess the verse.
- Prefer the local lookup once it exists. Until then, only quote the checked-in fixtures you have actually read.

## Forbidden moves

- Do not quote from model memory, even for John 3:16.
- Do not paraphrase a verse and call it Scripture, BSB, WEB, KJV, or "the Bible."
- Do not silently correct, modernize, or "improve" wording.
- Do not fetch NIV, ESV, NASB, NLT, CSB, NKJV, or any translation marked `refused`.
- Do not invent books, chapters, or verses (no "Hezekiah 4:12", no extra Beatitude).
- Do not claim God told you something through weights or a system prompt.
- Do not present this project as a complete 66-book corpus until the ingest issues are closed.

## Fail closed

Unknown reference, missing file, hash mismatch, or refused translation → no quotation. Uncertainty is a valid answer.

## Tone

Be plain and exact. "I could not verify that verse in this corpus" is better than a confident misquote.
