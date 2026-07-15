"""Tests for scout.core / scout.report (region reading is mocked out)."""

from __future__ import annotations

from pathlib import Path

import pytest

from minecraft.world import WorldInfo
from scout import core, report

FAKE_ENTITIES = [
    ("overworld", {"id": "minecraft:command_block", "x": 1, "y": 2, "z": 3,
                   "Command": "say hi", "auto": 1}),
    ("overworld", {"id": "minecraft:chest", "x": 0, "y": 0, "z": 0}),
    ("the_end", {"id": "minecraft:repeating_command_block", "x": 5, "y": 6, "z": 7,
                 "Command": "time set day"}),
]


@pytest.fixture
def fake_world(tmp_path: Path, monkeypatch) -> Path:
    world = tmp_path / "world"
    world.mkdir()
    (world / "level.dat").write_bytes(b"")  # locate_directory only checks existence
    monkeypatch.setattr(core, "read_world_info",
                        lambda w: WorldInfo(Path(w), "world", "1.21.11", 42, []))
    monkeypatch.setattr(core.region, "iter_block_entities", lambda w: iter(FAKE_ENTITIES))
    return world


def test_scan_world_aggregates(fake_world: Path):
    scan = core.scan_world(fake_world)
    assert scan.info.name == "world"
    assert scan.total_block_entities == 3
    assert scan.block_entity_counts["minecraft:command_block"] == 1
    assert len(scan.command_blocks) == 2  # command_block + repeating_command_block


def test_command_block_fields(fake_world: Path):
    scan = core.scan_world(fake_world)
    first = scan.command_blocks[0]
    assert first.command == "say hi"
    assert first.auto is True
    assert first.coords == "1 2 3"
    assert first.dimension == "overworld"


def test_report_to_dict_and_markdown(fake_world: Path):
    scan = core.scan_world(fake_world)
    data = report.to_dict(scan)
    assert data["command_blocks"][0]["command"] == "say hi"
    assert data["block_entities"]["total"] == 3

    md = report.render_markdown(scan)
    assert "# Scout report: world" in md
    assert "time set day" in md
