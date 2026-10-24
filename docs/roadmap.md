[README](../README.md) › Roadmap

# Roadmap

A personal fork of [Kanban Markdown](https://github.com/LachyFS/kanban-markdown-vscode-extension), the VS Code extension that shows Markdown files as a board. The fork fixes card ordering in the epic view, then improves card editing and board polish, and is eventually published under its own name, which is set early so the README can present the fork as its own. Upstream PRs are a nice-to-have (see [Upstream](git-workflow.md#upstream)). What each part of this doc holds is under [Roadmap](CLAUDE.md#roadmap).

## Discontinued

The fork was discontinued on 2026-10-24, after the baseline tests. Phase 1 was partly done: the area docs and the baseline tests exist, but the review findings weren't sorted into cards and the name wasn't confirmed. Nothing was published.

Why: the fork was meant to be the task board for an agent workflow. Keeping the backlog as files in the repo turned out to be the wrong place for that once the workflow gets more agentic, with several agents working in parallel:

- A board has to be a singleton: one shared state of every task that everyone, person or agent, reads and changes. Files in git aren't one. Each branch and worktree has its own copy of every card, so an agent in a worktree sees the board as it was when its branch was made, and a status change made there only reaches the others after a merge.
- Every status change is a commit. With one agent at a time that's overhead; with several in parallel it means merge conflicts on the card files.
- Agents working in parallel have to claim a task before starting it, so two don't pick the same one. That needs a shared state that changes at once; in git, every claim would have to go through `main` first.
- Triggers (a label or status that starts a run) and agents running elsewhere need the board where they can reach it, outside the local checkout.

A shared tracker (GitHub Issues) provides all of this, so tasks move there. Specs stay in the repo, where they are versioned with the code they describe. The work on the agent workflow continues in another project.

The phases below and the cards in `backlog/` stay as they were left, as a record. They won't be worked on.

## Shipped

Nothing yet.

## Phases not pursued

### Phase 1: Foundation

Goal: the codebase is understood and safe to change before any fix or feature: it is documented, has baseline tests, has been reviewed, and the fork has a provisional name.

Why now: the code quality is uneven and `KanbanPanel.ts` has no tests around moves, so the fixes would be built on guesses. The review's findings decide which refactors come before the fixes.

Done when:

- [ ] the extension and webview area docs exist;
- [ ] the move and order logic and the move message have baseline tests;
- [ ] the review passes are done, their findings are cards, and the refactors chosen to come first are done;
- [ ] a provisional name (Markan) is chosen and the README presents the fork under it.

### Phase 2: Ordering Fixes

Goal: dragging a card keeps its place, also in the epic view, and a bad order key can't break a drag.

Why now: the epic view is the reason for the fork, and until `equal-order-keys` ships every `order` key must be unique across the board. The two fixes are also the best test of whether the codebase is easy to work in.

Done when:

- [ ] a drop in a lane keeps its position after reload;
- [ ] equal keys no longer throw, and errors are visible;
- [ ] both have unit tests;
- [ ] F5 opens a sample board to drag on, and a drag there leaves only the moved card changed in `git diff`.

### Phase 3: Card Editing

Goal: the card editor matches the board: the status list comes from the configured columns, links open, task lists work, and saving a card doesn't lose data.

Why now: the editor is where the daily friction is, and these are small fixes. The serializer work needs a spec first because it touches persistence.

Done when:

- [ ] the status dropdown lists the configured columns;
- [ ] a save from the board changes nothing but what was edited;
- [ ] links in a card open, and task lists render and save.

### Phase 4: Board Polish

Goal: smaller board features: label colours, send a card to the top or bottom, and rules for dropping into a column.

Why now: after the editing fixes, and the send-to-top/bottom work builds on the lane order from Phase 2.

Done when:

- [ ] a label has a colour that is set in one place and shown on the board;
- [ ] a card can be sent to the top or bottom of its lane;
- [ ] a column can be set to refuse drops.

### Phase 5: Publish

Goal: the fork has its own name, publisher and settings prefix, and is published on the Marketplace and Open VSX.

Why now: last, because the publisher ID can't be changed once created, and publishing is worth more once the fixes are in. The name is chosen provisionally in Phase 1 so there is time to doubt it; it is confirmed and registered here, together with the publisher and the settings prefix. When a `v*` tag may go to origin is in [Releases](git-workflow.md#releases).

Done when:

- [ ] settings and commands use the fork's own prefix;
- [ ] the extension installs from the Marketplace under its own ID;
- [ ] the changelog covers the fork's releases.
