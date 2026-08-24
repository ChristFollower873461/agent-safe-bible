# Scripture quote

Use this skill whenever a human asks for a Bible verse, passage, or "what does the Bible say."

## Do this

1. Read `data/allowlist.json`. Default translation is `BSB`.
2. If the asked translation is in `refused`, refuse. Suggest BSB, WEB, or KJV.
3. Look up the reference in this repository. Until the full corpus exists, only quote files you have actually opened under `data/fixtures/`.
4. Emit the passage as `agent-safe-bible.passage.v1` JSON, or a block quote that copies `text` exactly and names `translation` plus `ref`.
5. Put any explanation after the quote. Never inside it.

## Do not do this

- Quote from memory.
- Paraphrase and label it Scripture.
- Invent a reference.
- Use NIV, ESV, NASB, NLT, CSB, or NKJV.
- Claim the 66-book corpus is present before ingest lands.

## Current fixtures

- `data/fixtures/john-3-16.bsb.json`
- `data/fixtures/john-3-16.web.json`
- `data/fixtures/john-3-16.kjv.json`

If the human asks for any other verse, say it is not in the corpus yet.
