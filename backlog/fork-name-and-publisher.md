---
id: "fork-name-and-publisher"
status: "backlog"
priority: "high"
assignee: null
epic: "05 Publish"
dueDate: null
created: "2026-10-23T15:04:03.000Z"
modified: "2026-10-23T18:07:50.000Z"
completedAt: null
labels: ["chore", "infra"]
order: "aB"
---
# Name and publisher of the fork

**Goal:** the fork has its own name and publisher, so it doesn't collide with `LachyFS.kanban-markdown` and can be published.

The provisional name is chosen in [`provisional-name`](provisional-name.md) and the README presents it ([`readme-rework`](readme-rework.md)); this card confirms it and registers it. Until the publisher is registered, the name is only text. The settings prefix stays `kanban-markdown.*` until [`settings-prefix`](settings-prefix.md).

- The Marketplace ID is `publisher.name`. The publisher ID can't be changed after creation, and names of removed extensions stay reserved. Pick the publisher with care (a name or handle).
- The name only has to be distinct and honest. Shortlist (checked 2026-10-23 on the Marketplace, Open VSX and npm): Laneboard (top pick), Swimdeck, Plainboard, MD Lanes, Diffboard, Cardshelf. Keep "Kanban Markdown" out of the display name. The search can't show reserved names; the real check is `vsce publish`.
- `launch.json` gets `--disable-extension=LachyFS.kanban-markdown`, so the installed original doesn't run next to the fork in the Extension Development Host.

**Done when**

- [ ] `name`, `displayName`, `publisher` and `repository` (the fork's URL) are set in `package.json`
- [ ] `launch.json` disables the original extension
- [ ] the README and the repository name match the confirmed name
- [ ] `pnpm package` builds a `.vsix` under the new name

**Open questions**

- Keep the provisional name, or change it? And the publisher ID.

**Needs:** [`provisional-name`](provisional-name.md)