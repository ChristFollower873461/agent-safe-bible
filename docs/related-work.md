# Related work

This project does not pretend the landscape is empty. It names the closest neighbors and the remaining gap.

## Public-domain text

| Project | What it is | Why it is not this |
| --- | --- | --- |
| [HelloAO Free Use Bible API](https://bible.helloao.org/) | Large free JSON API, including BSB. No keys. | Live API, not a fail-closed agent contract or a pinned local corpus. |
| [seven1m/open-bibles](https://github.com/seven1m/open-bibles) | Libre Bible XML corpus. | Human/library formats, not an agent quotation layer. |
| [seven1m/bible_api](https://github.com/seven1m/bible_api) | bible-api.com JSON API. | Network lookup; limited agent policy. |
| [TehShrike/world-english-bible](https://github.com/TehShrike/world-english-bible) | WEB as JSON. | One translation, no safety contract. |
| [BSB-publishing/bsb2usfm](https://github.com/BSB-publishing/bsb2usfm) | BSB/MSB to USFM. | Source we may ingest from; not agent-facing. |

## Agent-facing tools

| Project | What it is | Why it is not this |
| --- | --- | --- |
| [V-Gutierrez/faith](https://github.com/V-Gutierrez/faith) | Offline agent-first Bible CLI. Closest cousin. | Seeds from HelloAO; not a license-firewall corpus with a refuse-list and quotation/interpretation split. |
| [TJ-Frederick/TheologAI](https://github.com/TJ-Frederick/TheologAI) | Study MCP (text, commentary, creeds). | Study stack, including some keyed APIs. |
| [djayatillake/studybible-mcp](https://github.com/djayatillake/studybible-mcp) | Hermeneutics MCP. | CC study data, not a verbatim-quote contract. |
| [eliranwong/biblemate](https://github.com/eliranwong/biblemate) | Autonomous Bible-study agent. | Application, not a shared safety corpus. |

## Quotation fidelity

| Project | What it is | Why it is not this |
| --- | --- | --- |
| [apologist-project/llm-scripture-fidelity](https://github.com/apologist-project/llm-scripture-fidelity) | Research on how models quote Scripture. Shows unassisted memory is unreliable. | Benchmark, not a productized allowlisted corpus. |
| [ArVaViT/equip](https://github.com/ArVaViT/equip) | Canonical-text substitution so quotes stay verbatim. | LMS pipeline, not a public agent Bible. |

## The gap

No public repo we found is all of: vendor-independent local corpus, public-domain allowlist with an explicit refuse-list, `passage.v1` that forbids mixing commentary into quote text, and an agent contract that fails closed instead of guessing.
