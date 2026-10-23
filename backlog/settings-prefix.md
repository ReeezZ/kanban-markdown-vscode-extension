---
id: "settings-prefix"
status: "backlog"
priority: "medium"
assignee: null
epic: "04 Publish"
dueDate: null
created: "2026-10-23T15:04:03.000Z"
modified: "2026-10-23T15:04:03.000Z"
completedAt: null
labels: ["enhancement", "extension"]
order: "aC"
---
# Own settings prefix

**Goal:** the fork's settings and commands use its own prefix, not `kanban-markdown.*`, so they don't clash with the original extension.

The `contributes.configuration` schema, the command and view IDs and the `workspaceState` keys are risky to change (see [Scope Control](../CLAUDE.md#scope-control--risk-guardrails)), so this starts with a short plan. The repo's own `.vscode/settings.json` and `docs/CLAUDE.md` name `kanban-markdown.columns` and must change with it; the docs check reads the columns by `id`, so it keeps working.

**Done when**

- [ ] the plan says what is renamed: settings, commands, views, state keys
- [ ] settings and commands use the new prefix
- [ ] `.vscode/settings.json` and the docs use the new prefix
- [ ] the integration tests pass

**Open questions**

- Read the old `kanban-markdown.*` keys as a fallback, so others can switch without trouble? It costs code.
- Rename the command and view IDs too, or only the settings?

**Needs:** [`fork-name-and-publisher`](fork-name-and-publisher.md)