---
id: "editor-save-overwrites-other-card"
status: "backlog"
priority: "high"
assignee: null
epic: "02 Ordering Fixes"
dueDate: null
created: "2026-10-23T23:32:39.000Z"
modified: "2026-10-23T23:32:39.000Z"
completedAt: null
labels: ["bug", "webview"]
order: "aM"
---
# Editor save overwrites another card

Opening card B within 800 ms of an edit to card A writes B's body into A's file, with B's fields after a body edit and A's fields after a field edit. The save timers in `FeatureEditor.tsx` (`:562-564`, `:606-609`) keep the `onSave` of the card they started on, the editor has no `key` per card (`App.tsx:384`), and `featureContent` doesn't cancel them. Found by reading, not yet reproduced in the running app.

Reproduced manually on 2026-10-24 by the user

Same code path, still open: every `featureContent` replaces unsaved edits without a check, and a stale field timer can then revert a drag's status. The fix probably covers all three, so how is open. See [Card editor in the webview doc](../docs/areas/webview.md#card-editor).

Found while pinning moves in [`baseline-tests`](done/baseline-tests.md): `_lastWrittenContent` only knows editor saves, so dragging the open card makes the watcher send `featureContent`, which then replaces unsaved edits; after a drag across the `done` boundary the watcher event carries the old path, so the open card isn't refreshed at all.
