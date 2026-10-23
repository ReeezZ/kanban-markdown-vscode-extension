[README](../README.md) › Development

# Development

The fork's own setup and workflow. The root [README](../README.md) is the fork's page for users (and its Marketplace page), so the dev workflow is written here instead. [CONTRIBUTING](../CONTRIBUTING.md) is upstream's and stays as it is. For what upstream documents (install, scripts, code style), see those two.

## Layout

- `src/extension/`: the extension host, bundled with esbuild.
- `src/webview/`: the React webview, bundled with Vite.
- `src/shared/`: types and utilities used by both sides. How they fit together is in [Architecture](architecture.md#building-blocks).
- `tests/`: unit tests (Vitest) and the integration tests that run in a VS Code host.
- `l10n/` and `package.nls*.json`: the en/es/pt strings. `pnpm check-l10n` checks that the files match.
- `scripts/`: upstream's tsx scripts (`release.ts`, `check-l10n.ts`) and the doc check. See [scripts/README.md](../scripts/README.md) for when a script is shell and when it's Python.
- `docs/`: roadmap, architecture, specs and area docs; what each holds is in [docs/CLAUDE.md](CLAUDE.md).
- `backlog/`: one Markdown card per planned feature, fix or idea, grouped by roadmap phase. It's shown as a board by the Kanban Markdown extension; the card format is in [docs/CLAUDE.md](CLAUDE.md#backlog).
- `.devcontainer/`, `.githooks/`, `.claude/`: the container, the git hooks and the Claude Code settings, hooks and skills.

## Devcontainer

The agent workflow runs in the devcontainer in `.devcontainer/`: Node 22, pnpm 12.15.0 (the `packageManager` version), bash 5, python3 3.10 or newer, jq, xvfb and the Electron libraries for the integration tests.

- `post-create.sh` installs pnpm, runs `pnpm install --frozen-lockfile`, sets the hooks path and makes the hooks executable.
- The hooks path is `core.hooksPath=.githooks` in the container's system git config (`/etc/gitconfig`), not in `.git/config`. The macOS host shares `.git/config`, has bash 3.2 and its own `node_modules`, so on the Mac commits run no hooks.
- The Claude login and `node_modules` live in named volumes, so they survive a rebuild.
- Worktrees under `.claude/worktrees/` sit on the bind mount, so pnpm keeps their store at the repo root, in `.pnpm-store/` (ignored by git and vsce). It is pnpm's default location, shared by all worktrees, and their `node_modules` hardlink into it.
- pnpm 12, not upstream's 9: pnpm 9 is past its end of life with open advisories. pnpm 12 runs install scripts only for allow-listed packages (`allowBuilds` in `pnpm-workspace.yaml`: esbuild only; `keytar` is only `vsce login`'s credential store) and installs no release younger than a day (`minimumReleaseAge: 1440`). CI runs on Node 22 too.

### What the container keeps from the Mac

VS Code forwards host credentials into a devcontainer, so the container is no boundary for them on its own. These are set in the Mac's VS Code User settings, not in `devcontainer.json`, which code in the container could change:

- `dev.containers.gitCredentialHelperConfigLocation: "none"` and `dev.containers.copyGitConfig: false`. The SSH agent is still forwarded (no setting turns it off), and holds no keys.
- `.git/hooks` and `.git/config` are mounted read-only (`devcontainer.json`), since git on the Mac runs what they hold and changes there don't show in `git status`. One effect: `git branch -d` deletes the branch but exits 1, as it can't drop the branch's config section. `.devcontainer/` and `.vscode/` stay writable, since they're tracked: check `git status` before a rebuild.

Pushing and pulling work from VS Code's git UI in the container: its askpass hands git the Mac's GitHub login, whatever the settings above say. Force pushes and other pushes from a shell run in a terminal on the Mac. Branches and commits go through the agent, not the git UI: the agent's git runs the hooks inside the Bash sandbox, the git UI runs them outside it, where any process can ask the askpass socket for the login.

### Claude Code's Bash sandbox

Every Bash command the agent runs is sandboxed with bubblewrap: it writes only to the repo and `$TMPDIR`, and can't change the Claude Code settings, skills and hooks or `.git/hooks` and `.git/config`. Without `bubblewrap` and `socat` in the image, Claude Code would run commands unsandboxed without an error.

