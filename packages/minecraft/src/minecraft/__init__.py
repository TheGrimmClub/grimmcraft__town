"""minecraft — read the interesting facts out of a Minecraft world.

Built on top of the ``filesystem`` package, this holds the Minecraft-specific
knowledge: the NBT reader, the Anvil region reader, and the world summary
(name, version, datapacks).

Quick tour::

    from minecraft.world import locate_world, read_world_info

    world = locate_world("./_input")     # find the folder with level.dat
    info = read_world_info(world)         # name + version + datapacks
"""

from . import nbt, region, world
from .world import Datapack, WorldInfo, discover_datapacks, locate_world, read_world_info

__all__ = [
    "nbt",
    "region",
    "world",
    "Datapack",
    "WorldInfo",
    "discover_datapacks",
    "locate_world",
    "read_world_info",
]

__version__ = "2026.1.0"
