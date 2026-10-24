---
id: "ai-start-command-quoting"
status: "backlog"
priority: "low"
assignee: null
epic: null
dueDate: null
created: "2026-10-24T11:24:53.000Z"
modified: "2026-10-24T11:24:53.000Z"
completedAt: null
labels: ["bug", "extension"]
order: "aO"
---
# Build with AI command breaks outside POSIX shells and for Codex

`_startWithAI` types the agent command into the user's shell with `terminal.sendText`, quoted by `_shellQuote` for POSIX shells only (`KanbanPanel.ts:337`). In `cmd.exe` a `'` isn't a quote, so `&`, `|` or `>` in the title or the first 200 characters of the body act as operators; PowerShell is probably affected too. Not tried on Windows. A fix might pass the arguments through `TerminalOptions.shellPath` and `shellArgs` instead of typing them.

The Codex branch (`KanbanPanel.ts:944-951`) passes `ask`, `auto`, `full-auto` and `suggest` to `--ask-for-approval`; the current CLI is believed to take `untrusted`, `on-failure`, `on-request` or `never`, with full auto as its own `--full-auto` flag. Check against the Codex docs.

Bypass and full-auto modes stay: choosing one is like passing the flag on the CLI.
