"""CLI: python3 -m asb get|ingest|mcp|verify."""

from __future__ import annotations

import argparse
import sys

from .jsonutil import dumps
from .lookup import LookupFailure, get


def _fail(exc: LookupFailure) -> int:
    sys.stderr.write(dumps(exc.as_dict()))
    return 2


def cmd_get(args: argparse.Namespace) -> int:
    try:
        result = get(args.ref, args.tr)
    except LookupFailure as exc:
        return _fail(exc)
    sys.stdout.write(dumps(result))
    return 0


def cmd_ingest(args: argparse.Namespace) -> int:
    from .ingest import ingest

    translations = None
    if args.tr:
        translations = [item.strip().upper() for item in args.tr.split(",") if item.strip()]
    ingest(translations, force=args.force)
    return 0


def cmd_verify(_args: argparse.Namespace) -> int:
    from .allowlist import allowed_ids
    from .corpus import CORPUS_ROOT, load_manifest
    from .jsonutil import sha256_file

    errors = 0
    for translation in sorted(allowed_ids()):
        try:
            manifest = load_manifest(translation)
        except Exception as exc:  # noqa: BLE001
            sys.stderr.write(f"{translation}: {exc}\n")
            errors += 1
            continue
        for row in manifest["files"]:
            path = CORPUS_ROOT / translation / row["path"]
            digest = sha256_file(path) if path.is_file() else None
            if digest != row["sha256"]:
                sys.stderr.write(f"hash mismatch {translation}/{row['path']}\n")
                errors += 1
    if errors:
        return 2
    sys.stdout.write("ok corpus hashes\n")
    return 0


def cmd_mcp(_args: argparse.Namespace) -> int:
    from .mcp import serve

    serve()
    return 0


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(prog="python3 -m asb", description="Agent-Safe Bible lookup")
    sub = parser.add_subparsers(dest="command", required=True)

    get_p = sub.add_parser("get", help="look up a verse or range from the local corpus")
    get_p.add_argument("ref", help='reference, e.g. "John 3:16"')
    get_p.add_argument("--tr", default=None, help="translation id (default BSB)")
    get_p.set_defaults(func=cmd_get)

    ingest_p = sub.add_parser("ingest", help="download HelloAO texts into data/corpus (maintainers)")
    ingest_p.add_argument("--tr", default=None, help="comma-separated ids, default all allowed")
    ingest_p.add_argument("--force", action="store_true", help="re-download cached complete JSON")
    ingest_p.set_defaults(func=cmd_ingest)

    verify_p = sub.add_parser("verify", help="check corpus SHA-256 manifests")
    verify_p.set_defaults(func=cmd_verify)

    mcp_p = sub.add_parser("mcp", help="stdio MCP server wrapping local lookup")
    mcp_p.set_defaults(func=cmd_mcp)
    return parser


def main(argv: list[str] | None = None) -> int:
    parser = build_parser()
    args = parser.parse_args(argv)
    return args.func(args)


if __name__ == "__main__":
    sys.exit(main())
