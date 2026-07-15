// carpenter — an interactive scaffolder for GrimmCraft Town.
//
// It asks a few questions in a Bubble Tea + Lip Gloss form, then stamps out a
// new Python app under apps/<name>/ that follows the same layout as the
// hand-written tools (pyproject.toml, Taskfile.yaml, src/<name>, tests).
//
// Interactive:      go run .            (or `task carpenter:new`)
// Non-interactive:  go run . --name my_app --desc "…" [--author "…"] [--force]
package main

import (
	"fmt"
	"os"
	"os/exec"
	"path/filepath"
	"strings"

	"github.com/charmbracelet/bubbles/textinput"
	tea "github.com/charmbracelet/bubbletea"
	"github.com/charmbracelet/lipgloss"
)

const usage = `carpenter — scaffold a new Python app under apps/

Usage:
  carpenter                              run the interactive questionnaire
  carpenter --name <name> [--desc <s>]   scaffold without the TUI
             [--author <s>] [--force]

Flags:
  --name        app name (lowercase, [a-z][a-z0-9_]*); enables headless mode
  --desc        one-line description
  --author      author name (defaults to git user.name)
  --force       overwrite an existing app directory
  --root        repo root to scaffold into (default: found via config.yaml)
  -h, --help    show this help
`

// -- Lip Gloss styling (the "lipstick") --------------------------------------

var (
	titleStyle   = lipgloss.NewStyle().Bold(true).Foreground(lipgloss.Color("#F9801D")).MarginBottom(1)
	labelStyle   = lipgloss.NewStyle().Foreground(lipgloss.Color("#8A93E8"))
	focusLabel   = lipgloss.NewStyle().Bold(true).Foreground(lipgloss.Color("#FED83D"))
	helpStyle    = lipgloss.NewStyle().Faint(true).MarginTop(1)
	errStyle     = lipgloss.NewStyle().Bold(true).Foreground(lipgloss.Color("#B02E26"))
	okStyle      = lipgloss.NewStyle().Bold(true).Foreground(lipgloss.Color("#5E7C16"))
	pathStyle    = lipgloss.NewStyle().Foreground(lipgloss.Color("#169C9C"))
	boxStyle     = lipgloss.NewStyle().Border(lipgloss.RoundedBorder()).BorderForeground(lipgloss.Color("#F9801D")).Padding(1, 2)
)

// -- Bubble Tea model --------------------------------------------------------

type field struct {
	label string
	input textinput.Model
}

type model struct {
	appsDir string
	force   bool
	fields  []field
	focus   int
	err     error
	done    bool
	created []string
	cancel  bool
}

func initialModel(appsDir string, force bool, defAuthor string) model {
	labels := []string{"App name", "Description", "Author"}
	placeholders := []string{"my_app", "One-line summary of the app", "Ada Lovelace"}
	fields := make([]field, len(labels))
	for i := range labels {
		ti := textinput.New()
		ti.Placeholder = placeholders[i]
		ti.CharLimit = 120
		ti.Width = 42
		fields[i] = field{label: labels[i], input: ti}
	}
	if defAuthor != "" {
		fields[2].input.SetValue(defAuthor)
	}
	fields[0].input.Focus()
	return model{appsDir: appsDir, force: force, fields: fields}
}

func (m model) Init() tea.Cmd { return textinput.Blink }

func (m model) Update(msg tea.Msg) (tea.Model, tea.Cmd) {
	if key, ok := msg.(tea.KeyMsg); ok {
		switch key.String() {
		case "ctrl+c", "esc":
			m.cancel = true
			return m, tea.Quit
		case "tab", "down":
			m.focus = (m.focus + 1) % len(m.fields)
			return m, m.refocus()
		case "shift+tab", "up":
			m.focus = (m.focus - 1 + len(m.fields)) % len(m.fields)
			return m, m.refocus()
		case "enter":
			if m.focus < len(m.fields)-1 {
				m.focus++
				return m, m.refocus()
			}
			return m.submit()
		}
	}
	var cmd tea.Cmd
	m.fields[m.focus].input, cmd = m.fields[m.focus].input.Update(msg)
	return m, cmd
}

func (m *model) refocus() tea.Cmd {
	var cmd tea.Cmd
	for i := range m.fields {
		if i == m.focus {
			cmd = m.fields[i].input.Focus()
		} else {
			m.fields[i].input.Blur()
		}
	}
	return cmd
}

func (m model) submit() (tea.Model, tea.Cmd) {
	spec := specFromInputs(m.fields)
	written, err := Scaffold(m.appsDir, spec, m.force)
	if err != nil {
		m.err = err
		return m, nil // stay on the form so the user can fix it
	}
	m.done, m.created, m.err = true, written, nil
	return m, tea.Quit
}

