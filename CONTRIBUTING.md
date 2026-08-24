# Contributing

Thank you. This repo is a public-domain Scripture contract, so contribution quality is mostly about **not changing the words**.

## First reads

1. `README.md`
2. `PLAN.md`
3. `AGENTS.md`
4. `NOTICE.md`
5. `docs/decisions.md`

## What we want

- Allowlist and schema fixes.
- Documented corpus ingest scripts that preserve verbatim text.
- Lookup, parser, and exact-match tests.
- Agent-skill and MCP wrappers around the local lookup.
- Accessibility and docs.

## What we will reject

- Copyrighted translations, even with "for personal use" or "fair use" notes.
- Paraphrases, AI-rewritten verses, or "easier English" editions presented as BSB/WEB/KJV.
- Silent wording changes in fixtures or corpus files.
- Remote API clients as the v0 source of truth.

## Corpus PRs

A corpus pull request must include:

- Source URL and license proof in `NOTICE.md` or a per-translation notice.
- SHA-256 of the canonical JSON in a manifest.
- The ingest script, so the files are reproducible.
- Golden-verse tests that fail if a single character in the quoted `text` changes.

## Tests

```sh
python3 tests/test_contract.py
```

Add tests with the change. Do not merge a wording change that only updates a fixture to make a test pass unless the source edition actually changed and that change is documented.
