"""Scout's core: scan a world and pull out the interesting data."""

from __future__ import annotations

from collections import Counter
from dataclasses import dataclass, field
from pathlib import Path

from filesystem import paths
from minecraft import region
from minecraft.world import WorldInfo, read_world_info


@dataclass
class CommandBlock:
    """One command block found in the world."""

    dimension: str
    x: int
    y: int
    z: int
    command: str
    name: str | None = None
    auto: bool = False           # "Always Active" (no redstone needed)
    track_output: bool = True

    @property
    def coords(self) -> str:
        return f"{self.x} {self.y} {self.z}"


@dataclass
class WorldScan:
    """Everything scout learned about a world in one pass."""

    world: Path
    info: WorldInfo
    command_blocks: list[CommandBlock] = field(default_factory=list)
    block_entity_counts: dict[str, int] = field(default_factory=dict)

    @property
    def total_block_entities(self) -> int:
        return sum(self.block_entity_counts.values())


def _is_command_block(block_id: str) -> bool:
    # covers command_block, chain_command_block, repeating_command_block
    return block_id.lower().endswith("command_block")


def _custom_name(raw) -> str | None:
    if raw is None:
        return None
    if isinstance(raw, dict):
        return str(raw.get("text", raw))
    return str(raw)


def scan_world(world_dir: str | Path) -> WorldScan:
    """Read level.dat + every region file in a single pass."""
    world = paths.locate_directory(world_dir)
    if world is None:
        raise FileNotFoundError(f"No Minecraft world (level.dat) found under {world_dir}")

    scan = WorldScan(world=world, info=read_world_info(world))
    counts: Counter[str] = Counter()

    for dimension, entity in region.iter_block_entities(world):
        block_id = str(entity.get("id", "unknown"))
        counts[block_id] += 1
        if _is_command_block(block_id):
            scan.command_blocks.append(
                CommandBlock(
                    dimension=dimension,
                    x=int(entity.get("x", 0)),
                    y=int(entity.get("y", 0)),
                    z=int(entity.get("z", 0)),
                    command=str(entity.get("Command", "")),
                    name=_custom_name(entity.get("CustomName")),
                    auto=bool(entity.get("auto", 0)),
                    track_output=bool(entity.get("TrackOutput", 1)),
                )
            )

    scan.block_entity_counts = dict(counts.most_common())
    return scan
