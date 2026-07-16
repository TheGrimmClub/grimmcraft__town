"""Read Minecraft's Anvil region files (``r.X.Z.mca``).

A region file packs 32×32 chunks. Its layout:

- 4096-byte *location* table: 1024 entries of ``offset(3 bytes) + sectors(1)``
- 4096-byte *timestamp* table (we ignore it)
- then each chunk at ``offset * 4096``: ``length(4 bytes) + compression(1) + data``

The chunk ``data`` is compressed NBT; :func:`minecraft.nbt.parse` auto-detects
the gzip/zlib compression, so we just hand it the payload. This module is the
low-level reader; higher-level tools (scout, blacksmith) build on it.
"""

from __future__ import annotations

from collections.abc import Iterator
from pathlib import Path

from . import nbt
from filesystem.paths import as_path

SECTOR = 4096

# Region sub-folders per dimension, mapped to friendly names.
DIMENSION_DIRS = {
    "region": "overworld",
    "DIM-1/region": "the_nether",
    "DIM1/region": "the_end",
}


def _chunk_payload(data: bytes, index: int) -> bytes | None:
    """Return the compressed NBT bytes for chunk ``index`` (0..1023), or None."""
    entry = data[index * 4 : index * 4 + 4]
    if len(entry) < 4:
        return None
    offset = int.from_bytes(entry[:3], "big")
    sectors = entry[3]
    if offset == 0 or sectors == 0:
        return None  # chunk not generated
    start = offset * SECTOR
    if start + 5 > len(data):
        return None
    length = int.from_bytes(data[start : start + 4], "big")
    if length <= 1:
        return None
    # length counts the 1 compression-type byte plus the compressed data
    return data[start + 5 : start + 4 + length]


def iter_region_chunks(region_path: str | Path) -> Iterator[dict]:
    """Yield the parsed NBT of every generated chunk in one ``.mca`` file."""
    data = as_path(region_path).read_bytes()
    if len(data) < SECTOR:
        return
    for index in range(1024):
        payload = _chunk_payload(data, index)
        if payload is None:
            continue
        try:
            yield nbt.parse(payload)
        except (ValueError, EOFError, OSError):
            continue  # skip a corrupt chunk rather than fail the whole scan


def chunk_block_entities(chunk: dict) -> list[dict]:
    """Return a chunk's block entities (handles 1.18+ and older layouts)."""
    if "block_entities" in chunk:
        return chunk.get("block_entities") or []
    level = chunk.get("Level") or {}
    return level.get("TileEntities") or []


def chunk_block_state(chunk: dict, x: int, y: int, z: int) -> dict | None:
    """Return the block-state palette entry at absolute world coords.

    The result looks like ``{"Name": "minecraft:chain_command_block",
    "Properties": {"conditional": "true", "facing": "east"}}`` — Properties
    may be absent. Only the 1.18+ chunk layout (``sections``) is supported;
    older chunks return None.

    Block states live in 16x16x16 *sections*: each section has a ``palette``
    of distinct states and a ``data`` long-array of bit-packed palette
    indices (1.16+ packing: indices never span two longs).
    """
    for section in chunk.get("sections") or []:
        if section.get("Y") != y >> 4:
            continue
        states = section.get("block_states") or {}
        palette = states.get("palette") or []
        if not palette:
            return None
        data = states.get("data")
        if len(palette) == 1 or not data:
            return palette[0]  # the whole section is a single block state
        bits = max(4, (len(palette) - 1).bit_length())
        per_long = 64 // bits
        index = (y & 15) * 256 + (z & 15) * 16 + (x & 15)
        if index // per_long >= len(data):
            return None
        packed = data[index // per_long] & 0xFFFFFFFFFFFFFFFF  # signed long -> unsigned
        entry = (packed >> ((index % per_long) * bits)) & ((1 << bits) - 1)
        return palette[entry] if entry < len(palette) else None
    return None


def iter_region_files(world_dir: str | Path) -> Iterator[tuple[str, Path]]:
    """Yield ``(dimension_name, path)`` for every region file in a world."""
    world = as_path(world_dir)
    for rel, dimension in DIMENSION_DIRS.items():
        folder = world / rel
        if folder.is_dir():
            for mca in sorted(folder.glob("*.mca")):
                yield dimension, mca


def iter_block_entities(world_dir: str | Path) -> Iterator[tuple[str, dict]]:
    """Yield ``(dimension_name, block_entity)`` for the whole world."""
    for dimension, path in iter_region_files(world_dir):
        for chunk in iter_region_chunks(path):
            for entity in chunk_block_entities(chunk):
                yield dimension, entity
