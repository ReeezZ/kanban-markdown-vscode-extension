---
id: "readme-rework"
status: "ready"
priority: "high"
assignee: null
epic: "01 Foundation"
dueDate: null
created: "2026-10-23T16:30:00.000Z"
modified: "2026-10-23T20:00:00.000Z"
completedAt: null
labels: ["chore", "infra"]
order: "a0V"
---
# README rework

**Goal:** someone opening the repo or (later) the Marketplace page sees Markan, a personal fork in progress, with its credit to upstream, and not upstream's page with upstream's numbers.

**Done when**

- [ ] the title is Markan with "Kanban" in the tagline, followed by a short fork section: a personal project in progress, forked from LachyFS/kanban-markdown-vscode-extension (linked, with its Marketplace page), what it changes or plans to, and a link to the roadmap
- [ ] upstream's Marketplace, Open VSX, downloads, stars and CI badges are gone; License and the agent badges stay
- [ ] Quick Start and Installation say the fork isn't published yet and how to build and install a `.vsix` (`pnpm package`), with a pointer to upstream for the published original
- [ ] the Development section is one line linking [docs/development.md](../docs/development.md) and CONTRIBUTING; what it said about the test suites that development.md lacks moves there, and the two `README.md#testing` links (root `CLAUDE.md`, `docs/development.md`) point to the new place
- [ ] the icon and screenshot URLs point at `ReeezZ/kanban-markdown-vscode-extension/main` and load
- [ ] upstream's feature sections, Kanban Skill, Contributors and License stay; `LICENSE` still carries the original copyright line
- [ ] `./scripts/docs_check.py --check` passes

**Out of scope:** `package.json` (`name`, `displayName`, `publisher`, `repository`), the fork's own badges and Marketplace install, which are [`fork-name-and-publisher`](fork-name-and-publisher.md) and [`publish-extension`](publish-extension.md); `CHANGELOG.md` ([`changelog-catch-up`](changelog-catch-up.md)).

Built directly, no spec. One branch.

**Needs:** [`provisional-name`](done/provisional-name.md)