func specFromInputs(fields []field) AppSpec {
	spec := AppSpec{
		Name:        strings.TrimSpace(fields[0].input.Value()),
		Description: strings.TrimSpace(fields[1].input.Value()),
		Author:      strings.TrimSpace(fields[2].input.Value()),
	}
	return spec.withDefaults()
}

func (s AppSpec) withDefaults() AppSpec {
	if s.Description == "" {
		s.Description = s.Name + " — a GrimmCraft Town tool"
	}
	return s
}

func (m model) View() string {
	if m.done {
		return "" // final summary is printed by main() after the program exits
	}
	var b strings.Builder
	b.WriteString(titleStyle.Render("🔨 carpenter — new Python app"))
	b.WriteByte('\n')
	for i, f := range m.fields {
		marker := "  "
		lbl := labelStyle.Render(f.label)
		if i == m.focus {
			marker = focusLabel.Render("▸ ")
			lbl = focusLabel.Render(f.label)
		}
		b.WriteString(fmt.Sprintf("%s%s\n  %s\n\n", marker, lbl, f.input.View()))
	}
	if m.err != nil {
		b.WriteString(errStyle.Render("✗ "+m.err.Error()) + "\n")
	}
	b.WriteString(helpStyle.Render("tab / ↑↓ move · enter next/create · esc cancel"))
	return boxStyle.Render(b.String())
}

// -- entry point -------------------------------------------------------------

func main() {
	opts, err := parseArgs(os.Args[1:])
	if err != nil {
		fmt.Fprintln(os.Stderr, "carpenter:", err)
		os.Exit(2)
	}
	if opts.help {
		fmt.Print(usage)
		return
	}

	root := opts.root
	if root == "" {
		root, _ = os.Getwd()
	}
	appsDir, err := findAppsDir(root)
	if err != nil {
		fmt.Fprintln(os.Stderr, "carpenter:", err)
		os.Exit(1)
	}

	author := opts.author
	if author == "" {
		author = gitAuthor()
	}

	// Headless mode: --name given, skip the TUI entirely.
	if opts.name != "" {
		spec := AppSpec{Name: opts.name, Description: opts.desc, Author: author}.withDefaults()
		written, err := Scaffold(appsDir, spec, opts.force)
		if err != nil {
			fmt.Fprintln(os.Stderr, "carpenter:", err)
			os.Exit(1)
		}
		printSuccess(appsDir, spec, written)
		return
	}

	res, err := tea.NewProgram(initialModel(appsDir, opts.force, author)).Run()
	if err != nil {
		fmt.Fprintln(os.Stderr, "carpenter:", err)
		os.Exit(1)
	}
	fm := res.(model)
	switch {
	case fm.done:
		printSuccess(appsDir, specFromInputs(fm.fields), fm.created)
	case fm.cancel:
		fmt.Println("carpenter: cancelled — nothing written.")
	}
}

type options struct {
	name, desc, author, root string
	force, help              bool
}

func parseArgs(args []string) (options, error) {
	var o options
	for i := 0; i < len(args); i++ {
		switch args[i] {
		case "-h", "--help":
			o.help = true
		case "--force", "-f":
			o.force = true
		case "--name", "--desc", "--author", "--root":
			if i+1 >= len(args) {
				return o, fmt.Errorf("%s needs a value", args[i])
			}
			i++
			switch args[i-1] {
			case "--name":
				o.name = args[i]
			case "--desc":
				o.desc = args[i]
			case "--author":
				o.author = args[i]
			case "--root":
				o.root = args[i]
			}
		default:
			return o, fmt.Errorf("unknown argument %q (try --help)", args[i])
		}
	}
	return o, nil
}

func gitAuthor() string {
	out, err := exec.Command("git", "config", "user.name").Output()
	if err != nil {
		return ""
	}
	return strings.TrimSpace(string(out))
}

func printSuccess(appsDir string, spec AppSpec, written []string) {
	repoRoot := filepath.Dir(appsDir)
	var b strings.Builder
	b.WriteString(okStyle.Render(fmt.Sprintf("✓ forged app %q", spec.Name)) + "\n\n")
	for _, p := range written {
		if rel, err := filepath.Rel(repoRoot, p); err == nil {
			p = rel
		}
		b.WriteString("  " + pathStyle.Render(p) + "\n")
	}
	b.WriteString("\n" + titleStyle.Render("Next steps") + "\n")
	b.WriteString(fmt.Sprintf(`  1. Register it with the workspace in pyproject.toml:
       - add %q to [project].dependencies
       - add '%s = { workspace = true }' to [tool.uv.sources]
  2. Wire it into the root Taskfile.yaml:
       - add apps/%s/src to the PYTHONPATH env
       - add an include under includes:  %s: { taskfile: ./apps/%s/Taskfile.yaml, dir: . }
  3. Install & test:  task setup && uv run %s hello
`, spec.Name, spec.Name, spec.Name, spec.Name, spec.Name, spec.Name))
	fmt.Print(boxStyle.Render(b.String()) + "\n")
}
