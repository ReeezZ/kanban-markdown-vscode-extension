[README](../README.md) › Development

# Development

The fork's own setup and workflow. The root [README](../README.md) and [CONTRIBUTING](../CONTRIBUTING.md) are upstream's and stay as they are; what the fork adds is written here. For what upstream documents (install, scripts, code style), see those two.

## Layout

- `src/extension/`: the extension host, bundled with esbuild.
- `src/webview/`: the React webview, bundled with Vite.
- `src/shared/`: types and utilities used by both sides. How they fit together is in [Architecture](architecture.md#building-blocks).
- `tests/`: unit tests (Vitest) and the integration tests that run in a VS Code host.
- `l10n/` and `package.nls*.json`: the en/es/pt strings. `pnpm check-l10n` checks that the files match.
- `scripts/`: upstream's tsx scripts (`release.ts`, `check-l10n.ts`) and the doc check. See [scripts/README.md](../scripts/README.md) for when a script is shell and when it's Python.
- `backlog/`: one Markdown card per planned feature, fix or idea, grouped by roadmap phase. It's shown as a board by the Kanban Markdown extension; the card format is in [docs/CLAUDE.md](CLAUDE.md#backlog).
- `.devcontainer/`, `.githooks/`, `.claude/`: the container, the git hooks and the Claude Code settings, hooks and skills.

## Devcontainer

The agent workflow runs in the devcontainer in `.devcontainer/`: Node 22, pnpm 12.15.0 (the `packageManager` version), bash 5, python3 3.10 or newer, jq, xvfb and the Electron libraries for the integration tests.

- `post-create.sh` installs pnpm, runs `pnpm install --frozen-lockfile`, sets the hooks path and makes the hooks executable.
- The hooks path is `core.hooksPath=.githooks` in the container's system git config (`/etc/gitconfig`), not in `.git/config`. The macOS host shares `.git/config`, has bash 3.2 and its own `node_modules`, so on the Mac commits run no hooks.
- The Claude login and `node_modules` live in named volumes, so they survive a rebuild.
- Worktrees under `.claude/worktrees/` sit on the bind mount, so pnpm keeps their store at the repo root, in `.pnpm-store/` (ignored by git and vsce). It is pnpm's default location, shared by all worktrees, and their `node_modules` hardlink into it.

## Checks

Two git hooks run automatically (see [Git workflow](#git-workflow)). `commit-msg` checks the subject (see [Commit messages](git-workflow.md#commit-messages)). `pre-commit` runs the docs check on every commit, then the checks of each area the commit stages a file in:

- **docs**, on every commit: `./scripts/docs_check.py --check`.
- **scripts**, when `scripts/` is staged: `python3 -m unittest discover -s scripts -t .`.
- **app**, when `src/`, `tests/`, `package.json`, `pnpm-lock.yaml`, `pnpm-workspace.yaml`, `tsconfig*.json`, `vite.config.ts`, `vitest.config.mts`, `eslint.config.mjs`, `tailwind.config.js` or `postcss.config.mjs` is staged: `pnpm lint`, `pnpm typecheck`, `pnpm test`.
- **l10n**, when `l10n/` or `package.nls*.json` is staged: `pnpm check-l10n`.

- With a base (`.githooks/pre-commit main`, as the merge steps run it) the hook picks the areas from what the branch changed since the base, and the app check also runs `pnpm build`.
- The integration tests stay out of the hook as too slow for every commit. Run them with `pnpm run build:extension && xvfb-run -a pnpm run test:integration`: they need the extension built first, and a display. They are described in [README › Testing](../README.md#testing).
- The checks read the working tree, so they see unstaged edits too. To check exactly what's staged, stash the rest first (`git stash --keep-index`).
- There is no Prettier step. Prettier is configured upstream, but the code doesn't follow it, so the hook doesn't check it.
- What `docs_check.py` checks, and what `--fix` writes, is in [scripts/README.md](../scripts/README.md).

## Git workflow

Features and fixes are built on short-lived branches and merged back into `main`, in the main checkout or in a worktree when another agent is busy there. Subjects follow Conventional Commits. The steps, commands and conventions are in [git-workflow.md](git-workflow.md); how the fork stays in sync with upstream is under [Upstream](git-workflow.md#upstream).

## Doc checks

Two Claude Code skills in `.claude/skills/` check the docs. They only run when typed, and report proposed changes without editing anything.

- `/docs-consistency` checks the docs against each other: status, links, contradictions, folds that are due. Run it after a slice or a fold.
- `/docs-drift [area]` checks docs against the code, and flags passages that only restate the code, to trim rather than update. It's slower; run it at phase close, after `/docs-consistency`.

`/memory-review` goes through Claude Code's memory files for this project with you. It proposes a verdict for each one (keep, merge, move into the docs, delete) and applies the ones you approve. Unlike the doc checks, it edits files.
