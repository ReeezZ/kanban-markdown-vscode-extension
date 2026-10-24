---
id: "sort-by-date"
status: "backlog"
priority: "low"
assignee: null
epic: "XX Board Future"
dueDate: null
created: "2026-10-24T11:28:57.000Z"
modified: "2026-10-24T11:28:57.000Z"
completedAt: null
labels: ["feature", "webview"]
order: "aQ"
---
# Sort cards by date added or date edited

Sort the cards in each column by `created` or `modified` instead of the manual `order`. Both dates are already in every card's frontmatter.

Open: whether the sort is a view mode that leaves `order` alone (and what dragging does while it's on) or a one-off action that rewrites `order`; newest or oldest first; whether the choice is remembered (a setting or `workspaceState`, both risky to change).

Upstream issue #23 asks for a variant: the Done column ordered by `completedAt`, newest first, with the date kept when a card leaves Done and comes back.
