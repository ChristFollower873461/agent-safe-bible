# Scripture quote

Use this skill whenever a human asks for a Bible verse, passage, or "what does the Bible say."

## Do this

1. Read `data/allowlist.json`. Default translation is `BSB`.
2. If the asked translation is in `refused`, refuse. Suggest BSB, WEB, or KJV.
3. From this repository, run:

   ```sh
   python3 -m asb get "John 3:16" --tr BSB
   ```

4. Emit the stdout JSON as the quotation, or a block quote that copies `text` exactly and names `translation` plus `ref`.
5. Put any explanation after the quote. Never inside it.
6. If stdout is empty and the process exits non-zero, report the stderr JSON. Do not invent a verse.

## Do not do this

- Quote from memory, including John 3:16, Genesis 1:1, Psalm 23, or Romans 8:28.
- Paraphrase and label it Scripture.
- Invent a reference.
- Use NIV, ESV, NASB, NLT, CSB, or NKJV.
- Call a remote Bible API. Lookup is local and hashed.

## Commands

```sh
python3 -m asb get "Genesis 1:1"
python3 -m asb get "Psalm 23:1-6" --tr KJV
python3 -m asb get "John 3:16" --tr WEB
python3 -m asb mcp
```

A range returns `agent-safe-bible.passages.v1` with one `passage.v1` object per verse.