- `runArgs: --security-opt seccomp=unconfined` in `devcontainer.json`, because Docker's default seccomp profile blocks the user namespaces bubblewrap needs. `sandbox.enableWeakerNestedSandbox: true` in the container's `/home/node/.claude/settings.json`, because an unprivileged container can't mount a fresh `/proc`; it reuses the container's, which is acceptable as the container is the outer boundary. It's set by hand, so it never applies on the Mac and the agent doesn't write its own sandbox settings.
- Electron can't create user namespaces inside the sandbox, so the integration tests run outside it: `.claude/settings.json` lists `pnpm run build:extension` and `xvfb-run -a pnpm run test:integration` in `sandbox.excludedCommands`. Claude Code drops a leading `env -u …` before matching but matches `xvfb-run` as written. A call with a `cd`, a redirect or another command stays sandboxed, so the agent runs the e2e command as one bare call ([Testing](../CLAUDE.md#testing)). Excluded commands still need a permission.
- The write block on `.claude/settings.json`, `.claude/skills/` and `.claude/hooks/` holds in every checkout, worktrees included, and git is no exception: a `git switch`, `rebase`, `merge` or `restore` that has to rewrite a file there fails halfway (`Read-only file system`), leaving that file modified and the rest done. Edits through Claude Code's Edit and Write tools still work. So the agent runs git commands that rewrite those paths unsandboxed. Outside the sandbox `$TMPDIR` is a different folder, so a file such commands read (a merge message) goes in the session's scratchpad instead.
- The sandbox doesn't let commands listen on Unix sockets. The `tsx` CLI always does, so inside the sandbox a tsx script runs as `node --import tsx <script>`, as the pre-commit hook does for `check-l10n`.
- pnpm 12 keeps its lock folders in `$XDG_RUNTIME_DIR`, falling back to `/tmp`, which is read-only in the sandbox. `post-checkout` sets it to `$TMPDIR` when unset; a `pnpm install` the agent runs by hand in a fresh worktree needs the same.
- To block a path that doesn't exist (`.bashrc`, `.mcp.json`, `.claude/agents` and others in the repo root), the sandbox creates an empty placeholder file and mounts `/dev/null` over it. The placeholders exist while a sandboxed command runs: inside the sandbox `git status` lists them as untracked character devices, which `/branch` and `/merge` ignore; outside it, in VS Code's git view, they're empty files, so don't stage everything while a background command runs.

## Checks

Two git hooks run automatically (see [Git workflow](#git-workflow)). `commit-msg` checks the subject (see [Commit messages](git-workflow.md#commit-messages)). `pre-commit` runs the docs check on every commit, then the checks of each area the commit stages a file in:

- **docs**, on every commit: `./scripts/docs_check.py --check`.
- **scripts**, when `scripts/` is staged: `python3 -m unittest discover -s scripts -t .`.
- **app**, when `src/`, `tests/`, `package.json`, `pnpm-lock.yaml`, `pnpm-workspace.yaml`, `tsconfig*.json`, `vite.config.ts`, `vitest.config.mts`, `eslint.config.mjs`, `tailwind.config.js` or `postcss.config.mjs` is staged: `pnpm lint`, `pnpm typecheck`, `pnpm test`.
- **l10n**, when `l10n/` or `package.nls*.json` is staged: the script of `pnpm check-l10n`, run as `node --import tsx scripts/check-l10n.ts` (see [Claude Code's Bash sandbox](#claude-codes-bash-sandbox)).

- With a base (`.githooks/pre-commit main`, as the merge steps run it) the hook picks the areas from what the branch changed since the base, and the app check also runs `pnpm build`.
- The integration tests stay out of the hook as too slow for every commit. Run them with `pnpm run build:extension && xvfb-run -a pnpm run test:integration`: they need the extension built first, and a display: `xvfb-run -a` starts a throwaway virtual display (Xvfb) on a free display number, as CI does. An agent adds `env -u ELECTRON_RUN_AS_NODE`, see [Testing](../CLAUDE.md#testing). They are described in [README › Testing](../README.md#testing).
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
