[README](../README.md) › Roadmap

# Roadmap

A personal fork of [Kanban Markdown](https://github.com/LachyFS/kanban-markdown-vscode-extension), the VS Code extension that shows Markdown files as a board. The fork fixes card ordering in the epic view, then improves card editing and board polish, and is eventually published under its own name. Fixes that upstream could take stay self-contained commits, so they can be offered as PRs (see [Upstream](git-workflow.md#upstream)). What each part of this doc holds is under [Roadmap](CLAUDE.md#roadmap).

## Shipped

Nothing yet.

## Open phases

### Phase 1: Ordering Fixes

Goal: dragging a card keeps its place, also in the epic view, and a bad order key can't break a drag.

Why now: the epic view is the reason for the fork, and until `equal-order-keys` ships every `order` key must be unique across the board. The two fixes are also the best test of whether the codebase is easy to work in. They stay self-contained commits, so they can go upstream as PRs.

Done when:

- [ ] a drop in a lane keeps its position after reload;
- [ ] equal keys no longer throw, and errors are visible;
- [ ] both have unit tests;
- [ ] the fixes are self-contained commits;
- [ ] the extension and webview area docs exist;
- [ ] F5 opens a sample board to drag on, and a drag there leaves only the moved card changed in `git diff`.

### Phase 2: Card Editing

Goal: the card editor matches the board: the status list comes from the configured columns, links open, task lists work, and saving a card doesn't lose data.

Why now: the editor is where the daily friction is, and these are small upstream-able fixes. The serializer work needs a spec first because it touches persistence.

Done when:

- [ ] the status dropdown lists the configured columns;
- [ ] a save from the board changes nothing but what was edited;
- [ ] links in a card open, and task lists render and save.

### Phase 3: Board Polish

Goal: smaller board features: label colours, send a card to the top or bottom, and rules for dropping into a column.

Why now: after the editing fixes, and the send-to-top/bottom work builds on the lane order from Phase 1.

Done when:

- [ ] a label has a colour that is set in one place and shown on the board;
- [ ] a card can be sent to the top or bottom of its lane;
- [ ] a column can be set to refuse drops.

### Phase 4: Publish

Goal: the fork has its own name, publisher and settings prefix, and is published on the Marketplace and Open VSX.

Why now: last, because the name and publisher ID can't be changed once created, and publishing is worth more once the fixes are in. When a `v*` tag may go to origin is in [Releases](git-workflow.md#releases).

Done when:

- [ ] settings and commands use the fork's own prefix;
- [ ] the extension installs from the Marketplace under its own ID;
- [ ] the changelog covers the fork's releases.
