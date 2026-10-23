---
id: "status-options-from-columns"
status: "backlog"
priority: "high"
assignee: null
epic: "02 Card Editing"
dueDate: null
created: "2026-10-23T15:04:03.000Z"
modified: "2026-10-23T15:04:03.000Z"
completedAt: null
labels: ["bug", "webview"]
order: "a4"
---
# Status dropdown lists the configured columns

**Goal:** in the card editor the status list shows my configured columns, so I can pick `ready`, and picking a status never drops the card off the board. Upstream issue #61.

**Cause:** `FeatureEditor.tsx` hardcodes `statuses` (L74), `statusDots` (L83) and the labels (`getStatusLabels()`, L541), and `FeatureStatus` in `src/shared/types.ts:4` is the fixed union `'backlog' | 'todo' | 'in-progress' | 'review' | 'done'`. A card with a status that is no configured column doesn't show on the board.

**Fix:** build the options from the configured `columns` and widen the type to `string`. Self-contained.

**Done when**

- [ ] the dropdown lists the columns from `kanban-markdown.columns`, with their names
- [ ] `ready` and `in-progress` can be picked; `todo` and `review` are gone unless configured
- [ ] `FeatureStatus` is widened and the code still type-checks
- [ ] a test covers options from a custom column set

**Open questions**

- What dot colour does a column get in the editor: its configured colour?

**Needs:** none