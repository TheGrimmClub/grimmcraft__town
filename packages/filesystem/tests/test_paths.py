"""Tests for filesystem.paths."""

from __future__ import annotations

from pathlib import Path

from filesystem import paths


def test_is_junk_detects_macos_clutter():
    assert paths.is_junk("world/__MACOSX/foo")
    assert paths.is_junk("world/.DS_Store")
    assert not paths.is_junk("world/level.dat")


def test_ensure_dir_creates_nested(tmp_path: Path):
    target = tmp_path / "a" / "b" / "c"
    result = paths.ensure_dir(target)
    assert result.is_dir()
    assert result == target


def test_locate_world_when_root_is_world(tmp_world: Path):
    assert paths.locate_world(tmp_world) == tmp_world


def test_locate_world_when_nested(tmp_path: Path, tmp_world: Path):
    # tmp_world lives at tmp_path/world; searching from tmp_path should find it
    assert paths.locate_world(tmp_world.parent) == tmp_world


def test_locate_world_missing(tmp_path: Path):
    assert paths.locate_world(tmp_path / "nope") is None
