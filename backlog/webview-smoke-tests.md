---
id: "webview-smoke-tests"
status: "backlog"
priority: "low"
assignee: null
epic: "XX Infra Future"
dueDate: null
created: "2026-10-24T19:07:56.000Z"
modified: "2026-10-24T19:07:56.000Z"
completedAt: null
labels: ["idea", "webview"]
order: "ag"
---
# Smoke tests that drive the real webview

Today each side of the host↔webview messages is tested on its own; nothing drags a card in a real VS Code. A few end-to-end tests could, with ExTester (Red Hat, the most active), Playwright on Electron (used by VS Code's own smoke tests and GitLens) or wdio-vscode-service. Open: whether any of them is worth its setup weight (a browser driver, xvfb in CI) for a single-developer project.
