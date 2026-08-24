# Notices

This project contains two classes of material.

## Software, schemas, and documentation

Copyright 2026 Philip Standley. Licensed under the MIT License. See `LICENSE`.

## Bible text

Bible translations in this repository are **not** licensed under MIT. They remain public domain.

### Berean Standard Bible (BSB)

The Berean Bible texts were dedicated to the public domain as of 30 April 2023. All uses are freely permitted. Attribution is appreciated but not required.

The Holy Bible, Berean Standard Bible, BSB is produced in cooperation with Bible Hub, Discovery Bible, OpenBible.com, and the Berean Bible Translation Committee. This text of God's Word has been dedicated to the public domain.

- Terms: https://berean.bible/terms.htm
- Homepage: https://berean.bible
- Ingest source: HelloAO id `BSB` from https://bible.helloao.org/api/BSB/complete.simple.json

### King James Version (KJV)

The 1769 King James Version is in the public domain in the United States.

Ingest source: HelloAO id `eng_kjv` from https://bible.helloao.org/api/eng_kjv/complete.simple.json
Edition details: https://ebible.org/Scriptures/details.php?id=eng-kjv2006

Leading pilcrow characters (`¶`) are printing marks and are stripped at ingest. Verse wording is not otherwise changed.

### World English Bible (WEB)

The World English Bible is in the public domain.

- https://worldenglish.bible
- Ingest source: HelloAO id `ENGWEBP` (Protestant 66 books) from https://bible.helloao.org/api/ENGWEBP/complete.simple.json
- Edition details: https://ebible.org/Scriptures/details.php?id=engwebp

This edition uses "only born Son" in John 3:16. Verses that HelloAO returns with empty text (omitted readings such as Luke 17:36) are skipped, not filled in.

### Ingest provider

Corpus files were generated from the [HelloAO Free Use Bible API](https://bible.helloao.org/) simplified complete downloads. Runtime lookup does not call that API.

## What this project will not ship

This project will not vendor, cache, or emit translations with quotation limits or commercial licenses, including but not limited to NIV, ESV, NASB, NLT, CSB, and NKJV.
