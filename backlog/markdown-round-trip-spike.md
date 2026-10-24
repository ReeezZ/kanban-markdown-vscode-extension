---
id: "markdown-round-trip-spike"
status: "backlog"
priority: "low"
assignee: null
epic: "XX Editor v2"
dueDate: null
created: "2026-10-23T15:04:03.000Z"
modified: "2026-10-23T15:04:03.000Z"
completedAt: null
labels: ["idea", "webview"]
order: "aF"
---
# Markdown round-trip spike

**Goal:** find out how to stop the editor from rewriting a card body it didn't change, and what else makes the editor feel immature. Time-boxed.

**Cause:** `tiptap-markdown` 0.9 re-serialises the whole body on save, so formatting that differs from its output changes. The repo uses TipTap 3 already. Overlaps with the body part of [`serializer-keeps-card-files`](serializer-keeps-card-files.md).

Options to try:

- TipTap's official Markdown extension.
- Keep the body unchanged when it wasn't edited.

If [`editor-direction-spike`](editor-direction-spike.md) moves the body to VS Code's own editor, the round trip no longer matters for the body.

The spike also covers the general "the editor feels immature" complaint: collect concrete items and turn each into a card.

**Done when**

- [ ] a short written result: which option, with the diff noise it leaves on real cards
- [ ] concrete editor items parked as cards
- [ ] this card is deleted or becomes a numbered phase

**Open questions**

- Is the official extension stable enough to replace `tiptap-markdown`? Check maintenance first, since it is a new dependency.
- Which editor items are worth a phase at all?

**Needs:** none