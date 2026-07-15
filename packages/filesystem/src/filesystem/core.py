
# [ ] Includes standard
from __future__ import annotations

from datetime import datetime as DateTime
from os import path
from pathlib import Path as SystemPath       # pyright: ignore[reportUnusedImport]
from typing import Any                       # pyright: ignore[reportUnusedImport]
from zipfile import ZipFile, ZIP_DEFLATED    # pyright: ignore[reportUnusedImport]

# [ ] Types
path_like = str | SystemPath
path_like_optional = path_like | None
SystemPathOptional = SystemPath | None
AnyOptional = Any | None

# [ ] Constants
# - Boolean
yes = True
true = True

no = False
false = False

# [ ] Classes
#
class StringChecker:
    """A simple string checker for archive names.
    TODO: create tests
    """
    def __init__(self):
        self.special_chars : set[str] = set("!@#$%^&*()_+{}[]|\\:;\"'<>,.?/~`")

    def space_cleaner(self, name: str) -> str:
        return str(name.replace(" ", "__").replace('-', '_'))


# [ ] Functions
#
def get_iso_time() -> str:
    """wrapper to get the ISO time string (YYYYMMDD_HHMMSS)
    """
    return DateTime.now().strftime('%Y%m%d_%H%M%S')

def get_iso_date() -> str:
    """wrapper to get the ISO date string (YYYYMMDD)
    """
    return DateTime.now().strftime('%Y%m%d')
