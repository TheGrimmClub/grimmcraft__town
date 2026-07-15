package main

import (
	"os"
	"path/filepath"
	"strings"
	"testing"
)

func TestValidate(t *testing.T) {
	good := []string{"scout", "my_app", "a", "app2", "under_score"}
	for _, n := range good {
		if err := (AppSpec{Name: n}).Validate(); err != nil {
			t.Errorf("%q should be valid: %v", n, err)
		}
	}
	bad := []string{"", "2app", "My_App", "with-dash", "with space", "_leading"}
	for _, n := range bad {
		if err := (AppSpec{Name: n}).Validate(); err == nil {
			t.Errorf("%q should be invalid", n)
		}
	}
}

func TestScaffoldWritesLayout(t *testing.T) {
	apps := t.TempDir()
	spec := AppSpec{Name: "widget", Description: "A test widget", Author: "Ada"}

	written, err := Scaffold(apps, spec, false)
	if err != nil {
		t.Fatalf("Scaffold: %v", err)
	}

	want := []string{
		"widget/pyproject.toml",
		"widget/Taskfile.yaml",
		"widget/src/widget/__init__.py",
		"widget/src/widget/__main__.py",
		"widget/src/widget/cli.py",
		"widget/tests/test_widget.py",
	}
	if len(written) != len(want) {
		t.Fatalf("wrote %d files, want %d: %v", len(written), len(want), written)
	}
	for _, rel := range want {
		if _, err := os.Stat(filepath.Join(apps, rel)); err != nil {
			t.Errorf("expected %s: %v", rel, err)
		}
	}
}

func TestScaffoldRendersTemplates(t *testing.T) {
	apps := t.TempDir()
	spec := AppSpec{Name: "widget", Description: "A test widget", Author: "Ada"}
	if _, err := Scaffold(apps, spec, false); err != nil {
		t.Fatal(err)
	}
	read := func(rel string) string {
		b, err := os.ReadFile(filepath.Join(apps, "widget", rel))
		if err != nil {
			t.Fatal(err)
		}
		return string(b)
	}

	pyproject := read("pyproject.toml")
	for _, want := range []string{`name = "widget"`, `description = "A test widget"`, `widget = "widget.cli:main"`, `packages = ["src/widget"]`} {
		if !strings.Contains(pyproject, want) {
			t.Errorf("pyproject.toml missing %q", want)
		}
	}

	// The literal {{.CLI_ARGS}} must survive templating (different delimiters).
	taskfile := read("Taskfile.yaml")
	if !strings.Contains(taskfile, "uv run widget hello {{.CLI_ARGS}}") {
		t.Errorf("Taskfile.yaml did not preserve {{.CLI_ARGS}}:\n%s", taskfile)
	}
	if !strings.Contains(taskfile, "apps/widget/src") {
		t.Errorf("Taskfile.yaml missing PYTHONPATH entry")
	}

	cli := read("src/widget/cli.py")
	if !strings.Contains(cli, `NAME = "widget"`) {
		t.Errorf("cli.py missing NAME constant")
	}
	if strings.Contains(read("src/widget/__init__.py"), "Ada") == false {
		t.Errorf("__init__.py missing author")
	}
}

func TestScaffoldRefusesExisting(t *testing.T) {
	apps := t.TempDir()
	spec := AppSpec{Name: "widget", Description: "x"}
	if _, err := Scaffold(apps, spec, false); err != nil {
		t.Fatal(err)
	}
	if _, err := Scaffold(apps, spec, false); err == nil {
		t.Error("expected refusal on existing app without --force")
	}
	if _, err := Scaffold(apps, spec, true); err != nil {
		t.Errorf("--force should overwrite: %v", err)
	}
}

func TestScaffoldRejectsBadName(t *testing.T) {
	apps := t.TempDir()
	if _, err := Scaffold(apps, AppSpec{Name: "Bad-Name"}, false); err == nil {
		t.Error("expected validation error for bad name")
	}
}

func TestFindAppsDir(t *testing.T) {
	root := t.TempDir()
	if err := os.WriteFile(filepath.Join(root, "config.yaml"), []byte("x:\n"), 0o644); err != nil {
		t.Fatal(err)
	}
	nested := filepath.Join(root, "apps", "carpenter")
	if err := os.MkdirAll(nested, 0o755); err != nil {
		t.Fatal(err)
	}
	got, err := findAppsDir(nested)
	if err != nil {
		t.Fatal(err)
	}
	if want := filepath.Join(root, "apps"); got != want {
		t.Errorf("findAppsDir = %q, want %q", got, want)
	}
}
