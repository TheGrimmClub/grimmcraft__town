// Package main — carpenter's scaffolding logic.
//
// This file is deliberately free of any Bubble Tea / Lip Gloss code so it can be
// unit-tested on its own: Scaffold() takes a plain AppSpec and writes a new
// Python app under apps/<name>/, matching the layout of the hand-written apps
// (guard, scout, blacksmith, town).
package main

import (
	"fmt"
	"os"
	"path/filepath"
	"regexp"
	"sort"
	"strings"
	"text/template"
)

// AppSpec is everything carpenter needs to stamp out a new app.
type AppSpec struct {
	Name        string
	Description string
	Author      string
}

var nameRe = regexp.MustCompile(`^[a-z][a-z0-9_]*$`)

// Validate checks that Name is a legal Python module / package name.
func (s AppSpec) Validate() error {
	if !nameRe.MatchString(s.Name) {
		return fmt.Errorf("app name %q must be lowercase and match [a-z][a-z0-9_]*", s.Name)
	}
	return nil
}

// files maps a destination path (relative to the new app dir) to its template.
// Templates use [[ ]] delimiters so the literal {{.CLI_ARGS}} in the generated
// Taskfile — and any {…} in the Python — passes straight through untouched.
func (s AppSpec) files() map[string]string {
	return map[string]string{
		"pyproject.toml": pyprojectTmpl,
		"Taskfile.yaml":  taskfileTmpl,
		filepath.Join("src", s.Name, "__init__.py"):  initTmpl,
		filepath.Join("src", s.Name, "__main__.py"):  mainTmpl,
		filepath.Join("src", s.Name, "cli.py"):       cliTmpl,
		filepath.Join("tests", "test_"+s.Name+".py"): testTmpl,
	}
}

// Scaffold writes the new app under appsDir/<name>/ and returns the created
// files (sorted). It refuses to touch an existing app unless force is set.
func Scaffold(appsDir string, spec AppSpec, force bool) ([]string, error) {
	if err := spec.Validate(); err != nil {
		return nil, err
	}
	appDir := filepath.Join(appsDir, spec.Name)
	if _, err := os.Stat(appDir); err == nil && !force {
		return nil, fmt.Errorf("%s already exists — pass --force to overwrite", appDir)
	}

	var written []string
	for rel, tmpl := range spec.files() {
		dest := filepath.Join(appDir, rel)
		if err := os.MkdirAll(filepath.Dir(dest), 0o755); err != nil {
			return written, err
		}
		content, err := render(tmpl, spec)
		if err != nil {
			return written, err
		}
		if err := os.WriteFile(dest, []byte(content), 0o644); err != nil {
			return written, err
		}
		written = append(written, dest)
	}
	sort.Strings(written)
	return written, nil
}

func render(tmpl string, spec AppSpec) (string, error) {
	t, err := template.New("f").Delims("[[", "]]").Parse(tmpl)
	if err != nil {
		return "", err
	}
	var b strings.Builder
	if err := t.Execute(&b, spec); err != nil {
		return "", err
	}
	return b.String(), nil
}

// findAppsDir walks up from start looking for the repo root (marked by
// config.yaml) and returns its apps/ directory.
func findAppsDir(start string) (string, error) {
	dir, err := filepath.Abs(start)
	if err != nil {
		return "", err
	}
	for {
		if _, err := os.Stat(filepath.Join(dir, "config.yaml")); err == nil {
			return filepath.Join(dir, "apps"), nil
		}
		parent := filepath.Dir(dir)
		if parent == dir {
			return "", fmt.Errorf("no repo root (config.yaml) found from %s upward", start)
		}
		dir = parent
	}
}

const pyprojectTmpl = `[project]
name = "[[.Name]]"
version = "2026.1.0"
description = "[[.Description]]"
requires-python = ">=3.11"
dependencies = [
    "filesystem",
    "minecraft",
]

[project.scripts]
[[.Name]] = "[[.Name]].cli:main"

[build-system]
requires = ["hatchling"]
build-backend = "hatchling.build"

[tool.hatch.build.targets.wheel]
packages = ["src/[[.Name]]"]

[tool.uv.sources]
filesystem = { workspace = true }
`

const taskfileTmpl = `version: "3"

env:
  PYTHONPATH: packages/filesystem/src:apps/[[.Name]]/src

tasks:
  default:
    desc: "Run the default task"
    cmds:
      - task --list
  info:
    desc: "Say hello (starter command — replace me)"
    cmds:
      - uv run [[.Name]] hello {{.CLI_ARGS}}
`

const initTmpl = `"""[[.Name]] — [[.Description]]

Author: [[.Author]]
Scaffolded by carpenter.
"""

__version__ = "2026.1.0"
`

const mainTmpl = `from .cli import main

if __name__ == "__main__":
    raise SystemExit(main())
`

const cliTmpl = `"""[[.Name]]'s command-line interface (argparse).

Scaffolded by carpenter — replace the starter ` + "``hello``" + ` command with real
ones. Follows the same shape as the other tools (guard, scout, …).
"""

from __future__ import annotations

import argparse
import sys

NAME = "[[.Name]]"


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(prog=NAME, description="[[.Description]]")
    sub = parser.add_subparsers(dest="command", required=True)

    p_hello = sub.add_parser("hello", help="Say hello (starter command)")
    p_hello.set_defaults(func=_cmd_hello)

    return parser


def _cmd_hello(args) -> int:
    print(f"{NAME}: hello! Replace me with real commands.")
    return 0


def main(argv: list[str] | None = None) -> int:
    args = build_parser().parse_args(argv if argv is not None else sys.argv[1:])
    return args.func(args)


if __name__ == "__main__":
    raise SystemExit(main())
`

const testTmpl = `"""Tests for [[.Name]]."""

from [[.Name]].cli import main


def test_hello_runs(capsys):
    rc = main(["hello"])
    out = capsys.readouterr().out
    assert rc == 0
    assert "[[.Name]]" in out
`
