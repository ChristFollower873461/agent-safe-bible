# Plan

Status: planning, public, v0 not shipped.

## Problem

LLMs are a bad Bible. They invent references, paraphrase verses, mix commentary into quotes, and often emit copyrighted translations they are not licensed to reproduce. Public-domain texts and Bible APIs already exist, but they do not give agents a fail-closed contract: *look this up, quote it verbatim, or refuse*.

## Non-goals

- A study app, chatbot, or sermon generator.
- A replacement for HelloAO, `faith`, TheologAI, or StudyBible MCP.
- Hosting copyrighted translations behind an API key.
- Teaching an agent to "sound biblical" from weights.
- A new English translation.

## Goals for v0

1. Pin an allowlist of unrestricted English translations: BSB (default), WEB, KJV.
2. Publish `passage.v1` so quotation and interpretation cannot share a record.
3. Ingest the 66-book Protestant canon for BSB, with SHA-256 over the canonical JSON.
4. Ship an agent skill and `AGENTS.md` that forbids memory quotes.
5. Ship a local lookup that returns the passage object or an explicit miss.
6. Test golden verses for exact text match, including John 3:16 in all three allowed translations.

## Phases

### Phase 0 — this commit

Charter, allowlist, schema, fixtures, agent skill, related-work notes, open issues.

### Phase 1 — corpus

Ingest BSB from a documented public-domain source. Store one JSON file per book, plus a manifest with byte hashes. Do not rewrite punctuation, capitalization, or footnotes into the `text` field. Footnotes, if kept, live in a sibling field.

Then add WEB and KJV as secondary corpora with the same schema.

### Phase 2 — lookup

A zero-dependency Python CLI:

```sh
python3 -m asb get "John 3:16" --tr BSB
```

Behavior:

- Parse flexible human refs to USFM (`JHN 3:16`).
- Return `passage.v1` JSON on stdout.
- Exit non-zero on unknown book, bad verse, or refused translation.
- Never call a remote Bible API in v0. Offline only.

### Phase 3 — agent packaging

Keep `AGENTS.md` and `skills/scripture-quote/SKILL.md` in sync with lookup flags. Add `llms.txt`. Optional later: MCP that wraps the same local lookup, not a third-party API.

### Phase 4 — fidelity tests

Exact-match tests for a pinned golden set. A paraphrase presented as `kind: quotation` is a failed test. Optional later: compare this lookup against the methods in `apologist-project/llm-scripture-fidelity`.

## Decisions already made

Recorded in [`docs/decisions.md`](docs/decisions.md).

- Default English: BSB.
- Canon for v0: Protestant 66 books.
- Offline corpus, not a live API client.
- Refuse restricted translations rather than "quote with attribution."

## Open questions

- When, if ever, to add deuterocanon / apocrypha as a labeled extra corpus.
- Whether public-domain original-language texts (Westminster Leningrad Codex, and only similarly unrestricted Greek) belong in v1.
- Whether a tiny WASM or Rust lookup belongs beside Python, following the Drip Council fail-closed pattern.
- How strictly to normalize whitespace before hashing.

## Success

v0 is done when an agent with this repo can resolve John 3:16, Psalm 23, and Romans 8:28 from BSB without network access, cannot emit NIV/ESV as this project's text, and fails closed on a fake reference such as "Hezekiah 4:12."
