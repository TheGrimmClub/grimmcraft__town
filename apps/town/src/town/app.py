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

ROOT = find_repo_root()
CONFIG_PATH = ROOT / CONFIG_NAME


def _run_ui() -> None:
    state: dict = load_config(CONFIG_PATH if CONFIG_PATH.is_file() else None)
    buttons = list_tasks(ROOT)
    groups = group_tasks(buttons)
    # keep tool tabs first and in a friendly order
    order = ["guard", "scout", "blacksmith", "townhall", "general"]
    tool_names = sorted(groups, key=lambda g: (order.index(g) if g in order else 99, g))

    complex_editors: list[tuple[dict, str, "ui.textarea"]] = []

    ui.colors(primary="#5b7c99")
    with ui.header().classes("items-center justify-between"):
        with ui.column():
            ui.label("⚒  GrimCraft · Town").classes("text-xl font-bold")
            with ui.row():
                with ui.card():
                    # open the folder
                    ui.link(str(ROOT), str(ROOT)).classes("text-l")

                with ui.card():
                    ui.link('GrimmCraft Town on GitHub', 'https://github.com/TheGrimmClub/grimmcraft__town', new_tab=True)
                with ui.card():
                    ui.link('Grimmoire', 'https://thegrimmclub.github.io/grimmoire/', new_tab=True)
                with ui.card():
                        ui.link('Aternos Coding', 'https://aternos.org/worlds/', new_tab=True)
                with ui.card():
                        ui.link('NiceGUI', 'https://nicegui.io/documentation', new_tab=True)



    # Shared log, shown under the tabs.
    log = ui.log(max_lines=500).classes("w-full h-64 bg-black text-green-400 font-mono text-xs")

    async def run_task(name: str) -> None:
        log.push(f"$ task {name}")
        proc = await asyncio.create_subprocess_exec(
            "task", name,
            cwd=str(ROOT),
            stdout=asyncio.subprocess.PIPE,
            stderr=asyncio.subprocess.STDOUT,
        )
        assert proc.stdout is not None
        async for raw in proc.stdout:
            log.push(raw.decode(errors="replace").rstrip())
        await proc.wait()
        log.push(f"[exit {proc.returncode}]")
        (ui.notify if proc.returncode == 0 else ui.notify)(
            f"task {name} finished ({proc.returncode})",
            type="positive" if proc.returncode == 0 else "negative",
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

                with ui.card().classes("w-full"):
                    ui.label("Settings").classes("text-lg font-semibold")
                    render_config_editors(section)
                    ui.button("Save", on_click=save, icon="save").props("outline")



@ui.page("/")
def _index() -> None:
    """Build a fresh UI for each client (loads config from disk each visit)."""
    _run_ui()


def main() -> None:
    cfg = load_config(CONFIG_PATH if CONFIG_PATH.is_file() else None).get("town", {}) or {}
    ui.run(
        host=cfg.get("host", "127.0.0.1"),
        port=int(cfg.get("port", 8080)),
        title="GrimmCraft · Town",
        reload=False,
        show=True,
    )


# NiceGUI needs the UI defined at import time when launched via `ui.run` in the
# same module; calling main() from the `town` script entry point does that.
if __name__ in {"__main__", "__mp_main__"}:
    main()
