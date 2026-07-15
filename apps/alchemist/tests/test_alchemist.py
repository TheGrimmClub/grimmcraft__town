"""Tests for alchemist."""

from alchemist.cli import main


def test_hello_runs(capsys):
    rc = main(["hello"])
    out = capsys.readouterr().out
    assert rc == 0
    assert "alchemist" in out
