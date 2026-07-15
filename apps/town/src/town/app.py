"""Town — the NiceGUI control room.

Layout:
- one tab per tool (guard / scout / blacksmith), discovered from the Taskfiles
- each tab shows the tool's ``config.yaml`` section as editable fields
  (Save writes them straight back to disk)
- each tab shows a button per Task action; clicking one runs
  ``task <group>:<action>`` and streams the output into a shared log
"""

from __future__ import annotations

import asyncio

import yaml
from nicegui import ui

from filesystem.config import CONFIG_NAME, load_config, save_config

from .tasks import TaskButton, find_repo_root, group_tasks, list_tasks
from typing import Any

ROOT = find_repo_root()
CONFIG_PATH = ROOT / CONFIG_NAME


class Terminal:
    """A small, colorful log panel with a Clear button.

    NiceGUI's ``ui.log`` paints every line the same color; this keeps the black,
    monospaced terminal feel but colors each line by *kind* (prompt, output,
    warning, error, exit status) and lets the user wipe it with one click.
    """

    palette: dict[str,str] = {
        "prompt": "text-cyan-300",
        "info": "text-slate-200",
        "good": "text-green-400",
        "warn": "text-amber-300",
        "error": "text-red-400",
    }

    def __init__(self, max_lines: int = 500) -> None:
        self._max_lines: int = max_lines
        self._lines: list[ui.label] = []

        config: dict[str,Any] = load_config(CONFIG_PATH if CONFIG_PATH.is_file() else None).get("town", {}) or {}
        terminal_config = config.get("terminal", {})
        if terminal_config:
            self.palette = terminal_config
        else:
            pass # use the already set


        with ui.card().classes("w-full p-0 gap-0 overflow-hidden bg-black"):
            with ui.row().classes("w-full items-center justify-between px-3 py-1 bg-gray-900"):
                ui.label("Terminal").classes("text-xs font-mono text-gray-400")
                ui.button("Clear", icon="delete_sweep", on_click=self.clear) \
                    .props("flat dense no-caps color=grey-5")
            self._scroll: ui.scroll_area = ui.scroll_area().classes("w-full h-64 bg-black px-3 py-2")
            with self._scroll:
                self._body: ui.column = ui.column().classes("gap-0 font-mono text-xs")

    def push(self, text: str, kind: str = "info") -> None:
        colour = self.palette.get(kind, self.palette["info"])
        with self._body:
            label = ui.label(text).classes(f"{colour} whitespace-pre-wrap leading-snug")
        self._lines.append(label)
        while len(self._lines) > self._max_lines:
            self._body.remove(self._lines.pop(0))
        self._scroll.scroll_to(percent=1.0)

    def clear(self) -> None:
        self._body.clear()
        self._lines.clear()


def _classify(line: str) -> str:
    """Pick a colour *kind* for a line of streamed task output."""
    low = line.lower()
    if any(w in low for w in ("error", "traceback", "exception", "failed", "fatal")):
        return "error"
    if any(w in low for w in ("warning", "deprecat")):
        return "warn"
    if low.startswith("task:") or line.startswith("["):
        return "warn"
    return "info"


