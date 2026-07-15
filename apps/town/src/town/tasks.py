"""Discover the buttons from Taskfiles.

The Taskfiles are the single source of truth for "what can town do". We ask
``task --list --json`` for the described tasks and group them by their
namespace (``guard:backup`` -> group ``guard``, action ``backup``).
"""

from __future__ import annotations

import json
import subprocess
from dataclasses import dataclass
from pathlib import Path


@dataclass
class TaskButton:
    name: str          # full task name, e.g. "guard:backup"
    group: str         # namespace, e.g. "guard" ("" for root tasks)
    action: str        # short name, e.g. "backup"
    desc: str          # description shown on the button/tooltip


def find_repo_root(start: str | Path | None = None) -> Path:
    """Walk up until we find the folder that holds the root Taskfile."""
    here = Path(start or Path.cwd()).resolve()
    for folder in (here, *here.parents):
        if (folder / "Taskfile.yaml").is_file() or (folder / "Taskfile.yml").is_file():
            return folder
    return here


def list_tasks(root: str | Path | None = None) -> list[TaskButton]:
    """Return the described tasks from the root Taskfile as buttons."""
    root = find_repo_root(root)
    proc = subprocess.run(
        ["task", "--list", "--json"],
        cwd=root,
        capture_output=True,
        text=True,
        check=False,
    )
    if proc.returncode != 0 or not proc.stdout.strip():
        return []

    data = json.loads(proc.stdout)
    buttons: list[TaskButton] = []
    for task in data.get("tasks", []):
        full = task.get("name", "")
        group, sep, action = full.partition(":")
        buttons.append(
            TaskButton(
                name=full,
                group=group if sep else "",
                action=action if sep else full,
                desc=task.get("desc", ""),
            )
        )
    return buttons


def group_tasks(buttons: list[TaskButton]) -> dict[str, list[TaskButton]]:
    """Group buttons by namespace, preserving first-seen order."""
    groups: dict[str, list[TaskButton]] = {}
    for button in buttons:
        groups.setdefault(button.group or "general", []).append(button)
    return groups
