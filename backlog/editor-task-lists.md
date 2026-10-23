---
id: "editor-task-lists"
status: "backlog"
priority: "medium"
assignee: null
epic: "03 Card Editing"
dueDate: null
created: "2026-10-23T15:04:03.000Z"
modified: "2026-10-23T15:04:03.000Z"
completedAt: null
labels: ["feature", "webview"]
order: "a7"
---
# Task lists in the editor

**Goal:** `- [ ]` items in a card body show as checkboxes that I can tick in the editor, and are saved as Markdown task lists. Upstream issue #59. These cards' own "Done when" lists are task lists.

**Cause:** the editor is `StarterKit`, `Placeholder` and `tiptap-markdown` 0.9 (`FeatureEditor.tsx:3-5`, `:549-551`), with no TaskList or TaskItem extension.

This needs a new TipTap dependency (`@tiptap/extension-task-list` and `-task-item`), so it starts with a short plan and a check of the package, not an install.

**Done when**

- [ ] a plan names the package, version and its maintenance state
- [ ] a task list renders with checkboxes and can be ticked
- [ ] the saved Markdown is `- [ ]` and `- [x]`, and an untouched list round-trips unchanged
- [ ] a test covers parse and serialize of a task list

**Open questions**

- Does `tiptap-markdown` 0.9 write the task list syntax back correctly, Use the result of [`markdown-round-trip-spike`](markdown-round-trip-spike.md) if it exists by then.

**Needs:** none