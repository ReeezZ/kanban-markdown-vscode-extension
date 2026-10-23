---
id: "publish-extension"
status: "backlog"
priority: "medium"
assignee: null
epic: "04 Publish"
dueDate: null
created: "2026-10-23T15:04:03.000Z"
modified: "2026-10-23T15:04:03.000Z"
completedAt: null
labels: ["chore", "infra"]
order: "aE"
---
# Publish the extension

**Goal:** the fork can be installed from the Marketplace and Open VSX under its own ID.

Steps from the handoff:

- Marketplace: Microsoft account, Azure DevOps organisation, publisher, then `vsce publish`. Azure DevOps retires global PATs on 2026-12-01, so use Entra ID (`vsce publish --azure-credential`) after that date.
- Open VSX: GitHub login, an Eclipse account, the Publisher Agreement, an access token, `ovsx create-namespace`, `ovsx publish`.
- No tag goes to origin before the name and publisher are set; see [Releases](../docs/git-workflow.md#releases).
- vsce doesn't read `.gitignore`, so anything new and untracked in the repo root ends up in the `.vsix` unless `.vscodeignore` excludes it.
- After publishing, swap the extension ID in `.devcontainer/devcontainer.json` and in guitar_companion.

**Done when**

- [ ] the Marketplace and Open VSX accounts and publisher are set up
- [ ] `.vscodeignore` is checked with `pnpm exec vsce ls --no-dependencies`
- [ ] `release.yml` publishes under the new name, and the tag scheme is written down
- [ ] the first release is installable from both registries
- [ ] the devcontainer installs the fork instead of the original

**Open questions**

- The tag scheme: upstream's `v*` tags, or a prefix that can't clash with them, so `upstream/main` merges stay clean?
- Does the release workflow publish on its own, or stay manual for now?

**Needs:** [`fork-name-and-publisher`](fork-name-and-publisher.md), [`settings-prefix`](settings-prefix.md)