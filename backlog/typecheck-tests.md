---
id: "typecheck-tests"
status: "backlog"
priority: "low"
assignee: null
epic: "01 Foundation"
dueDate: null
created: "2026-10-24T19:07:56.000Z"
modified: "2026-10-24T19:07:56.000Z"
completedAt: null
labels: ["chore", "infra"]
order: "ae"
---
# Typecheck and lint the tests

`pnpm typecheck` and `pnpm lint` cover `src/` only, so a type error in `tests/` shows up only when Vitest runs it, and the fake `vscode` module can't be typed against `@types/vscode` to catch drift. Bring `tests/` in, through its own tsconfig or the existing one. Open: how many errors the existing upstream tests raise, and whether fixing them means touching upstream files.
