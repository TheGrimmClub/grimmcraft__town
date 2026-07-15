"""Download data from the internet — a gentle interface to FTP and HTTP(S).

The goal is learnability: one obvious function per idea, friendly names, and
a single :func:`fetch` that reads a small dict so a beginner can describe a
source in YAML instead of remembering library APIs.
"""

from __future__ import annotations

import ftplib
import shutil
import urllib.request
from pathlib import Path
from urllib.parse import urlparse

from .paths import as_path, ensure_dir


def _prepare(dest: str | Path) -> Path:
    dest = as_path(dest)
    ensure_dir(dest.parent)
    return dest


def http_download(url: str, dest: str | Path) -> Path:
    """Download an ``http://`` or ``https://`` URL to ``dest``."""
    dest = _prepare(dest)
    request = urllib.request.Request(url, headers={"User-Agent": "grimm-guard"})
    with urllib.request.urlopen(request) as response, open(dest, "wb") as out:
        shutil.copyfileobj(response, out)
    return dest


def ftp_download(
    host: str,
    remote_path: str,
    dest: str | Path,
    *,
    user: str = "anonymous",
    password: str = "",
    port: int = 21,
) -> Path:
    """Download a single file from an FTP server to ``dest``."""
    dest = _prepare(dest)
    with ftplib.FTP() as ftp:
        ftp.connect(host, port)
        ftp.login(user, password)
        with open(dest, "wb") as out:
            ftp.retrbinary(f"RETR {remote_path}", out.write)
    return dest


def _ftp_from_url(url: str, dest: str | Path) -> Path:
    parts = urlparse(url)
    if not parts.hostname:
        raise ValueError(f"FTP url has no host: {url}")
    return ftp_download(
        parts.hostname,
        parts.path,
        dest,
        user=parts.username or "anonymous",
        password=parts.password or "",
        port=parts.port or 21,
    )


def download(url: str, dest: str | Path) -> Path:
    """Download any supported URL (``http``, ``https`` or ``ftp``) to ``dest``."""
    scheme = urlparse(url).scheme.lower()
    if scheme in ("http", "https"):
        return http_download(url, dest)
    if scheme == "ftp":
        return _ftp_from_url(url, dest)
    raise ValueError(f"Don't know how to download a '{scheme}' url: {url}")


def suggest_filename(url: str, fallback: str = "download.bin") -> str:
    """Guess a sensible filename from the tail of a URL."""
    name = Path(urlparse(url).path).name
    return name or fallback


def fetch(source: dict, dest: str | Path) -> Path:
    """Download from a *source description* (a small dict, e.g. from YAML).

    Supported shapes::

        {kind: http,  url: "https://host/world.zip"}
        {kind: ftp,   url: "ftp://user:pass@host/path/world.zip"}
        {kind: ftp,   host: host, path: /world.zip, user: me, password: pw, port: 21}

    ``kind`` is optional when a ``url`` is given (it is read from the scheme).
    """
    url = source.get("url")
    kind = (source.get("kind") or (urlparse(url).scheme if url else "")).lower()

    if kind in ("http", "https"):
        if not url:
            raise ValueError("http source needs a 'url'")
        return http_download(url, dest)
    if kind == "ftp":
        if url:
            return _ftp_from_url(url, dest)
        return ftp_download(
            source["host"],
            source["path"],
            dest,
            user=source.get("user", "anonymous"),
            password=source.get("password", ""),
            port=int(source.get("port", 21)),
        )
    raise ValueError(f"Unknown source kind: {kind!r} (use 'http', 'https' or 'ftp')")
