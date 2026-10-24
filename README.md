<div align="center">

<img src="https://raw.githubusercontent.com/ReeezZ/kanban-markdown-vscode-extension/main/resources/icon.png" alt="Markan" width="60" />

# Markan

*"Now your backlog can have merge conflicts too."*

**An agent native Kanban board for VS Code, backed by markdown files.**

[![License](https://img.shields.io/badge/license-MIT-green)](LICENSE)

[![Claude Code](https://img.shields.io/badge/Claude_Code-supported-f97316?logo=anthropic&logoColor=white)](https://docs.anthropic.com/en/docs/claude-code)
[![Codex](https://img.shields.io/badge/Codex-supported-10a37f?logo=openai&logoColor=white)](https://github.com/openai/codex)
[![GitHub Copilot](https://img.shields.io/badge/Copilot-supported-2b6cb0?logo=githubcopilot&logoColor=white)](https://github.com/features/copilot)
[![OpenCode](https://img.shields.io/badge/OpenCode-supported-64748b)](https://github.com/opencode-ai/opencode)
[![skills.sh](https://img.shields.io/badge/skills.sh-compatible-a855f7)](https://skills.sh)

<img src="https://raw.githubusercontent.com/ReeezZ/kanban-markdown-vscode-extension/main/docs/images/editor-view.png" alt="Editor View" width="800" />

</div>

---

## About this fork

Markan is a personal project in progress, forked from [LachyFS/kanban-markdown-vscode-extension](https://github.com/LachyFS/kanban-markdown-vscode-extension), published as [Kanban Markdown](https://marketplace.visualstudio.com/items?itemName=LachyFS.kanban-markdown) on the VS Code Marketplace. The fork starts from upstream's code and file format, and plans to fix card ordering in the epic view, improve card editing and board polish, and later publish under its own name. "Markan" is a provisional name. The plan is in the [roadmap](docs/roadmap.md).

Features are stored as markdown files with YAML frontmatter — version-controllable, diffable, and editable outside the extension. No accounts, no external services.

## Quick Start

1. **Install** — Markan isn't published yet: [build and install the `.vsix`](#installation), or install [upstream's published original](https://marketplace.visualstudio.com/items?itemName=LachyFS.kanban-markdown)
2. **Open** — run `Open Kanban Board` from the command palette (`Cmd+Shift+P` / `Ctrl+Shift+P`)
3. **Create** — press `N` to add your first feature card

## Features

### Board & Workflow

- 5-column workflow — Backlog, To Do, In Progress, Review, Done (customizable)
- Drag-and-drop between columns and within columns
- Sidebar view from the activity bar
- Split-view editor — board on left, inline editor on right
- Horizontal and vertical layouts
- Compact mode for dense boards
- Keyboard shortcuts — `N` new feature, `Esc` close dialogs, `Cmd/Ctrl+Enter` submit

### Cards

Each card is a markdown file with YAML frontmatter.

<div align="center">
<img src="https://raw.githubusercontent.com/ReeezZ/kanban-markdown-vscode-extension/main/docs/images/board-overview.png" alt="Kanban Board Overview" width="800" />
</div>

- Priority levels — Critical, High, Medium, Low with color-coded badges
- Assignees
- Due dates with smart formatting (Overdue, Today, Tomorrow, "5d", etc.)
- Labels — multiple per card, shows up to 3 with "+X more"
- Automatic created/modified timestamps
- Archive completed features to keep the board clean

### Search & Filtering

- Full-text search across content, IDs, assignees, and labels
- Filter by priority, assignee, label, or due date
- Due date filters — overdue, today, this week, or no date

### Editor Integration

- Rich text editing with Tiptap
- Inline frontmatter editing — dropdowns for status/priority, inputs for assignee/due date/labels
- Auto-save on change
- Auto-refresh when files change externally
- Native markdown mode — open files in VS Code's built-in editor instead
- Follows your VS Code/Cursor theme (light & dark)

## AI Agent Integration

Cards include a "Build with AI" action that passes full feature context (title, priority, labels, description) to your preferred agent.

| Agent | Modes |
|-------|-------|
| Claude Code | Default, Plan, Auto-edit, Full Auto |
| Codex | Suggest, Auto-edit, Full Auto |
| GitHub Copilot | Default |
| OpenCode | Default |

### Kanban Skill

Give agents read/write access to your board from the terminal:

```bash
npx skills add https://github.com/LachyFS/kanban-skill
```

Compatible with Claude Code, Codex, OpenCode, and [skills.sh](https://skills.sh)-compatible agents. See [kanban-skill](https://github.com/LachyFS/kanban-skill) for details.

## File Format

Features live in `.devtool/features/` by default, organized into subfolders by status.

```markdown
---
id: "implement-dark-mode-toggle-2026-01-25"
status: "todo"
priority: "high"
assignee: "john"
dueDate: "2026-01-25"
created: "2026-01-25T10:30:00.000Z"
modified: "2026-01-25T14:20:00.000Z"
labels: ["feature", "ui"]
order: 0
---

# Implement dark mode toggle

Add a toggle in settings to switch between light and dark themes...
```

## Configuration

Settings live under `kanban-markdown.*` in your VS Code/Cursor preferences.

| Setting | Default | Description |
|---------|---------|-------------|
| `featuresDirectory` | `.devtool/features` | Directory for feature files (relative to workspace root) |
| `filenamePattern` | `name-date` | Filename pattern for new cards (`name-date`, `date-name`, `name-datetime`, `datetime-name`) |
| `defaultPriority` | `medium` | Default priority for new features |
| `defaultStatus` | `backlog` | Default status for new features |
| `columns` | *see below* | Customize column IDs, names, and colors |
| `aiAgent` | `claude` | AI agent for "Build with AI" (`claude`, `codex`, `copilot`, `opencode`) |
| `showPriorityBadges` | `true` | Show priority badges on cards |
| `showAssignee` | `true` | Show assignee on cards |
| `showDueDate` | `true` | Show due date on cards |
| `showLabels` | `true` | Show labels on cards and in editors |
| `showBuildWithAI` | `true` | Show "Build with AI" button on cards |
| `showFileName` | `false` | Show the source markdown filename on cards |
| `compactMode` | `false` | Use compact card layout |
| `addNewCardsToTop` | `false` | Add new cards to the top of the column |
| `markdownEditorMode` | `false` | Open files in VS Code's native text editor instead of the inline rich-text editor |

Default columns:

```json
[
  { "id": "backlog", "name": "Backlog", "color": "#6b7280" },
  { "id": "todo", "name": "To Do", "color": "#3b82f6" },
  { "id": "in-progress", "name": "In Progress", "color": "#f59e0b" },
  { "id": "review", "name": "Review", "color": "#8b5cf6" },
  { "id": "done", "name": "Done", "color": "#22c55e" }
]
```

## Installation

Markan isn't published on a marketplace yet. Until it is, build the `.vsix` and install it:

1. `pnpm install`, then `pnpm package` — writes the `.vsix` to `releases/`
2. In VS Code: Extensions > `...` > Install from VSIX
3. Select the file from `releases/`

For the published original, install [Kanban Markdown](https://marketplace.visualstudio.com/items?itemName=LachyFS.kanban-markdown) from the VS Code Marketplace, or from [Open VSX](https://open-vsx.org/extension/LachyFS/kanban-markdown) (VSCodium, Cursor, etc.).

## Development

See [docs/development.md](docs/development.md) for setup, checks and workflow, and [CONTRIBUTING.md](CONTRIBUTING.md) for upstream's contributor guide.

## Contributors

Contributors to upstream, whose work this fork builds on:

- [@luciopaiva](https://github.com/luciopaiva) — sidebar view and layout improvements
- [@ungive](https://github.com/ungive) — file organization and status subfolders
- [@hodanli](https://github.com/hodanli) — label management enhancements
- [@SuperbDotHub](https://github.com/SuperbDotHub) — compact mode and card display options

## License

[MIT](LICENSE)
