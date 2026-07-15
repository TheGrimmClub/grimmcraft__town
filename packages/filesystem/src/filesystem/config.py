"""Load and save the shared ``config.yaml`` that ties the tools together.

``town`` edits this file through its UI; the command-line tools (``guard`` …)
read it for their defaults. Keeping it in one place means "the data" lives in
exactly one obvious spot.
"""

from __future__ import annotations

from pathlib import Path
from typing import Any

import yaml

from .paths import as_path

CONFIG_NAME = "config.yaml"

DEFAULT_CONFIG: dict[str, Any] = {
    "guard": {
        "world_dir": "./_input",
        "archive_dir": "./_backups",
        "restore_dir": "./_restore",
        "write_docs": True,
        "sources": {},
    },
    "scout": {},
    "blacksmith": {},
    "town": {"host": "127.0.0.1", "port": 8080},
}


def find_config(start: str | Path | None = None) -> Path | None:
    """Walk up from ``start`` (or cwd) looking for a ``config.yaml``."""
    here = as_path(start or Path.cwd()).resolve()
    for folder in (here, *here.parents):
        candidate = folder / CONFIG_NAME
        if candidate.is_file():
            return candidate
    return None


def load_config(path: str | Path | None = None) -> dict:
    """Load the config, falling back to :data:`DEFAULT_CONFIG` when absent."""
    found = as_path(path) if path else find_config()
    if not found or not Path(found).is_file():
        return dict(DEFAULT_CONFIG)
    data = yaml.safe_load(Path(found).read_text(encoding="utf-8")) or {}
    if not isinstance(data, dict):
        raise ValueError(f"{found} must contain a YAML mapping at the top level")
    return data


def save_config(data: dict, path: str | Path) -> Path:
    """Write ``data`` back to ``path`` as tidy YAML."""
    dest = as_path(path)
    dest.write_text(
        yaml.safe_dump(data, sort_keys=False, allow_unicode=True),
        encoding="utf-8",
    )
    return dest
