---
id: "fake-vscode-contract-tests"
status: "backlog"
priority: "low"
assignee: null
epic: "01 Foundation"
dueDate: null
created: "2026-10-24T19:07:56.000Z"
modified: "2026-10-24T19:07:56.000Z"
completedAt: null
labels: ["chore", "extension"]
order: "ad"
---
# Check the fake vscode module against real VS Code

The panel tests run on `tests/extension/fakeVscode.ts`, which encodes assumptions nothing checks: whether `writeFile` creates missing parent folders, whether `rename` onto an existing file throws, the shape of `readDirectory`, and when watcher events arrive relative to a `rename`. A few integration tests in a real VS Code would pin them; the last one also settles whether `_migrating` drops anything in practice. Open: whether the fake is changed where VS Code differs, or the difference is documented.
