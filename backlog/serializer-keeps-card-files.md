---
id: "serializer-keeps-card-files"
status: "backlog"
priority: "medium"
assignee: null
epic: "03 Card Editing"
dueDate: null
created: "2026-10-23T15:04:03.000Z"
modified: "2026-10-23T15:04:03.000Z"
completedAt: null
labels: ["bug", "extension"]
order: "a5"
---
# Saving a card keeps the rest of the file

**Goal:** when I edit a card on the board, `git diff` shows only what I changed. Nothing in the file is lost or rewritten on the way.

**Cause** (the handoff has this partly wrong):

- The body trim is in the parser, not the serializer: `src/shared/featureFrontmatter.ts:37`, `body.trim()`. It drops the trailing newline of the file.
- `modified` is bumped by the `KanbanPanel` callers (L612, 678, 791, 878, 1003, 1030), not by `serializeFeature`.
- The serializer (`featureFrontmatter.ts:42-61`) drops unknown frontmatter fields. That is why dependencies are a `**Needs:**` line in the body ([Backlog](../docs/CLAUDE.md#backlog)).

This touches persistence and the card file format, so it gets a spec first, with a plan before any code.

**Done when**

- [ ] a spec says what is kept: unknown fields, the trailing newline, `modified`
- [ ] an unknown frontmatter field survives a save from the board
- [ ] a save changes only the fields that were edited (tests on parse and serialize)
- [ ] the change is self-contained and doesn't break old card files

**Open questions**

- Where do unknown fields go in the output: after `order`, or in their original place?
- Should a drag, which only changes `order`, bump `modified` at all?
- Does the body round-trip belong here or in [`markdown-round-trip-spike`](markdown-round-trip-spike.md)?
- Does the fix change files for upstream users? The format is shared, so this may need an upstream issue first.

**Needs:** none