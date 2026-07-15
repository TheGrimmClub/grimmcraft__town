"""filesystem — the single, learner-friendly interface to the file world.

Instead of importing ``os``, ``pathlib``, ``zipfile``, ``ftplib`` and
``urllib`` all over the place, the GrimmCraft Town tools import *this* package.
It keeps the "how do I touch files, archives and remote servers" knowledge
in one small, well-documented place.

Quick tour::

    from filesystem import paths, archive, transfer, config
    from filesystem.world import read_world_info

    world = paths.locate_world("./_input")      # find the `world` folder
    info = read_world_info(world)               # name + version + datapacks
    archive.create_archive(world, "out.zip")    # zip it (skips macOS junk)
"""

from . import archive, config, nbt, paths, transfer, world
from .world import WorldInfo, read_world_info

__all__ = [
    "archive",
    "config",
    "nbt",
    "paths",
    "transfer",
    "world",
    "WorldInfo",
    "read_world_info",
]

__version__ = "2026.1.0"
