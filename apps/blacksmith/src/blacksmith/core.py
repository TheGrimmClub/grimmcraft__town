"""Blacksmith's forge — stamp out a fireworks datapack's ``.mcfunction`` files.

A fireworks show is wonderfully repetitive: the same ``summon firework_rocket``
command, repeated across a matrix of colours and explosion shapes. Rather than
hand-write (and mistype) a hundred near-identical files, the forge presses them
all from one small palette so every rocket comes out consistent.

The layout it produces matches the ``_templates/datapack__fireworks`` example::

    datapacks/<name>/
        pack.mcmeta
        data/<namespace>/function/
            rocket_<colour>_<shape>.mcfunction   # one summon, run by hand
            timer_<colour>_<shape>.mcfunction     # a timed volley
            load.mcfunction  tick.mcfunction  sheep.mcfunction
        data/minecraft/tags/function/
            load.json  tick.json
"""

from __future__ import annotations

import json
from dataclasses import dataclass, field
from pathlib import Path

from filesystem.paths import as_path, ensure_dir

# Friendly shape name -> Minecraft firework explosion shape.
SHAPES: dict[str, str] = {
    "ball": "small_ball",
    "burst": "burst",
    "creeper": "creeper",
    "sparkler": "sparkler",
    "star": "star",
}

# Colour name -> (primary RGB, fade RGB) as 24-bit integers.
COLORS: dict[str, tuple[int, int]] = {
    "red": (0xB02E26, 0xF9807C),
    "orange": (0xF9801D, 0xFFC182),
    "yellow": (0xFED83D, 0xFFF2A8),
    "green": (0x5E7C16, 0xA6D65F),
    "light_blue": (0x3AB3DA, 0xB5E8F5),
    "blue": (0x3C44AA, 0x8A93E8),
    "cyan": (0x169C9C, 0x7FE3E3),
    "purple": (0x8932B8, 0xD196F0),
    "pink": (0xF38BAA, 0xFFD1DE),
    "white": (0xF9FFFE, 0xFFFFFF),
}

# The countdown ticks at which a timed rocket fires, with a little left/right
# drift so a volley doesn't stack on one spot: (score, x-offset, flight_duration).
TIMER_STEPS: list[tuple[int, int, int]] = [
    (90, 5, 2),
    (70, 10, 1),
    (50, -5, 2),
    (30, -10, 1),
    (10, 0, 1),
]

# pack.mcmeta format numbers — kept in step with the 1.21.11 scaffold template.
PACK_FORMAT_MIN = [94, 1]
PACK_FORMAT_MAX = 94


@dataclass
class ForgeResult:
    """What a forge run produced, for the CLI to report back."""

    datapack: Path
    timers: list[str] = field(default_factory=list)  # timer function ids
    files_written: int = 0


def _rel(offset: int) -> str:
    """A relative coordinate: ``~`` for zero, ``~5`` / ``~-5`` otherwise."""
    return "~" if offset == 0 else f"~{offset}"


def rocket_command(
    shape: str,
    primary: int,
    fade: int,
    *,
    flight: int = 1,
    twinkle: int = 0,
    trail: int = 0,
    pos: str = "~ ~1 ~",
) -> str:
    """One ``summon firework_rocket`` command for a shape and colour pair."""
    explosion = (
        f'{{shape:"{shape}",has_twinkle:{twinkle},has_trail:{trail},'
        f"colors:[I;{primary}],fade_colors:[I;{fade}]}}"
    )
    return (
        f"summon firework_rocket {pos} {{LifeTime:45,"
        f"FireworksItem:{{id:firework_rocket,count:1,components:{{fireworks:{{"
        f"flight_duration:{flight},explosions:[{explosion}]}}}}}}}}"
    )


def timer_function(shape: str, primary: int, fade: int, *, twinkle: int = 0, trail: int = 0) -> str:
    """A timed volley: fire the same rocket at each :data:`TIMER_STEPS` score."""
    lines = []
    for score, dx, flight in TIMER_STEPS:
        cmd = rocket_command(
            shape, primary, fade, flight=flight, twinkle=twinkle, trail=trail,
            pos=f"{_rel(dx)} ~2 ~",
        )
        lines.append(f"execute if score timer Feuerwerk matches {score} run {cmd}")
    return "\n".join(lines) + "\n"


def _variant_flags(variant: int) -> tuple[int, int, int]:
    """(flight, twinkle, trail) that make numbered variants look distinct."""
    flight = 1 + (variant % 2)
    return flight, (1 if variant >= 2 else 0), (1 if variant >= 3 else 0)


