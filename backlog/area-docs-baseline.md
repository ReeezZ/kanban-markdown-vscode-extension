---
id: "area-docs-baseline"
status: "backlog"
priority: "high"
assignee: null
epic: "01 Ordering Fixes"
dueDate: null
created: "2026-10-23T15:04:03.000Z"
modified: "2026-10-23T15:04:03.000Z"
completedAt: null
labels: ["chore", "workflow"]
order: "a0"
---
# Area docs baseline

**Goal:** a developer or agent can read how the extension and the webview work today, before touching the ordering code, instead of reverse-engineering `KanbanPanel.ts`.

Write two area docs and link them from [Building blocks](../docs/architecture.md#building-blocks):

- `docs/areas/extension.md`: the message switch, move and order, file watching, the card format.
- `docs/areas/webview.md`: the store, drag and drop, the editor.

They are also the fold target for the Phase 1 specs, so each Phase 1 spec folds into a doc that already exists.

**Done when**

- [ ] both area docs exist, in the style of the doc rules (concepts, flows, edge rules, a few decisions; no code listings)
- [ ] each is linked from Building blocks, replacing the "will be linked" sentence there
- [ ] the text was checked against the code, not against the handoff
- [ ] `./scripts/docs_check.py --check` passes

**Open questions**

- Is "file watching" part of the extension doc or its own area?

**Needs:** none