# Agent-Safe Bible

A public-domain Scripture corpus and an agent contract so AI systems can quote the Bible **verbatim**, **license-clean**, and **without inventing verses**.

This is a fail-closed layer that treats Scripture as canonical text an agent must look up, not as something a model may recall or paraphrase.

## Why this exists

Open Bible text already exists. Agent Bible tools already exist. What did not exist as one public, vendor-independent project is all of this together:

| Safety | Meaning here |
| --- | --- |
| License-safe | Only unrestricted public-domain translations. No NIV, ESV, NASB, NLT, CSB, NKJV, or other limited-quote editions. |
| Quotation-safe | Agents must not emit Scripture from model memory. Lookup first. If lookup fails, say so. |
| Provenance-safe | Every passage carries translation, reference, and license. Book files are SHA-256 pinned. |
| Role-safe | Quotation and interpretation are separate objects. Commentary is never labeled as Bible text. |

Related work is listed in [`docs/related-work.md`](docs/related-work.md). Decisions are in [`docs/decisions.md`](docs/decisions.md).

## Default text

English default is the **Berean Standard Bible (BSB)**, dedicated to the public domain on 30 April 2023. Secondary allowed translations: **World English Bible (WEB)** and **King James Version (KJV)**.

See [`data/allowlist.json`](data/allowlist.json).

## Lookup

Offline. No Bible API at runtime.

```sh
python3 -m asb get "John 3:16"
python3 -m asb get "Psalm 23:1-4" --tr KJV
python3 -m asb get "John 3:16" --tr NIV   # exits 2, prints no verse
python3 -m asb get "Hezekiah 4:12"        # exits 2, prints no verse
python3 -m asb verify
```

A successful `get` writes a `passage.v1` (or `passages.v1` range) object to stdout. Failures write JSON to stderr and leave stdout empty.

## Agent contract, short form

Full rules: [`AGENTS.md`](AGENTS.md). Skill: [`skills/scripture-quote/SKILL.md`](skills/scripture-quote/SKILL.md). Machine summary: [`llms.txt`](llms.txt).

1. Never quote a verse from memory. Run `python3 -m asb get` or refuse.
2. Never present a paraphrase as Scripture.
3. Never mix commentary into the `text` field of a passage object.
4. Never fetch or paste a refused translation.
5. If the reference is unknown, the translation is not allowlisted, or a hash does not match, **fail closed**.

## MCP

Stdio server wrapping the same local lookup. It does not call HelloAO or any other remote Bible API.

```sh
python3 -m asb mcp
```

Example client config:

```json
{
  "mcpServers": {
    "agent-safe-bible": {
      "command": "python3",
      "args": ["-m", "asb", "mcp"],
      "cwd": "/path/to/agent-safe-bible"
    }
  }
}
```

Tools: `get_passage`, `list_translations`.

## Tests

```sh
python3 tests/test_contract.py
```

## Current status

v0 lookup, hashed 66-book corpora for BSB/WEB/KJV, agent contract, and local MCP are in this repository. Ingest used the HelloAO simplified complete downloads once; runtime is local files only.

## License

- Software, schemas, and documentation in this repository: [MIT](LICENSE).
- Bible text: public domain. See [NOTICE.md](NOTICE.md). Scripture is not licensed as MIT.
