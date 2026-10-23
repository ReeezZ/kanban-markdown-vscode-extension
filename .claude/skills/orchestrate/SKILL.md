---
name: orchestrate
description: Use when the user has confirmed orchestrator mode for an approved spec or plan. This Opus session hands each step to a Sonnet subagent, reviews the diff, fixes small things, runs checks and commits, then gives one summary at the end.
argument-hint: "[spec path or plan]  (default: the plan approved in this session)"
---

Carry out `$ARGUMENTS` (default: the plan approved in this session) as orchestrator: this session splits the work into steps, hands each to a Sonnet subagent, reviews what comes back and commits it. When the mode fits is in [Model choice](../../../CLAUDE.md#model-choice) in `CLAUDE.md`.

## 1. Before the first step

- The system prompt must name an Opus model. `opusplan` drops to Sonnet after plan approval, so on Sonnet ask the user for `/model opus` and stop.
- The work happens on a branch started with `/branch`.
- Steps come from the spec's Implementation order, or from the approved plan. One step is one commit.
- Steps run one after another in one checkout. Run steps in parallel only when they touch separate folders (e.g. two parts of the app once the interface between them is fixed), each subagent with the Agent tool's `isolation: "worktree"`. The project sets `worktree.baseRef` to `head`, so its worktree branches from the current HEAD (this session's worktree's HEAD when it runs in one): commit everything before starting it, since uncommitted changes don't come along. The subagent commits in its worktree; review that branch, then bring it onto the working branch with `git cherry-pick`. The parallel path hasn't been run yet; say so when choosing it.

## 2. Each step

- **Brief** (Agent tool, `model: sonnet`): the spec link and which step, the files it should touch, the step's done-means, and to run the checks of the area it changes (see [Checks](../../../docs/development.md#checks) in `docs/development.md`) before handing back. It doesn't commit (except in a parallel worktree, see above); it reports the changed files and the check results. Folder CLAUDE.md files load for subagents by themselves, so the brief doesn't repeat them.
- **Tests and code from separate subagents** ([Testing](../../../CLAUDE.md#testing) in `CLAUDE.md`):
  - Domain logic with a clear pass/fail (pure logic, no UI): a first subagent writes the tests from the spec's Tests section and confirms they fail; a second implements until they pass, without changing the tests.
  - UI steps: the code first, then a second subagent writes the e2e test in `tests/integration/`, or a component test where that fits; otherwise the user checks the result.
- **Review**: read the diff and check it against the step's done-means and the spec's Decisions. Fix small things yourself. If the approach is wrong, start a new subagent with a sharper brief instead of patching around it.
- **Commit** the step. The commit's permission prompt is the user's review of that step.
- If a step turns up an open design question, stop and ask the user; don't leave it to a subagent.

## 3. End of the run

- If the work has a card, the last step's commit finishes it as "Finished" in the [Backlog section of `docs/CLAUDE.md`](../../../docs/CLAUDE.md#backlog) describes, unless the branch is a slice that isn't the card's last.
- If the branch touches `src/extension/`, `src/shared/` or `tests/integration/`, start the e2e suite as [Testing](../../../CLAUDE.md#testing) in `CLAUDE.md` describes: `pnpm run build:extension && xvfb-run -a pnpm run test:integration`, as that one call so the sandbox exclusion in `.claude/settings.json` matches.
- One summary: each step with its commit, what you fixed yourself or had redone and why, the check and e2e results, and anything left open or deferred. Then say whether it's a good point to `/clear`, as CLAUDE.md asks. Merging goes through `/merge` once the user says so.
