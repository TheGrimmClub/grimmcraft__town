"""Turn a WorldScan into JSON-friendly data and a Markdown report."""

from __future__ import annotations

from dataclasses import asdict

from .core import CommandBlock, WorldScan


def to_dict(scan: WorldScan) -> dict:
    """A plain, JSON-serialisable view of a scan."""
    return {
        "world": {
            "name": scan.info.name,
            "version": scan.info.version,
            "data_version": scan.info.data_version,
            "path": str(scan.world),
            "datapacks": [
                {"name": p.name, "description": p.description, "enabled": p.enabled}
                for p in scan.info.datapacks
            ],
        },
        "block_entities": {
            "total": scan.total_block_entities,
            "by_type": scan.block_entity_counts,
        },
        "command_blocks": [asdict(cb) for cb in scan.command_blocks],
    }


def render_markdown(scan: WorldScan, *, max_commands: int | None = 200) -> str:
    """A human-readable Markdown report of a scan."""
    info = scan.info
    lines = [
        f"# Scout report: {info.name}",
        "",
        f"- **Version:** {info.version} (data {info.data_version})",
        f"- **Datapacks:** {', '.join(p.name for p in info.datapacks) or 'none'}",
        f"- **Block entities:** {scan.total_block_entities} across {len(scan.block_entity_counts)} types",
        f"- **Command blocks:** {len(scan.command_blocks)}",
        "",
        "## Block entities by type",
        "",
        "| Type | Count |",
        "| --- | ---: |",
    ]
    for block_id, count in scan.block_entity_counts.items():
        lines.append(f"| `{block_id}` | {count} |")

    lines += ["", "## Command blocks", ""]
    blocks = scan.command_blocks
    if not blocks:
        lines.append("_None found._")
        return "\n".join(lines) + "\n"

    shown = blocks if max_commands is None else blocks[:max_commands]
    lines += ["| Dimension | Coords | Auto | Command |", "| --- | --- | :---: | --- |"]
    for cb in shown:
        command = cb.command.replace("|", "\\|") or "—"
        lines.append(f"| {cb.dimension} | `{cb.block_info()}` | `{cb.conditional_info()}` | `{cb.is_always_active()}` | `{cb.coords}`, {cb.coords_info()} | {'⚡' if cb.auto else ''} | `{command}` |")
    if max_commands is not None and len(blocks) > max_commands:
        lines.append("")
        lines.append(f"_… and {len(blocks) - max_commands} more (raise --max to see them)._")
    return "\n".join(lines) + "\n"