def _run_ui() -> None:
    state: dict = load_config(CONFIG_PATH if CONFIG_PATH.is_file() else None)
    buttons = list_tasks(ROOT)
    groups = group_tasks(buttons)
    config = load_config(CONFIG_PATH if CONFIG_PATH.is_file() else None).get("town", {}) or {}
    title: str = str(config.get("title", "GrimmCraft"))
    links: dict[str,str] = config.get("links", {})

    # keep tool tabs first and in a friendly order
    order = ["guard", "scout", "blacksmith", "alchemist", "carpenter", "town"]
    tool_names = sorted(groups, key=lambda g: (order.index(g) if g in order else 99, g))

    complex_editors: list[tuple[dict, str, "ui.textarea"]] = []

    ui.colors(primary="#5b7c99")
    with ui.header().classes("items-center justify-between"):
        with ui.column():
            ui.label(title).classes("text-xl font-bold")
            with ui.row():
                with ui.card():
                    # open the folder
                    ui.link(str(ROOT), f'file://{str(ROOT)}', new_tab=True).classes("text-l")

                for title, link in links.items():
                    with ui.card():
                        ui.link(title, link, new_tab=True)

                #ui.link('GrimmCraft Town on GitHub', 'https://github.com/TheGrimmClub/grimmcraft__town', new_tab=True)
                #ui.link('Grimmoire', 'https://thegrimmclub.github.io/grimmoire/', new_tab=True)
                #ui.link('Aternos Coding', 'https://aternos.org/worlds/', new_tab=True)
                #ui.link('NiceGUI', 'https://nicegui.io/documentation', new_tab=True)



    # Shared colourful terminal, shown under the tabs.
    terminal = Terminal()

    async def run_task(name: str) -> None:
        terminal.push(f"$ task {name}", "prompt")
        proc = await asyncio.create_subprocess_exec(
            "task", name,
            cwd=str(ROOT),
            stdout=asyncio.subprocess.PIPE,
            stderr=asyncio.subprocess.STDOUT,
        )
        assert proc.stdout is not None
        async for raw in proc.stdout:
            line = raw.decode(errors="replace").rstrip()
            terminal.push(line, _classify(line))
        await proc.wait()
        ok = proc.returncode == 0
        terminal.push(f"[exit {proc.returncode}]", "good" if ok else "error")
        ui.notify(
            f"task {name} finished ({proc.returncode})",
            type="positive" if ok else "negative",
        )

    def save() -> None:
        # push complex (YAML) editors back into the state before writing
        for section, key, editor in complex_editors:
            try:
                section[key] = yaml.safe_load(editor.value) or {}
            except yaml.YAMLError as exc:
                ui.notify(f"YAML error in '{key}': {exc}", type="negative")
                return
        save_config(state, CONFIG_PATH)
        ui.notify(f"Saved {CONFIG_PATH.name}", type="positive")

    def render_config_editors(section: dict) -> None:
        if not section:
            ui.label("No settings for this tool yet.").classes("opacity-60 italic")
            return
        for key, value in section.items():
            if isinstance(value, bool):
                ui.switch(key).bind_value(section, key)
            elif isinstance(value, (int, float)):
                ui.number(label=key).bind_value(section, key).classes("w-72")
            elif isinstance(value, str):
                ui.input(label=key).bind_value(section, key).classes("w-full")
            else:  # dict / list -> editable YAML block
                ui.label(key).classes("font-medium mt-2")
                editor = ui.textarea(
                    value=yaml.safe_dump(value, sort_keys=False, allow_unicode=True)
                ).classes("w-full font-mono text-xs")
                complex_editors.append((section, key, editor))

    with ui.tabs().classes("w-full") as tabs:
        tab_refs = {name: ui.tab(name.capitalize()) for name in tool_names}

    with ui.tab_panels(tabs, value=tab_refs[tool_names[0]]).classes("w-full"):
        for name in tool_names:
            with ui.tab_panel(tab_refs[name]):
                section = state.setdefault(name if name != "general" else "townhall", {}) or {}

                with ui.card().classes("w-full"):
                    ui.label("Actions").classes("text-lg font-semibold")
                    with ui.row().classes("flex-wrap gap-2"):
                        group_buttons: list[TaskButton] = groups.get(name, [])
                        if not group_buttons:
                            ui.label("No tasks for this tool.").classes("opacity-60 italic")
                        for button in group_buttons:
                            ui.button(
                                button.action,
                                on_click=lambda b=button: run_task(b.name),
                            ).props("no-caps").tooltip(button.desc or button.name)

                with ui.expansion("Settings", icon="settings", value=False) \
                        .classes("w-full border rounded") \
                        .props('header-class="text-lg font-semibold"'):
                    render_config_editors(section)
                    ui.button("Save", on_click=save, icon="save").props("outline")



@ui.page("/")
def _index() -> None:
    """Build a fresh UI for each client (loads config from disk each visit)."""
    _run_ui()


def main() -> None:
    config = load_config(CONFIG_PATH if CONFIG_PATH.is_file() else None).get("town", {}) or {}
    ui.run(
        host=config.get("host", "127.0.0.1"),
        port=int(config.get("port", 8080)),
        title=str(config.get("title", "GrimmCraft")),
        reload=False,
        show=True,
    )


# NiceGUI needs the UI defined at import time when launched via `ui.run` in the
# same module; calling main() from the `town` script entry point does that.
if __name__ in {"__main__", "__mp_main__"}:
    main()
