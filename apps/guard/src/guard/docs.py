"""Generate a small self-documenting README.md for a world."""

from __future__ import annotations

from datetime import date
from pathlib import Path

from minecraft.world import WorldInfo


def render_readme(info: WorldInfo, *, when: date | None = None) -> str:
    """Build the Markdown text describing ``info``."""
    when = when or date.today()
    lines = [
        f"# World: {info.name}",
        "",
        "> Documented automatically by **guard**.",
        "",
        "## Overview",
        "",
        f"- **Name:** {info.name}",
        f"- **Minecraft version:** {info.version}",
    ]
    if info.data_version is not None:
        lines.append(f"- **Data version:** {info.data_version}")
    lines.append(f"- **Documented:** {when:%Y-%m-%d}")
    lines.append("")

    lines.append("## Datapacks")
    lines.append("")
    if info.datapacks:
        lines.append("| Datapack | Enabled | Description |")
        lines.append("| --- | --- | --- |")
        for pack in info.datapacks:
            mark = "✅" if pack.enabled else "❌"
            desc = pack.description.replace("|", "\\|") or "—"
            lines.append(f"| `{pack.name}` | {mark} | {desc} |")
    else:
        lines.append("_No datapacks found._")
    lines.append("")

    lines.append("<!-- scout will add mods and richer world data here later. -->")
    lines.append("")
    return "\n".join(lines)


def write_world_readme(world_dir: str | Path, info: WorldInfo, *, when: date | None = None) -> Path:
    """Write ``README.md`` into the world root and return its path."""
    dest = Path(world_dir) / "README.md"
    dest.write_text(render_readme(info, when=when), encoding="utf-8")
    return dest
