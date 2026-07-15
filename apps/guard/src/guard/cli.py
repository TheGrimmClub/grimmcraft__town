"""Guard's command-line interface (argparse).

Every command falls back to the shared ``config.yaml`` (the ``guard:`` section)
so ``town`` can drive it with zero arguments, while power users can still
override anything on the command line.
"""

from __future__ import annotations

import argparse
import sys

from filesystem.config import load_config
from minecraft.world import read_world_info

from . import core
from .docs import write_world_readme


def _guard_config() -> dict:
    return load_config().get("guard", {}) or {}


def build_parser(cfg: dict | None = None) -> argparse.ArgumentParser:
    cfg = cfg if cfg is not None else _guard_config()
    parser = argparse.ArgumentParser(
        prog="guard",
        description="Back up, restore and document Minecraft worlds.",
    )
    sub = parser.add_subparsers(dest="command", required=True)

    # -- backup ------------------------------------------------------------
    p_backup = sub.add_parser("backup", help="Zip a world into a timestamped archive")
    p_backup.add_argument("--world", default=cfg.get("world_dir", "./_input"),
                          help="Folder to search for a world (default: %(default)s)")
    p_backup.add_argument("--out", default=cfg.get("archive_dir", "./_backups"),
                          help="Where to write the .zip (default: %(default)s)")
    p_backup.add_argument("--no-docs", action="store_true",
                          help="Do not (re)write the world's README.md first")
    p_backup.set_defaults(func=_cmd_backup)

    # -- restore -----------------------------------------------------------
    p_restore = sub.add_parser("restore", help="Extract a world archive")
    p_restore.add_argument("--archive", required=True, help="The .zip to restore")
    p_restore.add_argument("--to", default=cfg.get("restore_dir", "./_restore"),
                           help="Destination folder (default: %(default)s)")
    p_restore.set_defaults(func=_cmd_restore)

    # -- download ----------------------------------------------------------
    p_dl = sub.add_parser("download", help="Download a world from FTP or HTTP(S)")
    p_dl.add_argument("source", help="A URL, or the name of a source in config.yaml")
    p_dl.add_argument("--to", default=cfg.get("archive_dir", "./_backups"),
                      help="Destination folder (default: %(default)s)")
    p_dl.add_argument("--restore", action="store_true",
                      help="Also restore the downloaded world after downloading")
    p_dl.add_argument("--restore-to", default=cfg.get("restore_dir", "./_restore"),
                      help="Where to restore when --restore is given (default: %(default)s)")
    p_dl.set_defaults(func=_cmd_download)

    # -- info --------------------------------------------------------------
    p_info = sub.add_parser("info", help="Show a world's name, version and datapacks")
    p_info.add_argument("--world", default=cfg.get("world_dir", "./_input"))
    p_info.set_defaults(func=_cmd_info)

    # -- docs --------------------------------------------------------------
    p_docs = sub.add_parser("docs", help="Write the world's README.md")
    p_docs.add_argument("--world", default=cfg.get("world_dir", "./_input"))
    p_docs.set_defaults(func=_cmd_docs)

    return parser


def _resolve_world(where: str):
    from filesystem import paths

    world = paths.locate_directory(where)
    if world is None:
        raise SystemExit(f"guard: no world (level.dat) found under {where}")
    return world


def _cmd_backup(args) -> int:
    result = core.backup(args.world, args.out, write_docs=not args.no_docs)
    print(f"Backed up '{result.info.name}' (mc {result.info.version})")
    if result.readme:
        print(f"  docs   -> {result.readme}")
    print(f"  archive-> {result.archive}")
    return 0


def _cmd_restore(args) -> int:
    dest = core.restore(args.archive, args.to)
    print(f"Restored {args.archive} -> {dest}")
    return 0


def _cmd_download(args) -> int:
    sources = _guard_config().get("sources", {}) or {}
    source = sources.get(args.source, args.source)
    path = core.download(source, args.to)
    print(f"Downloaded -> {path}")
    if args.restore:
        dest = core.restore(path, args.restore_to)
        print(f"Restored  -> {dest}")
    return 0


def _cmd_info(args) -> int:
    info = read_world_info(_resolve_world(args.world))
    print(f"Name:    {info.name}")
    print(f"Version: {info.version}")
    print(f"Data:    {info.data_version}")
    print("Datapacks:")
    for pack in info.datapacks or []:
        mark = "on " if pack.enabled else "off"
        print(f"  [{mark}] {pack.name} — {pack.description or '—'}")
    if not info.datapacks:
        print("  (none)")
    return 0


def _cmd_docs(args) -> int:
    world = _resolve_world(args.world)
    dest = write_world_readme(world, read_world_info(world))
    print(f"Wrote {dest}")
    return 0


def main(argv: list[str] | None = None) -> int:
    args = build_parser().parse_args(argv if argv is not None else sys.argv[1:])
    return args.func(args)


if __name__ == "__main__":
    raise SystemExit(main())
