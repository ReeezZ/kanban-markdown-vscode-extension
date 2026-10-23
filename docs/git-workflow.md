[README](../README.md) › Git workflow

# Git workflow

## Branches and merges

The branching is trunk-based, in the spirit of the GitHub flow that
[Driessen's gitflow note](https://nvie.com/posts/a-successful-git-branching-model/)
recommends over gitflow for continuously delivered software. A feature or a
fix is built on a short-lived branch off `main` and merged
back with `git merge --no-ff`, so a branch lands as one merge commit. The
merge commit's subject follows the commit convention below and describes
the whole branch. A branch with a single commit is fast-forwarded instead
(`git merge --ff-only`): that commit already describes the whole branch,
and a merge commit on top would only repeat it. Either way the
first-parent history reads as one line per feature or fix:

```sh
git log --first-parent --oneline main
```

Before the merge, the branch is rebased onto the latest `main`, so its
commits sit on top of everything already merged and the full history
stays a single line with one bump per merge, instead of branches crossing
each other. Rebasing rewrites the branch's commits, which is fine while
the branch is only local; a branch that was pushed would need a
force-push afterwards.

After the rebase, `.githooks/pre-commit main` runs the checks of every
folder the branch changed (see [Checks](development.md#checks)). Each commit passed them
on its own, but the rebase combined the branch with what's new on `main`,
which nothing has checked yet. If the repo has an end-to-end suite, it runs
too when the branch changes the code it covers, since the hook leaves it out
(see [Testing in the root CLAUDE.md](../CLAUDE.md#testing)). Nothing enforces these
before a merge; they're a step of the workflow, like the rebase.

Branch names are `<type>/<short-description>`, with the same types as
commit subjects, e.g. `feat/card-filters` or
`docs/trunk-based-workflow`. Work for a card in the [backlog](../backlog/) is
named after it, `<type>/<card-id>`, with a slice suffix when the card takes
several branches; how the card's status follows the work is in the
[Backlog section of docs/CLAUDE.md](CLAUDE.md#backlog). Tiny changes, like a one-line docs fix,
and card edits from refining the backlog can still be committed straight to
`main`.

There are no `develop`, `release/*` or `hotfix/*` branches, also after
release: for software released from tags they add merges without adding
safety. Experiments live on a longer-lived feature branch or behind a feature
flag instead, since a shared branch would make every release all or nothing.

The `/branch` and `/merge` skills (`.claude/skills/`) carry out these steps,
including the commands. Whether a branch gets its own worktree or the main
checkout is asked when it starts (see below).

### Releases

`pnpm release:patch`, `release:minor` and `release:major` (upstream's `scripts/release.ts`) write the `chore: release vX.Y.Z` commit and the tag. The CHANGELOG is written by hand first, so the release commit picks it up.

`release.yml` publishes as LachyFS on any `v*` tag push. No `v*` tag goes to `origin` until the fork's name and publisher are set (Phase 4 of the [roadmap](roadmap.md)).

### Dependabot PRs

Don't merge them in the GitHub UI, where nothing checks them. Fetch the
branch (`git fetch origin <branch>:<branch>`) and merge it through `/merge`
like any other branch. Pushing `main` afterwards is the user's step.

### Worktrees for parallel work

A branch can get its own worktree under `.claude/worktrees/<name>`, and
`/branch` asks. Work that takes several commits or a longer stretch goes
there, so the main checkout stays free for a second session or a quick fix
meanwhile; a change done in a few minutes stays in the main checkout. That
depends on the work expected, not on the branch type. The cost is a second
install of the dependencies, and the board in the main checkout showing the
card as in progress only after the merge. When something else, like another
agent, is working in the main checkout, the branch takes a worktree without
asking.

Normally `main` is checked out in the main checkout, so the merge runs there.
It's checked right before merging, not earlier: whoever works in the main
checkout can switch it to another branch at any time, and a merge there
would land on that branch. When the main checkout is on another branch,
possibly with uncommitted work, switching it to `main` would disturb that
work. The merge then runs in the worktree instead, which can take `main`
over because it's checked out nowhere else.

The `post-checkout` hook seeds a new worktree under `.claude/worktrees/`: it
installs the dependencies, so the checks run there right away. When the
worktree was created another way, the install is yours to run.

## Commit messages

Subjects follow [Conventional Commits](https://www.conventionalcommits.org/en/v1.0.0/):

```
<type>[(scope)][!]: <lowercase imperative description>
```

| Type       | For                                                               |
| ---------- | ----------------------------------------------------------------- |
| `feat`     | behaviour or UI a user can see, including visual changes          |
| `fix`      | a bug, including a layout or styling one                          |
| `docs`     | README, roadmap, backlog cards, architecture, specs, area docs    |
| `test`     | unit or e2e tests on their own                                    |
| `refactor` | code changes that don't change behaviour                          |
| `perf`     | speed or size, without changing behaviour                         |
| `build`    | devcontainer, toolchain and package manager                       |
| `ci`       | CI workflows                                                      |
| `chore`    | dependencies, tooling and release scripts, editor and tool config |
| `revert`   | undoing an earlier commit                                         |

A scope is optional. When the change belongs to one part of the app, use
that area's name (the area labels in the [Backlog section of docs/CLAUDE.md](CLAUDE.md#backlog)),
also for its docs: `docs(<area>): mark spec NNNN done`. Other scopes are fine
where they help, e.g. `build(devcontainer)`.
`!` marks a breaking change, such as an API, settings or storage change old
data or clients can't handle. A commit that needs two types is usually two
commits.

`.githooks/commit-msg` rejects subjects that don't match, merge commits
included: git's default `Merge branch '…'` subject is rejected, so pass
`-m` to `git merge`. What the `pre-commit` hook runs is under
[Checks](development.md#checks). Upstream's own convention is loose; the hook makes it strict for this fork's own commits.

## Upstream

`upstream` is `LachyFS/kanban-markdown-vscode-extension`. The fork's `main` is pushed, so it takes upstream changes by merge, not rebase.

- **Sync.** `git fetch upstream`, then `git merge upstream/main -m "chore: merge upstream <ref>"`. The `-m` is needed because the hook rejects git's default subject. Then run `.githooks/pre-commit ORIG_HEAD`, which checks what the merge changed.
- **PRs.** Make a `pr/<card-id>` branch from `upstream/main` and cherry-pick the code commits onto it. Run the checks in CONTRIBUTING by hand, since upstream has no hooks. Upstream is on pnpm 9, so a lockfile change is regenerated on the PR branch, not cherry-picked.
- **Pickable when cheap.** Upstream PRs are a nice-to-have (see [Fork and upstream](../CLAUDE.md#fork-and-upstream)). A fix that stays its own commit, with no fork-only files and no `backlog/` changes in it, can be cherry-picked; one that can't is ported by hand if it ever goes upstream.
- **README.** The root README is the fork's own; on a sync, its conflicts resolve to ours.

## Why Conventional Commits

They make the history easy to scan and filter by type now, and leave the
option of generating changelogs and version bumps once there are releases.
There's no `style` type: in the convention it means formatting (Prettier's
job), and here it would get mixed up with CSS work. The check is a shell
hook rather than commitlint and husky, so it needs no packages.
