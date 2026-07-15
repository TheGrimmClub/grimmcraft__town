"""Tests for blacksmith's fireworks forge."""

from __future__ import annotations

import json
from pathlib import Path

import pytest

from blacksmith import core


@pytest.fixture
def world(tmp_path: Path) -> Path:
    """A throwaway world folder for forging into."""
    w = tmp_path / "world"
    w.mkdir()
    (w / "level.dat").write_bytes(b"not-real-nbt")
    return w


def _func_dir(pack: Path, namespace: str = "fireworks") -> Path:
    return pack / "data" / namespace / "function"


def test_rocket_command_shape_and_colors():
    cmd = core.rocket_command("small_ball", 0x25, 0x66, flight=2, twinkle=1, trail=1)
    assert cmd.startswith("summon firework_rocket ~ ~1 ~ ")
    assert 'shape:"small_ball"' in cmd
    assert "colors:[I;37]" in cmd  # 0x25
    assert "fade_colors:[I;102]" in cmd  # 0x66
    assert "flight_duration:2" in cmd
    assert "has_twinkle:1" in cmd and "has_trail:1" in cmd


def test_timer_function_has_one_line_per_step():
    text = core.timer_function("burst", 1, 2)
    lines = text.strip().splitlines()
    assert len(lines) == len(core.TIMER_STEPS)
    assert all(line.startswith("execute if score timer Feuerwerk matches ") for line in lines)
    scores = [core.TIMER_STEPS[0][0], core.TIMER_STEPS[-1][0]]
    assert f"matches {scores[0]} run summon" in lines[0]
    assert f"matches {scores[1]} run summon" in lines[-1]


def test_forge_writes_full_matrix(world: Path):
    result = core.forge_fireworks(world, colors=["blue", "red"], shapes=["ball", "star"])
    fdir = _func_dir(result.datapack)

    # 2 colours x 2 shapes -> a rocket + a timer each, plus load/tick/sheep.
    for color in ("blue", "red"):
        for shape in ("ball", "star"):
            assert (fdir / f"rocket_{color}_{shape}.mcfunction").is_file()
            assert (fdir / f"timer_{color}_{shape}.mcfunction").is_file()
    for fixed in ("load", "tick", "sheep"):
        assert (fdir / f"{fixed}.mcfunction").is_file()

    assert len(result.timers) == 4
    # pack.mcmeta + 4 rockets + 4 timers + load/tick/sheep + 2 tags = 14 files.
    assert result.files_written == 14


def test_tick_dispatches_every_timer(world: Path):
    result = core.forge_fireworks(world, colors=["green"], shapes=["creeper", "burst"])
    tick = (_func_dir(result.datapack) / "tick.mcfunction").read_text()
    assert "scoreboard players remove timer Feuerwerk 1" in tick
    for tid in result.timers:
        assert f"function {tid}" in tick


def test_pack_meta_and_tags_are_valid_json(world: Path):
    result = core.forge_fireworks(world, namespace="pyro", colors=["white"], shapes=["ball"])
    meta = json.loads((result.datapack / "pack.mcmeta").read_text())
    assert meta["pack"]["min_format"] == core.PACK_FORMAT_MIN

    tag_dir = result.datapack / "data" / "minecraft" / "tags" / "function"
    assert json.loads((tag_dir / "load.json").read_text())["values"] == ["pyro:load"]
    assert json.loads((tag_dir / "tick.json").read_text())["values"] == ["pyro:tick"]


def test_variants_produce_numbered_files(world: Path):
    result = core.forge_fireworks(world, colors=["blue"], shapes=["ball"], variants=3)
    fdir = _func_dir(result.datapack)
    for n in (1, 2, 3):
        assert (fdir / f"rocket_blue_ball_{n}.mcfunction").is_file()
    assert not (fdir / "rocket_blue_ball.mcfunction").exists()
    assert len(result.timers) == 3


def test_forge_refuses_existing_without_force(world: Path):
    core.forge_fireworks(world, colors=["blue"], shapes=["ball"])
    with pytest.raises(FileExistsError):
        core.forge_fireworks(world, colors=["blue"], shapes=["ball"])
    # force overwrites cleanly.
    result = core.forge_fireworks(world, colors=["blue"], shapes=["ball"], force=True)
    assert result.datapack.is_dir()


def test_forge_rejects_unknown_palette(world: Path):
    with pytest.raises(ValueError, match="colour"):
        core.forge_fireworks(world, colors=["chartreuse"])
    with pytest.raises(ValueError, match="shape"):
        core.forge_fireworks(world, shapes=["spiral"])
