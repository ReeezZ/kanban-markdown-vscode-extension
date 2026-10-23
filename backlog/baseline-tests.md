---
id: "baseline-tests"
status: "backlog"
priority: "high"
assignee: null
epic: "01 Foundation"
dueDate: null
created: "2026-10-23T16:30:00.000Z"
modified: "2026-10-23T16:30:00.000Z"
completedAt: null
labels: ["chore", "extension"]
order: "a0l"
---
# Baseline tests

**Goal:** the behaviour of moves, ordering and the host's message handling is pinned by tests before the code is reviewed and refactored, so a refactor that changes behaviour fails a test.

Today `_moveFeature` has no tests (see Risks in the [architecture doc](../docs/architecture.md#risks)). `tests/` has the card-file helpers, the shared utilities, the webview store and the integration suite; the move and order logic, the message switch and the file watcher's own-write rule are not covered. The tests pin what the code does now, including its known bugs; the fixes in Phase 2 then change those tests on purpose.

Needs a spec first: `KanbanPanel` depends on the VS Code API, so the spec picks the seam (a fake `vscode`, a pure function pulled out, or the integration suite).

**Done when**

- [ ] the spec says what is pinned and through which seam
- [ ] the move and order logic is covered: status change, the new key, the standard and epic views
- [ ] the message switch is covered for the card operations
- [ ] the file watcher's own-write rule is covered
- [ ] the webview's drop index computation is covered
- [ ] the tests run in CI

**Open questions**

- Extract pure functions as part of this card, or only test through a fake?

**Needs:** none
