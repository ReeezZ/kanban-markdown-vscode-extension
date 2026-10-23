---
id: "send-to-top-bottom"
status: "backlog"
priority: "low"
assignee: null
epic: "04 Board Polish"
dueDate: null
created: "2026-10-23T15:04:03.000Z"
modified: "2026-10-23T15:04:03.000Z"
completedAt: null
labels: ["feature", "webview"]
order: "a9"
---
# Send a card to the top or bottom

**Goal:** I can send a card to the top or bottom of its column, or of its lane in the epic view, without dragging it.

**Cause:** none, this is new. The order logic is small: `generateKeyBetween(null, first)` for the top and `generateKeyBetween(last, null)` for the bottom, using the lane filter from [`epic-lane-drop-order`](epic-lane-drop-order.md).

**Done when**

- [ ] a card can be sent to the top and to the bottom, in the standard view and in a lane
- [ ] the key computation is a pure function with unit tests
- [ ] a decision on the UI is written down

**Open questions**

- The UI: cards have no context menu. Options: hover buttons on the card, a keyboard shortcut on the focused card, a webview context menu (`webview/context` contribution and `data-vscode-context`), or a command palette entry for the open card. Decide after the lane fix.

**Needs:** [`epic-lane-drop-order`](epic-lane-drop-order.md)