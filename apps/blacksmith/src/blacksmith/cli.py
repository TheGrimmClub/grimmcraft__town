"""Blacksmith's command-line interface (argparse).

``list`` reports the datapacks in a world; ``forge`` generates one from a small
palette. Both fall back to the shared ``config.yaml`` (the ``blacksmith:``
section) so ``town`` can drive them with zero arguments.
"""

from __future__ import annotations

import argparse
import sys

from filesystem import paths
from filesystem.config import load_config
from minecraft.world import discover_datapacks

from . import core

NAME = 'blacksmith'


def _blacksmith_config() -> dict:
    return load_config().get(NAME, {}) or {}


def _default_world() -> str:
    cfg = load_config()
    blacksmith = cfg.get(NAME, {}) or {}
    guard = cfg.get("guard", {}) or {}
    return blacksmith.get("world_dir") or guard.get("world_dir", "./_input")


def build_parser() -> argparse.ArgumentParser:
    default_world = _default_world()

    parser = argparse.ArgumentParser(prog=NAME, description="Build functions in datapacks.")
    sub = parser.add_subparsers(dest="command", required=True)

    p_list = sub.add_parser("list", help="List datapacks found in the world")
    p_list.add_argument("--world", default=default_world)
    p_list.set_defaults(func=_cmd_list)

    p_forge = sub.add_parser("forge", help="Forge (generate) a datapack's functions")
    p_forge.add_argument("kind", choices=["fireworks"], help="What to forge")
    p_forge.add_argument("--world", default=default_world,
                         help="Folder to search for a world (default: %(default)s)")
    p_forge.add_argument("--name", default="fireworks", help="Datapack folder name (default: %(default)s)")
    p_forge.add_argument("--namespace", default=None,
                         help="Function namespace (default: same as --name)")
    p_forge.add_argument("--variants", type=int, default=None,
                         help="Numbered rockets per colour/shape (default: 1)")
    p_forge.add_argument("--force", action="store_true", help="Overwrite an existing datapack")
    p_forge.set_defaults(func=_cmd_forge)

    return parser


def _resolve_world(where: str):
    world = paths.locate_directory(where)
    if world is None:
        raise SystemExit(f"{NAME}: no world (level.dat) found under {where}")
    return world


def _cmd_list(args) -> int:
    world = _resolve_world(args.world)
    packs = discover_datapacks(world)
    if not packs:
        print(f"{NAME}: No datapacks found.")
    for pack in packs:
        print(f"- {pack.name}: {pack.description or '—'}")
    return 0


def _cmd_forge(args) -> int:
    world = _resolve_world(args.world)
    fw = _blacksmith_config().get(args.kind, {}) or {}
    variants = args.variants if args.variants is not None else fw.get("variants", 1)
    try:
        result = core.forge_fireworks(
            world,
            name=args.name,
            namespace=args.namespace or args.name,
            colors=fw.get("colors"),
            shapes=fw.get("shapes"),
            variants=variants,
            force=args.force,
        )
    except (FileExistsError, ValueError) as exc:
        raise SystemExit(f"{NAME}: {exc}")

    print(f"Forged '{args.kind}' -> {result.datapack}")
    print(f"  {result.files_written} files, {len(result.timers)} timed rockets")
    print(f'  enable it in-game with:  /datapack enable "file/{args.name}"')
    return 0


def main(argv: list[str] | None = None) -> int:
    args = build_parser().parse_args(argv if argv is not None else sys.argv[1:])
    return args.func(args)


if __name__ == "__main__":
    raise SystemExit(main())
