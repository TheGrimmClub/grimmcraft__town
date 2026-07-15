"""Tests for filesystem.world (reading world info + datapacks)."""

from __future__ import annotations

from pathlib import Path

import pytest

from filesystem.world import discover_datapacks, read_world_info


def test_read_world_info(sample_world: Path):
    info = read_world_info(sample_world)
    assert info.name == "world"
    assert info.version == "1.21.11"
    assert info.data_version is not None
    names = {p.name for p in info.datapacks}
    assert "falron" in names


def test_datapack_description_and_enabled(sample_world: Path):
    packs = {p.name: p for p in discover_datapacks(sample_world)}
    assert packs["falron"].description == "Falron the Eye of the Storm"
    # with no explicit enabled-set, packs default to enabled
    assert packs["falron"].enabled is True


def test_read_world_info_without_level_dat(tmp_path: Path):
    (tmp_path / "empty").mkdir()
    with pytest.raises(FileNotFoundError):
        read_world_info(tmp_path / "empty")


def test_discover_datapacks_none(tmp_path: Path):
    (tmp_path / "world").mkdir()
    assert discover_datapacks(tmp_path / "world") == []
