---
id: "editor-direction-spike"
status: "backlog"
priority: "low"
assignee: null
epic: "XX Editor v2"
dueDate: null
created: "2026-10-24T11:24:53.000Z"
modified: "2026-10-24T11:24:53.000Z"
completedAt: null
labels: ["idea", "webview"]
order: "aN"
---
# Editor direction spike

Decide what the card editor is built on. Worth keeping: the pickers for priority, epic and labels, and room for link suggestions to other cards. Not worth keeping: the TipTap rich-text body, which converts Markdown on every load and save and whose Ctrl/Cmd+B clashes with VS Code's. The split view next to the board is wanted, but VS Code's own split works as well.

Options, the first to try first:

- The body in VS Code's own Markdown editor (`markdownEditorMode` already opens it beside the board) and the fields in a small webview next to it; upstream's unused `src/extension/FeatureHeaderProvider.ts` sketches that view. Link suggestions become a completion provider.
- A `CustomTextEditorProvider` per card file.
- Keep the webview's own copy of the card and fix it.

Upstream asks for two things a direction should allow: card details in the sidebar while the main editor stays in use (issue #67), and images in a card body (issue #52).

The result goes into the Decisions of `docs/architecture.md`, together with why the board is a webview (a two-dimensional layout with drag and drop no native view can draw; rejected: a tree view per status, a custom editor for the board, which binds to one file). Related: [`editor-save-overwrites-other-card`](editor-save-overwrites-other-card.md) (its fix doesn't wait for this), [`markdown-round-trip-spike`](markdown-round-trip-spike.md), [`serializer-keeps-card-files`](serializer-keeps-card-files.md), [`proper-links-and-link-types-2026-10-23`](proper-links-and-link-types-2026-10-23.md), [`clickable-links`](clickable-links.md).
