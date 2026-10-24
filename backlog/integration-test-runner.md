---
id: "integration-test-runner"
status: "backlog"
priority: "low"
assignee: null
epic: "XX Infra v2"
dueDate: null
created: "2026-10-24T19:07:56.000Z"
modified: "2026-10-24T19:07:56.000Z"
completedAt: null
labels: ["chore", "infra"]
order: "af"
---
# Run the integration tests with @vscode/test-cli

The integration tests use a custom runner (`tests/integration/runTests.ts`) on `@vscode/test-electron` 2. The docs' recommended setup is `@vscode/test-cli` with `@vscode/test-electron` 3, both on Node 22, which the devcontainer already has. It adds a `.vscode-test.mjs` config, coverage for the integration tests (c8, a flag the README doesn't document yet), and running them from the Test Explorer through the Extension Test Runner extension. Open: whether that is worth a dependency change, and whether the runner's `launchArgs` (fixture workspace, `--disable-extensions`, `--disable-workspace-trust`) carry over.
