---
id: "epic-lane-drop-order"
status: "backlog"
priority: "high"
assignee: null
epic: "02 Ordering Fixes"
dueDate: null
created: "2026-10-23T15:04:03.000Z"
modified: "2026-10-23T15:04:03.000Z"
completedAt: null
labels: ["bug", "extension"]
order: "a1"
---
# Drop in an epic lane keeps its position

**Goal:** when I drop a card in an epic lane, it stays where I dropped it, also after the board reloads.

**Cause:** the webview computes the drop index within the lane and column (`KanbanBoard.tsx:89`, `:109`; `App.tsx:339-344`). The host applies that index to the whole column across all epics: `KanbanPanel._moveFeature` filters the target column without the lane (`src/extension/KanbanPanel.ts:618-620`) and generates the key at L626. The `moveFeature` message has no lane field (`src/shared/types.ts:127`), while `moveAllCards` has one (L138). So the card lands next to cards of other epics and jumps after the reload.

**Fix:** send the epic lane in `moveFeature` and filter the target column with `featureMatchesEpicLane` (`src/shared/epicLane.ts`, already used by `_moveAllCards`). `_moveFeature` has no unit tests yet.

**Done when**

- [ ] `moveFeature` carries the lane, and `_moveFeature` filters by it
- [ ] a drop in a lane keeps its position after reload (checked on the sample board)
- [ ] unit tests cover a drop in a lane, across lanes and in the standard view
**Open questions**

- Extract the key computation out of `_moveFeature` into a pure function, so the tests don't need the panel? Probably yes; decide in the spec or the first commit.

**Needs:** none