"""A small, colorful terminal panel for NiceGUI.

Extracted from :mod:`town.app` so the widget is easy to read and reuse. It wraps
a scrollable, monospaced log whose lines are colored by *kind* (prompt, output,
warning, error, exit status), with a live AND/OR filter box and a Clear button.

Colors come from :data:`DEFAULT_PALETTE`; pass ``palette`` to override any of the
kinds (town reads one from ``config.yaml``'s ``town.terminal`` section). Use
:func:`classify` to pick a kind for a line of streamed command output.
"""

from __future__ import annotations

from nicegui import ui

# kind -> Tailwind/Quasar text-color class
DEFAULT_PALETTE: dict[str, str] = {
    "prompt": "text-cyan-300",
    "info": "text-slate-200",
    "good": "text-green-400",
    "warn": "text-amber-300",
    "error": "text-red-400",
}


def classify(line: str) -> str:
    """Pick a color *kind* for a line of streamed command output."""
    low = line.lower()
    if any(w in low for w in ("error", "traceback", "exception", "failed", "fatal")):
        return "error"
    if any(w in low for w in ("warning", "deprecat")):
        return "warn"
    if low.startswith("task:") or line.startswith("["):
        return "warn"
    return "info"


def parse_filter(query: str) -> list[list[str]]:
    """Parse a filter query into AND-groups of OR-alternatives.

    Space-separated terms are AND-ed; ``|`` inside a term separates OR
    alternatives. ``"error|warn task"`` becomes ``[["error", "warn"], ["task"]]``:
    a line matches when it contains ("error" or "warn") and "task".
    Matching is case-insensitive; empty terms are dropped.
    """
    groups: list[list[str]] = []
    for part in query.lower().split():
        alts = [alt for alt in part.split("|") if alt]
        if alts:
            groups.append(alts)
    return groups


def matches_filter(text: str, groups: list[list[str]]) -> bool:
    """True when ``text`` satisfies every AND-group (any alternative per group)."""
    low = text.lower()
    return all(any(alt in low for alt in group) for group in groups)


class Terminal:
    """A scrollable, colorful log panel with a filter box and a Clear button.

    NiceGUI's ``ui.log`` paints every line the same color; this keeps the black,
    monospaced terminal feel but colors each line by *kind* and lets the user
    wipe it with one click. Build it inside a page, then :meth:`push` lines.

    The filter box supports AND/OR: space-separated terms must all match,
    ``|`` inside a term offers alternatives (see :func:`parse_filter`).
    Filtering hides lines rather than dropping them, so clearing the box
    brings everything back.
    """

    def __init__(self, max_lines: int = 500, palette: dict[str, str] | None = None) -> None:
        self._max_lines: int = max_lines
        # merge over the defaults so a partial override can't drop a kind
        self._palette: dict[str, str] = {**DEFAULT_PALETTE, **(palette or {})}
        self._lines: list[ui.label] = []
        self._filter_groups: list[list[str]] = []

        with ui.card().classes("w-full p-0 gap-0 overflow-hidden bg-black"):
            with ui.row().classes("w-full items-center justify-between px-3 py-1 bg-gray-900"):
                _ = ui.label("Terminal").classes("text-xs font-mono text-gray-400")
                self._filter_input: ui.input = (
                    ui.input(placeholder="filter  (space = AND, | = OR)", on_change=self._on_filter_change)
                    .props("dense borderless clearable dark input-class=text-xs input-class=font-mono")
                    .classes("grow max-w-md px-2")
                )
                _ = ui.button("Clear", icon="delete_sweep", on_click=self.clear) \
                      .props("flat dense no-caps color=grey-5")
            self._scroll: ui.scroll_area = ui.scroll_area().classes("w-full h-64 bg-black px-3 py-2")
            with self._scroll:
                self._body: ui.column = ui.column().classes("gap-0 font-mono text-xs")

    def push(self, text: str, kind: str = "info") -> None:
        """Append a line, colored by ``kind`` (see :data:`DEFAULT_PALETTE`)."""
        color = self._palette.get(kind, self._palette["info"])
        with self._body:
            label = ui.label(text).classes(f"{color} whitespace-pre-wrap leading-snug")
        label.set_visibility(matches_filter(text, self._filter_groups))
        self._lines.append(label)
        while len(self._lines) > self._max_lines:
            self._body.remove(self._lines.pop(0))
        self._scroll.scroll_to(percent=1.0)

    def clear(self) -> None:
        """Wipe every line from the panel."""
        _ = self._body.clear()
        self._lines.clear()

    def _on_filter_change(self, e) -> None:
        # Quasar's clearable sends None when the X is clicked
        self._filter_groups = parse_filter(e.value or "")
        for label in self._lines:
            label.set_visibility(matches_filter(label.text, self._filter_groups))
