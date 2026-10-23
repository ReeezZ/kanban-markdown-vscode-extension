---
id: "clickable-links"
status: "backlog"
priority: "medium"
assignee: null
epic: "03 Card Editing"
dueDate: null
created: "2026-10-23T15:04:03.000Z"
modified: "2026-10-23T15:04:03.000Z"
completedAt: null
labels: ["feature", "webview"]
order: "a6"
---
# Links in a card open

**Goal:** a link in a card body opens when I click it: a web link in the browser, a relative `.md` link in the editor. Upstream issues #64 and #68.

**Cause:** link clicks don't reach the host: `src/` has no `openExternal` call or link message. The host has to open them (`vscode.env.openExternal` for web links, a text document for a relative path).

**Done when**

- [ ] clicking an `http(s)` link opens it in the browser
- [ ] clicking a relative `.md` link opens that file in the editor
- [ ] other schemes are not opened
- [ ] a message type for it in `src/shared/types.ts`, with a test of the target resolution

**Open questions**

- Which schemes are allowed: `http`, `https`, `mailto` only?
- Does a relative link to a card open the file, or the card on the board?
- Click, or Ctrl/Cmd+click, since the editor is editable?

**Needs:** none