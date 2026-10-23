---
id: "fork-name-and-publisher"
status: "backlog"
priority: "medium"
assignee: null
epic: "05 Publish"
dueDate: null
created: "2026-10-23T15:04:03.000Z"
modified: "2026-10-23T18:43:18.000Z"
completedAt: null
labels: ["chore", "infra"]
order: "aB"
---
# Name and publisher of the fork

**Goal:** the fork has its own name and publisher, so it doesn't collide with `LachyFS.kanban-markdown` and can be published.

The provisional name is chosen in [`provisional-name`](done/provisional-name.md) and the README presents it ([`readme-rework`](readme-rework.md)); this card confirms it and registers it. Until the publisher is registered, the name is only text. The settings prefix stays `kanban-markdown.*` until [`settings-prefix`](settings-prefix.md).

- The Marketplace ID is `publisher.name`. The publisher ID can't be changed after creation, and names of removed extensions stay reserved. Pick the publisher with care (a name or handle).
- The provisional name is Markan; the checks behind it and the names dropped are in [`provisional-name`](done/provisional-name.md). The bar for a name: distinct and honest, with no live product, extension or domain with users in the same niche (tiny hobby repos are fine). "Kanban" may appear in the display name or tagline ("Markan – Markdown Kanban board"), "Kanban Markdown" may not. The search can't show reserved names; the real check is `vsce publish`.
- `launch.json` gets `--disable-extension=LachyFS.kanban-markdown`, so the installed original doesn't run next to the fork in the Extension Development Host.

**Done when**

- [ ] `name`, `displayName`, `publisher` and `repository` (the fork's URL) are set in `package.json`
- [ ] `launch.json` disables the original extension
- [ ] the README and the repository name match the confirmed name
- [ ] `pnpm package` builds a `.vsix` under the new name

**Open questions**

- Keep the provisional name, or change it? And the publisher ID.

**Needs:** [`provisional-name`](done/provisional-name.md)