"""Command-line entry point: summarise a diff file."""

from __future__ import annotations

import argparse
import sys

from patchkit import __version__
from patchkit.parser import PatchError, parse_patch


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(prog="patchkit", description="Summarise a unified diff.")
    parser.add_argument("file", nargs="?", help="a diff file; reads stdin when omitted")
    parser.add_argument("--stat", action="store_true", help="show a per-file add/remove breakdown")
    parser.add_argument("--version", action="version", version=f"%(prog)s {__version__}")
    args = parser.parse_args(argv)

    text = sys.stdin.read() if args.file is None else _read(args.file)
    if text is None:
        return 2

    try:
        patch = parse_patch(text)
    except PatchError as exc:
        print(f"patchkit: {exc}", file=sys.stderr)
        return 2

    if args.stat:
        width = max((len(p) for p, _, _ in patch.stat()), default=0)
        for path, added, removed in patch.stat():
            print(f"  {path:<{width}}  +{added} -{removed}")
    print(patch.summary())
    return 0


def _read(path: str) -> str | None:
    try:
        with open(path, encoding="utf-8") as fh:
            return fh.read()
    except OSError as exc:
        print(f"patchkit: {exc}", file=sys.stderr)
        return None


if __name__ == "__main__":  # pragma: no cover
    raise SystemExit(main())
