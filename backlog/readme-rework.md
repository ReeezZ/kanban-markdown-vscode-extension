---
id: "readme-rework"
status: "backlog"
priority: "high"
assignee: null
epic: "01 Foundation"
dueDate: null
created: "2026-10-23T16:30:00.000Z"
modified: "2026-10-23T16:30:00.000Z"
completedAt: null
labels: ["chore", "infra"]
order: "a0V"
---
# README rework

**Goal:** the README presents the fork under its provisional name as its own project, with the credit to upstream, instead of reading as upstream's page.

It opens with a short section: what the fork is (a personal project, in progress), that it's forked from LachyFS/kanban-markdown-vscode-extension (linked), what it changes or plans to, and a link to the roadmap. Upstream's feature docs stay below it while they still fit. The README is also the Marketplace page, so it gets no dev workflow (see [Fork and upstream](../CLAUDE.md#fork-and-upstream)).

**Done when**

- [ ] the README opens with the fork section and the credit
- [ ] the title, badges and image links no longer claim upstream's Marketplace, Open VSX and star counts as the fork's
- [ ] its image and doc links still resolve
- [ ] `LICENSE` still carries the original copyright line

**Open questions**

- Keep upstream's badges (in a credit line) or drop them until the fork is published?

**Needs:** [`provisional-name`](provisional-name.md)
