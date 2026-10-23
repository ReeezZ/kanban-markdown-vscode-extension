---
id: "column-drop-rules"
status: "backlog"
priority: "low"
assignee: null
epic: "04 Board Polish"
dueDate: null
created: "2026-10-23T15:04:03.000Z"
modified: "2026-10-23T15:04:03.000Z"
completedAt: null
labels: ["enhancement", "extension"]
order: "aA"
---
# Rules for dropping into a column

**Goal:** I can set that a column takes no drops, or takes reordering only, so dragging a card into `ready` doesn't bypass `/refine`.

**Cause:** a drop into another column always sets the status (`_moveFeature` in `src/extension/KanbanPanel.ts`).

**Done when**

- [ ] a column can be set to "no drop in" or "reorder only"
- [ ] a refused drop leaves the card where it was and says why
- [ ] the rule is enforced in the host, not only in the webview
- [ ] tests cover a refused and an allowed drop

**Open questions**

- Where does the setting live: a new field on each entry of `kanban-markdown.columns`, or a separate setting? Either is a change to the configuration schema.
- Does "reorder only" apply to drops from other columns, or also to drops from a lane to another lane?

**Needs:** none