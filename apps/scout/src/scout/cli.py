"""Scout CLI — read Minecraft world data, especially command blocks."""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

from filesystem import paths
from filesystem.config import load_config
from filesystem.world import read_world_info

from . import core, report


def _default_world() -> str:
    cfg = load_config()
    scout_cfg = cfg.get("scout", {}) or {}
    return scout_cfg.get("world_dir") or (cfg.get("guard", {}) or {}).get("world_dir", "./_input")


def build_parser() -> argparse.ArgumentParser:
    world_default = _default_world()
    parser = argparse.ArgumentParser(prog="scout", description="Read Minecraft world data.")
    sub = parser.add_subparsers(dest="command", required=True)

    p_info = sub.add_parser("info", help="Quick one-line world summary")
    p_info.add_argument("--world", default=world_default)
    p_info.set_defaults(func=_cmd_info)

    p_scan = sub.add_parser("scan", help="Full scan: world info + block-entity counts + command blocks")
    p_scan.add_argument("--world", default=world_default)
    p_scan.add_argument("--json", action="store_true", help="Emit JSON instead of a text summary")
    p_scan.add_argument("--out", help="Write the JSON scan to this file")
    p_scan.set_defaults(func=_cmd_scan)

    p_cmd = sub.add_parser("commands", help="List every command block and its command")
    p_cmd.add_argument("--world", default=world_default)
    p_cmd.add_argument("--json", action="store_true", help="Emit JSON instead of a table")
    p_cmd.add_argument("--out", help="Write the output to this file")
    p_cmd.add_argument("--contains", help="Only show commands containing this text")
    p_cmd.set_defaults(func=_cmd_commands)

    p_report = sub.add_parser("report", help="Write a Markdown report of the world")
    p_report.add_argument("--world", default=world_default)
    p_report.add_argument("--out", help="Write the Markdown here (default: stdout)")
    p_report.add_argument("--max", type=int, default=200, help="Max command blocks to list (default: %(default)s)")
    p_report.set_defaults(func=_cmd_report)

    return parser


def _resolve_world(where: str) -> Path:
    world = paths.locate_world(where)
    if world is None:
        raise SystemExit(f"scout: no world (level.dat) found under {where}")
    return world


def _emit(text: str, out: str | None) -> None:
    if out:
        Path(out).write_text(text if text.endswith("\n") else text + "\n", encoding="utf-8")
        print(f"Wrote {out}")
    else:
        print(text)


def _cmd_info(args) -> int:
    info = read_world_info(_resolve_world(args.world))
    print(f"{info.name} — mc {info.version} — {len(info.datapacks)} datapack(s)")
    return 0


def _cmd_scan(args) -> int:
    scan = core.scan_world(args.world)
    if args.json or args.out:
        _emit(json.dumps(report.to_dict(scan), indent=2), args.out)
        return 0
    print(f"World:           {scan.info.name} (mc {scan.info.version})")
    print(f"Datapacks:       {', '.join(p.name for p in scan.info.datapacks) or 'none'}")
    print(f"Block entities:  {scan.total_block_entities} across {len(scan.block_entity_counts)} types")
    print(f"Command blocks:  {len(scan.command_blocks)}")
    print("Top block entities:")
    for block_id, count in list(scan.block_entity_counts.items())[:8]:
        print(f"  {count:>5}  {block_id}")
    return 0


def _cmd_commands(args) -> int:
    scan = core.scan_world(args.world)
    blocks = scan.command_blocks
    if args.contains:
        needle = args.contains.lower()
        blocks = [cb for cb in blocks if needle in cb.command.lower()]

    if args.json or args.out and args.out.endswith(".json"):
        from dataclasses import asdict

        _emit(json.dumps([asdict(cb) for cb in blocks], indent=2), args.out)
        return 0

    lines = [f"{len(blocks)} command block(s):"]
    for cb in blocks:
        flag = " [auto]" if cb.auto else ""
        lines.append(f"  {cb.dimension} {cb.coords}{flag}: {cb.command}")
    _emit("\n".join(lines), args.out)
    return 0


def _cmd_report(args) -> int:
    scan = core.scan_world(args.world)
    _emit(report.render_markdown(scan, max_commands=args.max), args.out)
    return 0


def main(argv: list[str] | None = None) -> int:
    args = build_parser().parse_args(argv if argv is not None else sys.argv[1:])
    return args.func(args)


if __name__ == "__main__":
    raise SystemExit(main())
