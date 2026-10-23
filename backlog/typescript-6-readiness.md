---
id: "typescript-6-readiness"
status: "backlog"
priority: "low"
assignee: null
dueDate: null
created: "2026-10-23T21:37:01.000Z"
modified: "2026-10-23T21:37:01.000Z"
completedAt: null
labels: ["chore", "infra"]
order: "aI"
epic: "01 Foundation"
---
# TypeScript 6 readiness

VS Code ships TypeScript 6.0; the repo builds with 5.9. Under 6.0 the root `tsconfig.json` fails: `types` defaults to `[]`, so `@types/node` isn't loaded (`Cannot find name 'crypto'`), and `baseUrl` is deprecated (removed in 7.0; `paths` works without it). Workaround for now: "TypeScript: Select TypeScript Version → Use Workspace Version".

Open: which `types` the root and integration tsconfigs need, and whether to bump `typescript` itself. `tsconfig.json` is upstream's file.
