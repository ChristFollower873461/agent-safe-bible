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

`kind` on `passage.v1` is only `quotation`. Commentary lives in prose or a future `note.v1` object. This stops a model from stuffing a paraphrase into `text`.
