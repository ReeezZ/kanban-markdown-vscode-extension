---
id: "fork-name-and-publisher"
status: "backlog"
priority: "medium"
assignee: null
epic: "04 Publish"
dueDate: null
created: "2026-10-23T15:04:03.000Z"
modified: "2026-10-23T15:04:03.000Z"
completedAt: null
labels: ["chore", "infra"]
order: "aB"
---
# Name and publisher of the fork

**Goal:** the fork has its own name and publisher, so it doesn't collide with `LachyFS.kanban-markdown` and can be published.

- The Marketplace ID is `publisher.name`. The publisher ID can't be changed after creation, and names of removed extensions stay reserved. Pick the publisher with care (a name or handle).
- The name only has to be distinct and honest. Shortlist (checked 2026-10-23 on the Marketplace, Open VSX and npm): Laneboard (top pick), Swimdeck, Plainboard, MD Lanes, Diffboard, Cardshelf. Keep "Kanban Markdown" out of the display name. The search can't show reserved names; the real check is `vsce publish`.
- `launch.json` gets `--disable-extension=LachyFS.kanban-markdown`, so the installed original doesn't run next to the fork in the Extension Development Host.
- `LICENSE` keeps the original copyright line.

**Done when**

- [ ] `name`, `displayName` and `publisher` are set in `package.json`
- [ ] `launch.json` disables the original extension
- [ ] the fork credit to Kanban Markdown is written down
- [ ] `pnpm package` builds a `.vsix` under the new name

**Open questions**

- The final name and publisher ID.
- Where does the credit go, since the root README is upstream's and stays as it is?

**Needs:** none