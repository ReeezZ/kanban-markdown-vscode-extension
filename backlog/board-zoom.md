---
id: "board-zoom"
status: "backlog"
priority: "low"
assignee: null
epic: "XX Board Future"
dueDate: null
created: "2026-10-24T12:49:39.000Z"
modified: "2026-10-24T12:49:39.000Z"
completedAt: null
labels: ["enhancement", "webview"]
order: "aU"
---
# Board zoom setting

A zoom or font size setting for the board only, so its text can match the editor's. Upstream issue #6; upstream PR #73 (unmerged) has the code: a `zoomLevel` setting passed to the webview as a CSS variable, applied live.

Open: the PR adds a `contributes.configuration` key (a risky area; the prefix comes from [`settings-prefix`](settings-prefix.md)) and allows inline styles in the CSP.
