---
id: "baseline-tests"
status: "done"
priority: "high"
assignee: null
epic: "01 Foundation"
dueDate: null
created: "2026-10-23T16:30:00.000Z"
modified: "2026-10-24T19:10:06.000Z"
completedAt: "2026-10-24T19:10:06.000Z"
labels: ["chore", "extension"]
order: "a0l"
---
# Baseline tests

**Goal:** a refactor that changes where a moved card lands fails a test, so the review's refactors and the Phase 2 fixes start from pinned behaviour instead of guesses.

This is preparation, not a feature: nothing changes for the person using the board. The tests are a safety net so the code can be changed afterwards without silently breaking moves.

Today `_moveFeature`, the `moveFeature` message and the webview's drop-index mapping have no tests (see Risks in the [architecture doc](../docs/architecture.md#risks)). This card pins the move path where it works correctly today: the standard view, with distinct keys.

Two seams:

- a fake `vscode` module (in-memory fs and a fake watcher, as in `tests/extension/featureFileUtils.test.ts`): the tests send `moveFeature` to `KanbanPanel` and check the file written and the `init` posted;
- the key computation (target column without the moved card, sorted by `order`, `generateKeyBetween` of the neighbours at the index), now in both `_moveFeature` and `App.tsx`, becomes one pure function with its own tests.

Order: the panel tests first, against today's code, then the extraction with them green, so the extraction isn't itself an untested refactor.

Spec first (0002): what is pinned, where the pure function lives, whether the drop-index mapping is extracted too, and the fake's shape.

Spec: `docs/specs/0002-baseline-tests.md`

**Done when**

- [x] the spec says what is pinned and through which seam
- [x] `moveFeature` through the panel is covered: a reorder within a column, a status change, a move into and out of `done` (the file moves, `completedAt` set or cleared, `modified` set), only the moved card's file written
- [x] the key computation is one pure function used by the host and the webview, with unit tests
- [x] the watcher is covered for a move: events dropped while `_migrating` is set, the 100 ms debounce before the reload, the open card reloaded in the editor when it differs from its last save
- [x] the webview's drop-index mapping is covered: filtered list to column index, a downward move in the same column, a drop on its own position does nothing
- [x] the tests run in `pnpm test`, and `KanbanPanel.ts` is no longer excluded from coverage in `vitest.config.mts`

**Out of scope:** the known bugs, a drop in an epic lane and equal keys: they stay unpinned, so a refactor could change them unnoticed, and [`epic-lane-drop-order`](../epic-lane-drop-order.md) and [`equal-order-keys`](../equal-order-keys.md) bring their tests with the fix. Other messages, move all, archive, loading and its migrations, labels and the sidebar are in the test gaps of [`code-review-passes`](../code-review-passes.md).

**Needs:** none
