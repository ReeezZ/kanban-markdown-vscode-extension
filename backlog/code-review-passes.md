---
id: "code-review-passes"
status: "backlog"
priority: "high"
assignee: null
epic: "01 Foundation"
dueDate: null
created: "2026-10-23T16:30:00.000Z"
modified: "2026-10-23T16:30:00.000Z"
completedAt: null
labels: ["chore", "extension"]
order: "a0s"
---
# Code review passes

**Goal:** the code quality of the extension host, the webview and `src/shared` is reviewed once, and the findings are cards, so the refactors that should come before the fixes are chosen deliberately.

One pass per area, after the area docs and the baseline tests exist. A finding is a card (correctness, structure, tests), not a fix made on the spot. The ones that should come before the Phase 2 fixes go into `01 Foundation`; the rest into a later epic.

**Done when**

- [ ] a review pass is done for the host, the webview and `src/shared`
- [ ] every finding is a card or is dropped, with the reason
- [ ] each card has an epic: Foundation if it must come before the fixes, otherwise later
- [ ] the roadmap's Foundation items still match what the review found

**Out of scope:** doing the refactors; each one is its own card.

**Open questions**

- Which lenses per pass (structure, correctness, tests, naming)?

**Needs:** [`baseline-tests`](baseline-tests.md), [`area-docs-baseline`](area-docs-baseline.md)
