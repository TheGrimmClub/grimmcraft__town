"""Blacksmith CLI (stub). Builds datapack functions; full spec comes later."""

from __future__ import annotations

import argparse
import sys

from filesystem import paths
from filesystem.config import load_config
from filesystem.world import discover_datapacks


def build_parser() -> argparse.ArgumentParser:
    guard_cfg = load_config().get("guard", {}) or {}
    default_world = (load_config().get("blacksmith", {}) or {}).get("world_dir") or guard_cfg.get("world_dir", "./_input")

    parser = argparse.ArgumentParser(prog="blacksmith", description="Build functions in datapacks.")
    sub = parser.add_subparsers(dest="command", required=True)

    p_list = sub.add_parser("list", help="List datapacks found in the world")
    p_list.add_argument("--world", default=default_world)
    p_list.set_defaults(func=_cmd_list)

    return parser


def _cmd_list(args) -> int:
    world = paths.locate_world(args.world)
    if world is None:
        raise SystemExit(f"blacksmith: no world found under {args.world}")
    packs = discover_datapacks(world)
    if not packs:
        print("No datapacks found.")
    for pack in packs:
        print(f"- {pack.name}: {pack.description or '—'}")
    print("blacksmith: function forging coming in a later stage.")
    return 0


def main(argv: list[str] | None = None) -> int:
    args = build_parser().parse_args(argv if argv is not None else sys.argv[1:])
    return args.func(args)


if __name__ == "__main__":
    raise SystemExit(main())