def _variant_labels(count: int) -> list[int]:
    """``[0]`` (unnumbered) for a single variant, else ``[1, 2, ...]``."""
    return [0] if count <= 1 else list(range(1, count + 1))


def _pack_mcmeta(description: str) -> str:
    meta = {
        "pack": {
            "description": description,
            "min_format": PACK_FORMAT_MIN,
            "max_format": PACK_FORMAT_MAX,
        }
    }
    return json.dumps(meta, indent=2) + "\n"


def _tag_json(values: list[str]) -> str:
    return json.dumps({"values": values}, indent=2) + "\n"


def _load_function() -> str:
    return (
        'tellraw @a ["",{"text":"Loading Fireworks...","color":"green"}]\n'
        "scoreboard objectives add Feuerwerk dummy\n"
        "scoreboard players set timer Feuerwerk 100\n"
        "scoreboard objectives setdisplay sidebar Feuerwerk\n"
        'tellraw @a ["",{"text":"done","color":"green"}]\n'
    )


def _tick_function(timer_ids: list[str]) -> str:
    lines = [
        "scoreboard players remove timer Feuerwerk 1",
        "execute if score timer Feuerwerk matches 0 run scoreboard players set timer Feuerwerk 100",
    ]
    lines += [f"function {tid}" for tid in timer_ids]
    return "\n".join(lines) + "\n"


def _sheep_function() -> str:
    rows = [f"summon sheep {_rel(dx)} ~20 {_rel(dz)}" for dz in (5, 0, -5) for dx in (5, 0, -5)]
    return "\n".join(rows) + "\n"


def _write(path: Path, text: str, written: list[Path]) -> None:
    path.write_text(text, encoding="utf-8")
    written.append(path)


def forge_fireworks(
    world_dir: str | Path,
    *,
    name: str = "fireworks",
    namespace: str | None = None,
    description: str = "Fireworks — forged by blacksmith",
    colors: list[str] | None = None,
    shapes: list[str] | None = None,
    variants: int = 1,
    force: bool = False,
) -> ForgeResult:
    """Generate the fireworks datapack under ``world_dir/datapacks/<name>``.

    ``colors`` / ``shapes`` default to the full :data:`COLORS` / :data:`SHAPES`
    palettes and may be narrowed to a subset. ``variants`` (>= 1) stamps that
    many numbered rockets per colour/shape, each nudged to look different.
    """
    namespace = namespace or name
    colors = list(colors) if colors else list(COLORS)
    shapes = list(shapes) if shapes else list(SHAPES)

    unknown_c = [c for c in colors if c not in COLORS]
    unknown_s = [s for s in shapes if s not in SHAPES]
    if unknown_c:
        raise ValueError(f"unknown colour(s): {', '.join(unknown_c)}")
    if unknown_s:
        raise ValueError(f"unknown shape(s): {', '.join(unknown_s)}")
    if variants < 1:
        raise ValueError("variants must be at least 1")

    pack = as_path(world_dir) / "datapacks" / name
    if pack.exists() and not force:
        raise FileExistsError(f"{pack} already exists — pass force=True to overwrite")

    func_dir = pack / "data" / namespace / "function"
    tag_dir = pack / "data" / "minecraft" / "tags" / "function"
    ensure_dir(func_dir)
    ensure_dir(tag_dir)

    written: list[Path] = []
    timer_ids: list[str] = []

    _write(pack / "pack.mcmeta", _pack_mcmeta(description), written)

    for color in colors:
        primary, fade = COLORS[color]
        for shape in shapes:
            mc_shape = SHAPES[shape]
            for variant in _variant_labels(variants):
                flight, twinkle, trail = _variant_flags(variant or 1)
                suffix = f"_{variant}" if variant else ""
                base = f"{color}_{shape}{suffix}"
                _write(
                    func_dir / f"rocket_{base}.mcfunction",
                    rocket_command(mc_shape, primary, fade, flight=flight, twinkle=twinkle, trail=trail) + "\n",
                    written,
                )
                _write(
                    func_dir / f"timer_{base}.mcfunction",
                    timer_function(mc_shape, primary, fade, twinkle=twinkle, trail=trail),
                    written,
                )
                timer_ids.append(f"{namespace}:timer_{base}")

    _write(func_dir / "load.mcfunction", _load_function(), written)
    _write(func_dir / "tick.mcfunction", _tick_function(timer_ids), written)
    _write(func_dir / "sheep.mcfunction", _sheep_function(), written)

    _write(tag_dir / "load.json", _tag_json([f"{namespace}:load"]), written)
    _write(tag_dir / "tick.json", _tag_json([f"{namespace}:tick"]), written)

    return ForgeResult(datapack=pack, timers=timer_ids, files_written=len(written))
