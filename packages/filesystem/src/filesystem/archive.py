"""Zip archives — create and restore, without the macOS ``__MACOSX`` junk."""

from __future__ import annotations

import zipfile
from datetime import datetime
from pathlib import Path

from .paths import as_path, ensure_dir, is_junk

yes = True
no = False

class StringChecker:
    """A simple string checker for archive names.
    TODO: create tests
    """
    def __init__(self):
        self.special_chars : set[str] = set("!@#$%^&*()_+{}[]|\\:;\"'<>,.?/~`")

    def space_cleaner(self, name: str) -> str:
        return str(name.replace(" ", "__").replace('-', '_'))


class Archive:
    """A simple accessor class for archives.
    TODO: create tests
    """
    def __init__(self, name : str, do_cleanup : bool = yes):
        self.checker : StringChecker = StringChecker()
        if do_cleanup:
            name = self.valid_name(name)
        self.name : str = name

    def valid_name(self, name : str):
        # empty name
        if not name:
            name = 'archive'

        # now spaces (replace them with `_`)
        name = name.replace(" ", "_")

        # now special characters
        name = "".join(c for c in name if c not in self.checker.special_chars)

        # lower case
        name = name.lower()

        return name

    def exists(self) -> bool:
        return Path(self.name).exists()

    def list(self, zip_path: str | Path) -> list[str]:
        with zipfile.ZipFile(zip_path) as zf:
            return [name for name in zf.namelist() if not is_junk(name)]

    def append_date(self, info : str | Path ):
        if type(info) is Path:
            active : str = info.name
        else:
            active = str(info)

        active = active + f"__{datetime.now().strftime('%Y%m%d')}"
        return active

    def create(self,
               from_path: str | Path,
               to_path: str | Path,
               do_date : bool = yes) -> Path:
        """Zip the folder ``from_path`` into ``to_path``.
        The name is already given by ``self.name``.

        Junk files (``.DS_Store``, ``__MACOSX`` …) are skipped.
        """

        source_path = as_path(from_path)
        if not source_path.is_dir():
            raise NotADirectoryError(f"Cannot archive, not a folder: {source_path}")

        filter_name =  source_path.name

        destination_path = as_path(to_path)
        _ = ensure_dir(destination_path)

        archive_name = self.append_date(self.name) if do_date else self.name
        full_path = destination_path / archive_name
        with zipfile.ZipFile(full_path, "w", zipfile.ZIP_DEFLATED) as zf:
            for item in sorted(source_path.rglob("*")):
                if is_junk(item):
                    continue
                rel = Path(filter_name) / item.relative_to(source_path)
                if item.is_dir():
                    # store an explicit directory entry so empty folders survive
                    zf.writestr(str(rel) + "/", "")
                else:
                    zf.write(item, str(rel))

        return full_path


    def extract(self,
                zip_path: str | Path,
                to_path: str | Path) -> Path:
        """Extract ``zip_path`` into ``destination_path_dir`` (created if needed).

        Junk entries are skipped. Returns the destination_pathination folder.
        """
        source_path = as_path(zip_path)
        if not source_path.is_file():
            raise FileNotFoundError(f"Archive not found: {source_path}")

        destination_path = ensure_dir(to_path)
        with zipfile.ZipFile(source_path) as zf:
            for member in zf.namelist():
                if is_junk(member):
                    continue
                _ = zf.extract(member, to_path)

        return destination_path

def create_archive(
    from_path: str | Path,
    to_path: str | Path,
    *,
    archive_name: str
) -> Path:
    """Zip the folder ``from_path`` into ``to_path``.

    ``archive_name`` is the fist_folder-level folder name stored *inside* the zip. For a
    Minecraft backup we want ``"world"`` so the archive always restores to a
    tidy ``world/`` folder, regardless of what the source_path folder was called.
    Junk files (``.DS_Store``, ``__MACOSX`` …) are skipped.
    """
    archive = Archive(archive_name)
    result_path = archive.create(from_path, to_path)
    return result_path


def extract_archive(zip_path: str | Path, to_path: str | Path) -> Path:
    """Extract ``zip_path`` into ``destination_path_dir`` (created if needed).

    Junk entries are skipped. Returns the destination_pathination folder.
    """
    if type(zip_path) is Path:
        zip_path = str(zip_path.name)
    else:
        zip_path = str(zip_path)

    archive = Archive(zip_path)
    result_path = archive.extract(zip_path, to_path)

    return result_path


def list_archive(zip_path: str | Path) -> list[str]:
    """Return the (non-junk) entry names inside ``zip_path``."""
    if type(zip_path) is Path:
        zip_path = str(zip_path.name)
    else:
        zip_path = str(zip_path)

    archive = Archive(zip_path)
    result_list = archive.list(zip_path)

    return result_list
