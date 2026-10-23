---
id: "area-docs-baseline"
status: "in-progress"
priority: "high"
assignee: null
epic: "01 Foundation"
dueDate: null
created: "2026-10-23T15:04:03.000Z"
modified: "2026-10-23T18:00:00.000Z"
completedAt: null
labels: ["chore", "workflow"]
order: "a0"
---
# Area docs baseline

**Goal:** a developer or agent can read how the extension and the webview work today, at the level of concepts, flows and edge rules, before touching the ordering code, instead of reverse-engineering `KanbanPanel.ts`.

Write two area docs and link them from [Building blocks](../docs/architecture.md#building-blocks):

- `docs/areas/extension.md`: the host: the message switch, move and order, file watching (including how it tells its own writes from external ones), the sidebar view and the header provider.
- `docs/areas/webview.md`: the store, drag and drop, the editor.

The docs explain what the code can't say on its own: how the parts fit together, why, and the edge rules. Diagrams where they replace text (for example the drag, write, watch and refresh loop, and the host and webview messages). No code listings. The card format stays in the architecture Decisions, which the extension doc links to.

**Done when**

- [ ] both area docs exist, in the style of the doc rules, with the diagrams rendered and checked
- [ ] each is linked from Building blocks, replacing the "will be linked" sentence there
- [ ] the text was checked against the code, not against the handoff
- [ ] `./scripts/docs_check.py --check` passes

**Out of scope:** tests and refactoring.

No spec: this is docs only, so it can be built directly. It is a lot of code to read (`KanbanPanel.ts` is about 1200 lines, the webview about 3000); if it overruns, the extension doc goes first, since the ordering fixes need it.

**Needs:** none
