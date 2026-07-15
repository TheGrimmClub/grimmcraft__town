"""Tests for filesystem.config."""

from __future__ import annotations

from pathlib import Path

from filesystem import config


def test_load_defaults_when_missing(tmp_path: Path):
    cfg = config.load_config(tmp_path / "does-not-exist.yaml")
    assert cfg["guard"]["world_dir"] == "./_input"


def test_save_and_load_roundtrip(tmp_path: Path):
    path = tmp_path / "config.yaml"
    data = {"guard": {"world_dir": "./here", "write_docs": False}, "town": {"port": 9000}}
    config.save_config(data, path)
    assert path.is_file()
    loaded = config.load_config(path)
    assert loaded == data


def test_find_config_walks_up(tmp_path: Path):
    (tmp_path / "config.yaml").write_text("guard: {}\n", encoding="utf-8")
    deep = tmp_path / "a" / "b"
    deep.mkdir(parents=True)
    assert config.find_config(deep) == tmp_path / "config.yaml"
