"""A tiny, dependency-free reader for Minecraft's NBT format.

NBT ("Named Binary Tag") is how Minecraft stores ``level.dat`` and much of a
world's data. This is a *reader* only — enough to pull facts like the world
name and version out of ``level.dat`` without pulling in a third-party
library. Files are usually gzip-compressed; we detect and handle that.

Reference: https://minecraft.wiki/w/NBT_format
"""

from __future__ import annotations

import gzip
import struct
import zlib
from pathlib import Path

# Tag ids from the NBT spec.
TAG_END = 0
TAG_BYTE = 1
TAG_SHORT = 2
TAG_INT = 3
TAG_LONG = 4
TAG_FLOAT = 5
TAG_DOUBLE = 6
TAG_BYTE_ARRAY = 7
TAG_STRING = 8
TAG_LIST = 9
TAG_COMPOUND = 10
TAG_INT_ARRAY = 11
TAG_LONG_ARRAY = 12


class _Reader:
    """A little cursor over the raw bytes, reading big-endian values."""

    def __init__(self, data: bytes) -> None:
        self.data = data
        self.pos = 0

    def take(self, count: int) -> bytes:
        chunk = self.data[self.pos : self.pos + count]
        if len(chunk) != count:
            raise EOFError("Unexpected end of NBT data")
        self.pos += count
        return chunk

    def u1(self) -> int:
        return self.take(1)[0]

    def _unpack(self, fmt: str, size: int):
        return struct.unpack(fmt, self.take(size))[0]

    def string(self) -> str:
        length = self._unpack(">H", 2)
        return self.take(length).decode("utf-8", "replace")


def _read_payload(reader: _Reader, tag: int):
    if tag == TAG_BYTE:
        return reader._unpack(">b", 1)
    if tag == TAG_SHORT:
        return reader._unpack(">h", 2)
    if tag == TAG_INT:
        return reader._unpack(">i", 4)
    if tag == TAG_LONG:
        return reader._unpack(">q", 8)
    if tag == TAG_FLOAT:
        return reader._unpack(">f", 4)
    if tag == TAG_DOUBLE:
        return reader._unpack(">d", 8)
    if tag == TAG_BYTE_ARRAY:
        length = reader._unpack(">i", 4)
        return list(reader.take(length))
    if tag == TAG_STRING:
        return reader.string()
    if tag == TAG_LIST:
        item_tag = reader.u1()
        length = reader._unpack(">i", 4)
        return [_read_payload(reader, item_tag) for _ in range(length)]
    if tag == TAG_COMPOUND:
        out: dict = {}
        while True:
            child_tag = reader.u1()
            if child_tag == TAG_END:
                break
            name = reader.string()
            out[name] = _read_payload(reader, child_tag)
        return out
    if tag == TAG_INT_ARRAY:
        length = reader._unpack(">i", 4)
        return [reader._unpack(">i", 4) for _ in range(length)]
    if tag == TAG_LONG_ARRAY:
        length = reader._unpack(">i", 4)
        return [reader._unpack(">q", 8) for _ in range(length)]
    raise ValueError(f"Unknown NBT tag id: {tag}")


def _decompress(raw: bytes) -> bytes:
    if raw[:2] == b"\x1f\x8b":  # gzip magic number
        return gzip.decompress(raw)
    if raw[:1] == b"\x78":  # zlib header
        try:
            return zlib.decompress(raw)
        except zlib.error:
            pass
    return raw


def parse(raw: bytes) -> dict:
    """Parse raw NBT bytes (gzip/zlib auto-detected) into a plain dict."""
    reader = _Reader(_decompress(raw))
    root_tag = reader.u1()
    if root_tag == TAG_END:
        return {}
    reader.string()  # root name (usually empty) — skip it
    payload = _read_payload(reader, root_tag)
    return payload if isinstance(payload, dict) else {"": payload}


def load(path: str | Path) -> dict:
    """Read and parse an NBT file (e.g. ``level.dat``)."""
    return parse(Path(path).read_bytes())
