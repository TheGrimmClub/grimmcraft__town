"""The actual world-keeping operations, kept separate from the CLI wiring."""

from __future__ import annotations

import re
from dataclasses import dataclass
from datetime import date
from pathlib import Path

from filesystem import paths, transfer
from filesystem.archive import Archive
from filesystem.world import WorldInfo, read_world_info

from .docs import write_world_readme

_SAFE = re.compile(r"[^A-Za-z0-9._-]+")


def _slug(text: str) -> str:
    """Make a token safe for a filename (letters, digits, ``-_.``)."""
    return _SAFE.sub("-", text).strip("-") or "unknown"


def archive_name(name: str, version: str, when: date | None = None) -> str:
    """Build ``{worldname}__mc{version}__{date}.zip``."""
    when = when or date.today()
    return f"{_slug(name)}__mc{_slug(version)}__{when:%Y-%m-%d}.zip"


@dataclass
class BackupResult:
    archive: Path
    info: WorldInfo
    readme: Path | None


def backup(
    world_dir: str | Path,
    out_dir: str | Path,
    *,
    write_docs: bool = True,
    when: date | None = None,
) -> BackupResult:
    """Locate a world under ``world_dir``, document it and zip it into ``out_dir``."""
    world = paths.locate_world(world_dir)
    if world is None:
        raise FileNotFoundError(f"No Minecraft world (level.dat) found under {world_dir}")

    info = read_world_info(world)
    readme = write_world_readme(world, info, when=when) if write_docs else None

    # Use filesystem.Archive directly: we already know the exact filename we
    # want, so keep it verbatim (do_cleanup=False) and don't let Archive append
    # its own date (do_date=False) — guard's name already carries the date.
    out = paths.ensure_dir(out_dir)
    filename = archive_name(info.name, info.version, when)
    Archive(filename, do_cleanup=False).create(world, out, do_date=False)
    return BackupResult(archive=out / filename, info=info, readme=readme)


def restore(archive_path: str | Path, dest_dir: str | Path) -> Path:
    """Extract a world archive into ``dest_dir``."""
    dest = paths.ensure_dir(dest_dir)
    Archive(str(archive_path), do_cleanup=False).extract(archive_path, dest)
    return dest


def download(source, dest_dir: str | Path) -> Path:
    """Download a world from a URL string or a source dict into ``dest_dir``.

    Returns the path of the downloaded file.
    """
    dest_dir = paths.ensure_dir(dest_dir)
    if isinstance(source, str):
        return transfer.download(source, dest_dir / transfer.suggest_filename(source, "world.zip"))
    # source is a dict describing an ftp/http endpoint
    url = source.get("url", "")
    filename = source.get("filename") or transfer.suggest_filename(url, "world.zip")
    return transfer.fetch(source, dest_dir / filename)
