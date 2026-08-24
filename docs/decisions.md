# Decisions

Keep this file short. Each entry is a choice we will not silently reverse.

## 2026-08-23 — Default English is BSB

Berean Standard Bible is modern English and public domain as of 30 April 2023. WEB is also unrestricted and remains allowed. KJV is allowed as the classic public-domain English text. Agents default to BSB unless asked otherwise.

## 2026-08-23 — v0 canon is 66 Protestant books

Deuterocanon can be a later labeled extra. Mixing canons in one undifferentiated dump would make agents lie about what "the Bible" contains.

## 2026-08-23 — Offline corpus, not a live API

v0 lookup must work with no network. APIs change, rate-limit, and mix licenses. A pinned hashable tree is the source of truth. Wrappers around HelloAO or `faith` are optional later and must still honor the allowlist.

## 2026-08-23 — Refuse restricted translations

We will not quote NIV, ESV, NASB, NLT, CSB, NKJV, or other limited-license editions "with attribution." Agents that need those texts must leave this project. Safety here includes copyright hygiene, not only hallucination control.

## 2026-08-23 — Quotation and interpretation are different kinds

`kind` on `passage.v1` is only `quotation`. Commentary lives in prose or a future `note.v1` object. This stops a model from stuffing a paraphrase into `text`. Additional properties on the quotation object are forbidden.

## 2026-08-23 — WEB is HelloAO ENGWEBP

The ingested WEB text is the Protestant World English Bible (`ENGWEBP`), not an older "one and only Son" dump. Fixtures must match the hashed corpus.

## 2026-08-23 — Strip leading pilcrows only

KJV digital editions prefix some verses with `¶`. That mark is not Scripture wording. Ingest strips a single leading pilcrow and the spaces that follow it. Internal punctuation, capitalization, and poetry newlines stay.

## 2026-08-23 — Empty source verses are omitted

If the source returns a verse number with empty text, ingest skips it. Lookup of that reference fails closed. We do not restore omitted readings from memory or from another translation.

## 2026-08-23 — Hash the written file, not a normalized string

SHA-256 in each manifest is over the UTF-8 book JSON as written (LF newlines). `python3 -m asb verify` and every `get` of a book re-check that digest.
