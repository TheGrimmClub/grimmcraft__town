"""Path helpers — find things and make folders without ceremony."""

from __future__ import annotations

from pathlib import Path

# Names that macOS / editors sprinkle around and that we never want in a backup.
JUNK_NAMES = {".DS_Store", "__MACOSX", "Thumbs.db", ".Spotlight-V100", ".Trashes"}


def as_path(value: str | Path) -> Path:
    """Turn a string or Path into an expanded, absolute-ish Path."""
    return Path(value).expanduser()


def ensure_dir(path: str | Path) -> Path:
    """Create ``path`` (and parents) if missing, then return it."""
    p = as_path(path)
    p.mkdir(parents=True, exist_ok=True)
    return p


def is_junk(path: str | Path) -> bool:
    """True if any part of the path is macOS / editor clutter."""
    parts = as_path(path).parts
    name = as_path(path).name
    return name in JUNK_NAMES or any(part in JUNK_NAMES for part in parts)


def locate_world(root: str | Path) -> Path | None:
    """Find a Minecraft world folder under ``root``.

    A world folder is any directory that contains a ``level.dat`` file.
    Returns the folder, or ``None`` if none is found. If ``root`` itself is a
    world, ``root`` is returned unchanged.
    """
    root = as_path(root)
    if not root.exists():
        return None
    if (root / "level.dat").is_file():
        return root
    for level in sorted(root.rglob("level.dat")):
        if not is_junk(level):
            return level.parent
    return None
