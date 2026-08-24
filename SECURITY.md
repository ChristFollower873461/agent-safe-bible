# Security

This repository is static text and a planned local lookup. There is no production server in v0.

Report a vulnerability privately via GitHub Security Advisories on this repository. Do not open a public issue for a real exploit.

In scope later: path traversal in lookup, hash-bypass, supply-chain issues in ingest scripts, and prompt-injection that causes an agent using this contract to emit refused translations or invented verses *if that is caused by a defect in our tools*.

Out of scope: an LLM ignoring `AGENTS.md`. That is a model-compliance problem, not a CVE. We still want tests that make compliance failures visible.
