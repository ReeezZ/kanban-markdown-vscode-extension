---
id: "label-colours"
status: "backlog"
priority: "medium"
assignee: null
epic: "03 Board Polish"
dueDate: null
created: "2026-10-23T15:04:03.000Z"
modified: "2026-10-23T15:04:03.000Z"
completedAt: null
labels: ["feature", "webview"]
order: "a8"
---
# Label colours

**Goal:** I can give a label a colour in the Label Manager, and the board shows it. Upstream issue #74.

**Cause:** labels have no colour. `LabelManager.tsx` only renames and deletes. Epics already have a light and dark colour approach in `src/shared/epicColor.ts`; copy it. Store the choice in a `labelColors` setting and use a hash of the name as the fallback.

The setting is a change to the `contributes.configuration` schema, so propose it before building. The new UI strings need en, es and pt entries.

**Done when**

- [ ] a colour can be picked per label in the Label Manager
- [ ] it is stored in the `labelColors` setting and read back after a reload
- [ ] a label without a colour gets a stable hash colour, in light and dark themes
- [ ] a test covers the colour lookup and the fallback

**Open questions**

- Fixed palette or a free colour picker?
- Setting key prefix: build with the current one; [`settings-prefix`](settings-prefix.md) renames it, and `labelColors` is one of the settings it will rename.

**Needs:** none