---
name: merge
description: Use whenever a branch is finished or the user asks to merge, before running any git merge. Rebases onto main, runs the pre-merge checks and e2e, summarises, asks, then merges (ff-only or --no-ff) and cleans up the branch and worktree.
argument-hint: "[branch]  (default: the current branch)"
---

Merge the branch `$ARGUMENTS` (default: the current branch) into `main`. The reasons for each step are in [Branches and merges](../../../docs/git-workflow.md#branches-and-merges) in `docs/git-workflow.md`. Never merge without the user's yes in chat, and never push.

## 1. Situation

- If the session is inside a worktree, leave it first (ExitWorktree with `keep`) before the first git command: a worktree session refuses git commands aimed outside it, `git -C <path>` included. Afterwards reach the branch's checkout with `git -C <path>`.
- `git worktree list` shows where `main` and the branch are checked out; the main checkout is the first entry. `git status --short` must be clean in the branch's checkout, or stop and say what's uncommitted. Untracked character devices don't count (`[ -c <path> ]`): they're the sandbox's placeholders for blocked paths, see [Devcontainer](../../../docs/development.md#devcontainer).
- `git log --oneline main..<branch>` gives the commits: one commit means fast-forward, several mean a merge commit.
- If the branch or `main` since the merge base changed `.claude/settings.json`, `.claude/skills/` or `.claude/hooks/` (`git diff --name-only <merge-base> main <branch> -- .claude/settings.json .claude/skills .claude/hooks`, run once per side), the rebase, the `git switch main` and the merge rewrite files the sandbox can't write: run those three unsandboxed, with the merge message in the scratchpad, not `$TMPDIR`. See [Claude Code's Bash sandbox](../../../docs/development.md#claude-codes-bash-sandbox).

## 2. Rebase and checks

- Before rebasing, `git log <merge-base>..main -- <files the branch changed>` shows what `main` changed in the same files. Git doesn't flag an edit to text the branch moved elsewhere; if `main` edited such text, carry the edit over by hand after the rebase.
- Find the branch's card: the card whose id is the branch description (the part after `/`) or a prefix of it followed by `-`, longest match, in `backlog/` or `backlog/done/`. If it isn't in `backlog/done/` with `status: "done"`, say so in the summary. That's expected on a slice that isn't the last one; otherwise ask whether the finishing commit is missing. A note, not a stop. No card matches: skip this.
- `git -C <branch checkout> rebase main`. On conflicts, stop and ask; don't resolve guesses.
- `.githooks/pre-commit main`, run from the branch's checkout: `(cd <branch checkout> && .githooks/pre-commit main)` when that's a worktree. The hook finds its checkout from the working directory, so `git -C` or calling it by path would check the main checkout instead. It runs the checks of every folder the branch changed. Judge it by its exit code; don't pipe it through `grep` or `tail`, which hide that.
- If the diff against `main` touches `src/extension/`, `src/shared/` or `tests/integration/`, start the e2e suite in the branch's checkout as [Testing](../../../CLAUDE.md#testing) in `CLAUDE.md` describes: `pnpm run build:extension && env -u ELECTRON_RUN_AS_NODE xvfb-run -a pnpm run test:integration`. Run the two commands as that one call, so the sandbox exclusion in `.claude/settings.json` matches; a `cd` in the same call keeps it sandboxed, so for a worktree `cd <worktree>` in a call of its own first, and `cd` back to the main checkout afterwards.
- List the upstream-able commits: the branch's commits that touch no fork-only file (`docs/`, `backlog/`, `.claude/`, `.githooks/`, `scripts/*.py`, `CLAUDE.md`), e.g. `git log --format='%h %s' main..<branch> -- . ':!docs' ':!backlog' ':!.claude' ':!.githooks' ':!scripts/*.py' ':!CLAUDE.md'`. A commit that mixes fork-only and other files isn't pickable as it is; say so. See [Upstream](../../../docs/git-workflow.md#upstream) for how they reach upstream.

## 3. Summary and ask

Report: branch, commit count and subjects, which of them are upstream-able, files changed by folder, check results (pre-commit, e2e: passed, failed, or hung), and which merge will run. Then ask in chat whether to merge. Stop there until the user says yes. Another session may merge meanwhile: after the yes, run `git log --oneline <branch>..main`; if it lists anything, `main` moved: rebase, re-run the checks and say so before merging.

## 4. Merge

Where `main` is checked out:

- **Main checkout** (check `git branch --show-current` is `main` right before merging; someone may have switched it): run the merge there.
- **The branch itself is in the main checkout** (no worktree of its own): `git switch main` there, then merge there.
- **Main checkout is on another branch**: don't switch it. Merge from the branch's worktree: `git -C <worktree> switch main`, merge there, and run `branch -d` there too, since it checks against the current branch.

The merge itself:

- One commit: `git merge --ff-only <branch>`.
- Several commits: write the message to a file in the scratchpad and run `git merge --no-ff -F <file> <branch>` (`git merge` doesn't read `-F -`). The subject follows the commit convention and describes the whole branch; a blank line follows it (without one git reads the whole message as the subject), then the body, a short list of what the branch contains. Check with `git log -1 --format=%s` afterwards.

Then clean up, each as a separate command. `git branch -d <branch>` is allowed without further approval for a just-merged branch, but git refuses it while a worktree still has the branch checked out:

- Merged in the main checkout: `git worktree remove <path>` first (if the branch had one), then `git branch -d <branch>`.
- Merged in the branch's worktree (now on `main`): `git branch -d <branch>` there first, then `git worktree remove <path>` from the main checkout.

In the container, `git branch -d` exits 1 with `could not lock config file .git/config`: the branch is deleted, but its config section stays, since `.git/config` is mounted read-only. Judge it by `git branch --list <branch>` being empty, not by the exit code.

If `git worktree remove` fails with "Directory not empty", ask the user to close that worktree's editor tabs, then retry. If it fails with `Device or resource busy`, or with "contains modified or untracked files" where every untracked path is a character device (the sandbox's placeholders, `[ -c <path> ]`), say that it's the sandbox and retry it unsandboxed.

## 5. Retro and wrap-up

The single wrap-up of the merge. Only what went differently than the card, spec or plan expected: where the user corrected course or the work got stuck (a wrong assumption, a failing tool, permission prompts). Leave out what a commit message or a memory already holds, or point at it ("noted in memory"). Nothing went differently: "Retro: nothing to note".

A proposal only when there's a real one: a line in a CLAUDE.md, a skill tweak, or a gap in the Definition of Ready ([Backlog in `docs/CLAUDE.md`](../../../docs/CLAUDE.md#backlog)). Applied only on the user's yes; a bigger one is offered as a `workflow` card through `/park`. A "maybe, if it happens again" goes into the memory instead.

Last line, always: whether it's a good point to `/clear`, and what lives only in the conversation, as CLAUDE.md asks. If this session doesn't know how the work went (a fresh session, or after `/clear`), write "No retro: no context" before it.
