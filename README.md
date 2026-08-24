# Agent-Safe Bible

A public-domain Scripture corpus and an agent contract so AI systems can quote the Bible **verbatim**, **license-clean**, and **without inventing verses**.

This is the planning and contract repo. The gap it fills is not "another Bible API." It is a fail-closed layer that treats Scripture as canonical text an agent must look up, not as something a model may recall or paraphrase.

## Why this exists

Open Bible text already exists. Agent Bible tools already exist. What does not exist as one public, vendor-independent project is all of this together:

| Safety | Meaning here |
| --- | --- |
| License-safe | Only unrestricted public-domain translations. No NIV, ESV, NASB, NLT, CSB, NKJV, or other limited-quote editions. |
| Quotation-safe | Agents must not emit Scripture from model memory. Lookup first. If lookup fails, say so. |
| Provenance-safe | Every passage carries translation, reference, and license. Checksums come with the full corpus. |
| Role-safe | Quotation and interpretation are separate objects. Commentary is never labeled as Bible text. |

Related work is listed in [`docs/related-work.md`](docs/related-work.md). The plan is in [`PLAN.md`](PLAN.md).

## Default text

v0 English default is the **Berean Standard Bible (BSB)**, dedicated to the public domain on 30 April 2023. Secondary allowed translations: **World English Bible (WEB)** and **King James Version (KJV)**.

See [`data/allowlist.json`](data/allowlist.json).

## Agent contract, short form

Full rules: [`AGENTS.md`](AGENTS.md). Skill: [`skills/scripture-quote/SKILL.md`](skills/scripture-quote/SKILL.md).

1. Never quote a verse from memory. Look it up in this corpus or refuse.
2. Never present a paraphrase as Scripture.
3. Never mix commentary into the `text` field of a passage object.
4. Never fetch or paste a refused translation.
5. If the reference is unknown, the translation is not allowlisted, or the text cannot be verified, **fail closed**.

## Current status

Planning. The repository has a charter, an allowlist, a passage schema, three golden John 3:16 fixtures, and an agent skill. It does not yet contain a full 66-book corpus or a lookup tool.

```sh
python3 tests/test_contract.py
```

## License

- Software, schemas, and documentation in this repository: [MIT](LICENSE).
- Bible text: public domain. See [NOTICE.md](NOTICE.md). Scripture is not licensed as MIT.
