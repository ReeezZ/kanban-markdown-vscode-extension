---
name: branch
description: Use whenever starting work that needs a branch (any feature, fix, docs or chore change beyond a tiny docs fix or a backlog refinement), before the first edit. Creates the branch off main, in the main checkout or its own worktree, and gives the /rename line.
argument-hint: "[card-id | <type>/<short-description>]  (e.g. card-filters, or feat/board-search)"
---

Start the branch `$ARGUMENTS`. Background and the reasons are in [Branches and merges](../../../docs/git-workflow.md#branches-and-merges) in `docs/git-workflow.md`.

1. **Card.** Use the card that `$ARGUMENTS` or the conversation names, or one in `backlog/` whose title (`# ` line) fits; ask only if two could fit. If the card's `status` isn't `ready` (or `in-progress`, for a later slice), say so and offer `/refine`; a note, not a stop. If none fits, go on without one. Offer `/park` only when the work will outlast this branch and should stay on the board.
2. **Name.** With a card: `<type>/<card-id>`, with a type from the commit table in `docs/git-workflow.md`; a card built in several branches gets a slice suffix, `<type>/<card-id>-<slice>`. Without one: `<type>/<short-description>`. If `$ARGUMENTS` is empty or has no valid type, propose a name and ask. Keep the word "git" out of the description: a session that switched into a worktree refuses any command naming git twice, so `git branch -m chore/git-skills …` is rejected there.
3. **Where.** Run `git worktree list` and `git branch --show-current`.
   - Worktree, without asking: the main checkout isn't on `main` or isn't clean, another agent works in it, or the user asked for one. Untracked character devices in `git status` don't count as unclean: they're the sandbox's placeholders for blocked paths, see [Devcontainer](../../../docs/development.md#devcontainer).
   - Exception: when the uncommitted changes are this branch's own work, branch in the main checkout instead, since a worktree off `main` wouldn't carry them.
   - Otherwise ask with AskUserQuestion, your recommendation first. Recommend by the work expected, not the branch type: several commits, a longer stretch, or test runs along the way → worktree, so the main checkout stays free meanwhile; a change done in a few minutes → main checkout. The type is only a hint (`fix` and `chore` tend to be small, `feat`, `docs` and `refactor` larger). Name the trade-off in the options: a worktree needs its own install of the dependencies, and the integration tests download VS Code into `.vscode-test/` (about 160 MB per worktree). There is no dev server, so no port conflict.
   - Main checkout: `git switch -c <name> main`. Worktree: `git worktree add .claude/worktrees/<short-description> -b <name> main`, then switch into it with EnterWorktree's `path` (never by `name`, see [Git](../../../CLAUDE.md#git) in the root `CLAUDE.md`). The `post-checkout` hook installs the dependencies.
   - If it's unclear whether someone else is working in the main checkout, ask.
4. **Start the card.** In the branch's checkout, set the card's `status: "in-progress"` and `modified` if it isn't already, and commit just that card as `docs(backlog): start <card-id>`, before any code. It's its own commit so the code commits cherry-pick onto upstream without `backlog/` ([Fork and upstream](../../../CLAUDE.md#fork-and-upstream)). In a worktree, the board in the main checkout shows it only after the merge. Skip this when the card is `in-progress` already (a later slice).
5. **Hand over.** Print `/rename <name>` for the user to paste (the agent can't rename the session).
