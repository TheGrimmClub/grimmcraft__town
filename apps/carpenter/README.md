# carpenter

An interactive scaffolder for GrimmCraft Town. Ask a few questions in a
[Bubble Tea](https://github.com/charmbracelet/bubbletea) +
[Lip Gloss](https://github.com/charmbracelet/lipgloss) form, and carpenter
stamps out a new Python app under `apps/<name>/` that matches the layout of the
hand-written tools (guard, scout, blacksmith, town).

Unlike the other apps, carpenter is a **Go** program — the questionnaire wants a
real TUI, and Bubble Tea/Lip Gloss are Go libraries.

## Usage

```sh
task carpenter:new                 # interactive questionnaire
# or, from apps/carpenter:
go run .

# non-interactive (scriptable, no TTY needed):
go run . --name my_app --desc "What it does" --author "You" [--force]
```

It generates:

```
apps/<name>/
  pyproject.toml
  Taskfile.yaml
  src/<name>/__init__.py  __main__.py  cli.py
  tests/test_<name>.py
```

then prints the next steps to register the app in the root `pyproject.toml` and
`Taskfile.yaml`.

## Develop

```sh
task carpenter:test    # go test ./...
task carpenter:build   # compile ./carpenter
task carpenter:tidy    # go mod tidy
```
