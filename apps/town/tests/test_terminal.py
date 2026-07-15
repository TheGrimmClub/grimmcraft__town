"""Tests for town.terminal (the reusable log widget's pure helpers)."""

from __future__ import annotations

from town.terminal import DEFAULT_PALETTE, classify


def test_classify_errors():
    assert classify("Traceback (most recent call last):") == "error"
    assert classify("guard: backup FAILED") == "error"
    assert classify("some Exception happened") == "error"


def test_classify_warnings():
    assert classify("DeprecationWarning: asyncore is deprecated") == "warn"
    assert classify("task: [guard:backup] uv run guard backup") == "warn"
    assert classify("[exit 0]") == "warn"


def test_classify_plain_output():
    assert classify("Backed up 'world' (mc 1.21.11)") == "info"
    assert classify("") == "info"


def test_default_palette_covers_every_kind():
    # push() falls back to palette["info"], and classify only returns these
    for kind in ("prompt", "info", "good", "warn", "error"):
        assert kind in DEFAULT_PALETTE
