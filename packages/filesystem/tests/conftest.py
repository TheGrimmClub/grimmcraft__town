"""Shared fixtures for the filesystem test suite."""

from filesystem.core import SystemPath

import pytest

DATA = SystemPath(__file__).parent / "data"


@pytest.fixture
def tmp_world(tmp_path: SystemPath) -> SystemPath:
    """A throwaway world folder with a couple of files and a nested datapack."""
    world = tmp_path / "world"
    (world / "region").mkdir(parents=True)
    (world / "level.dat").write_bytes(b"not-real-nbt")
    (world / "region" / "r.0.0.mca").write_bytes(b"chunkdata")
    (world / ".DS_Store").write_bytes(b"junk")
    return world
