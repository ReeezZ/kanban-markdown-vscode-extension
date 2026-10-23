---
id: "equal-order-keys"
status: "backlog"
priority: "high"
assignee: null
epic: "02 Ordering Fixes"
dueDate: null
created: "2026-10-23T15:04:03.000Z"
modified: "2026-10-23T23:50:00.000Z"
completedAt: null
labels: ["bug", "extension"]
order: "a2"
---
# Equal order keys must not break a drag

**Goal:** when two neighbouring cards share an `order` key, a drag still works, and when a move fails I see an error instead of nothing.

**Cause:** `generateKeyBetween(a, b)` from `fractional-indexing` throws when `a >= b`, which equal keys trigger. `case 'moveFeature'` (`src/extension/KanbanPanel.ts:121-123`) has no try/catch, so the drag fails silently. Status and `modified` are changed in memory before the key is known (L611-615), so the in-memory card is left half-changed and no file is written.

**Fix:** when `before >= after`, rebalance with `generateNKeysBetween`. Compute the new key first and mutate the card only after that. Wrap the handler in try/catch and show an error, with en, es and pt strings (`pnpm check-l10n`). Self-contained commit. The rebalance goes into the pure key function that [`baseline-tests`](baseline-tests.md) extracts, so it is tested without the panel.

Until this ships, every `order` key is unique across the whole board (see [Backlog](../docs/CLAUDE.md#backlog)); afterwards the rule can relax to unique per epic.

**Done when**

- [ ] equal keys no longer throw: the drop lands where it was dropped
- [ ] the card is not mutated when the move fails
- [ ] a failed move shows an error in en, es and pt
- [ ] unit tests cover equal neighbours, a rebalance, and the failure path
- [ ] the order rule in the backlog docs is relaxed once it ships

**Open questions**

- Rebalance only the run of equal keys, or the whole column? A rebalance of the whole column rewrites many card files.

**Needs:** [`baseline-tests`](baseline-tests.md)