"""alchemist's command-line interface (argparse).

Scaffolded by carpenter — replace the starter ``hello`` command with real
ones. Follows the same shape as the other tools (guard, scout, …).
"""

from __future__ import annotations

import argparse
import sys

NAME = "alchemist"


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(prog=NAME, description="working with the version contol system")
    sub = parser.add_subparsers(dest="command", required=True)

    p_hello = sub.add_parser("hello", help="Say hello (starter command)")
    p_hello.set_defaults(func=_cmd_hello)

    return parser


def _cmd_hello(args) -> int:
    print(f"{NAME}: hello! Replace me with real commands.")
    return 0


def main(argv: list[str] | None = None) -> int:
    args = build_parser().parse_args(argv if argv is not None else sys.argv[1:])
    return args.func(args)


if __name__ == "__main__":
    raise SystemExit(main())
