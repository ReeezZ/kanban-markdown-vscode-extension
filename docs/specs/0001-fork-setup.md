[README](../../README.md) › [Roadmap](../roadmap.md) › 0001 Fork setup

# 0001 Fork setup

## Status

Approved

- Phase: Scaffold/Infra

## Goal

Set up the fork before its first fix:

- pnpm 12, a devcontainer, and CI on Node 22;
- the full agent workflow from the template repo (`agentic_template`): rules, docs lifecycle, git hooks, docs check, Claude Code settings, hooks and skills;
- a backlog built from the fork handoff.

Upstream's existing conventions stay as they are. Fix commits stay separate from tooling, so they can still be cherry-picked into upstream PRs.

The work is split between two sessions:

- **Steps 1–4** run on the macOS host, which has no hooks yet. Homebrew's pnpm 12.15.0 matches the pinned version, so it can verify them.
- **Steps 5–10** run in a new Claude Code session inside the devcontainer, reading this spec. The host's `~/.claude` (plans, memories) isn't visible in the container.

## Done means

- `packageManager` is `pnpm@12.15.0`. `pnpm-workspace.yaml` allow-lists install scripts for esbuild only and sets `minimumReleaseAge`. CI uses `pnpm/action-setup@v6` and Node 22.
- `.devcontainer/` builds an image with Node 22, pnpm 12, bash 5, GNU coreutils, python3 ≥ 3.10, jq, xvfb and the Electron libraries, plus Claude Code. The Claude login and `node_modules` are kept in named volumes. The temporary template mount is gone again, so the container starts on any machine.
- The template's files are in place and adapted (step 5–6):
  - `CLAUDE.md`, `docs/CLAUDE.md`, `docs/git-workflow.md`, `docs/development.md`, `docs/roadmap.md`, `docs/architecture.md`;
  - `docs/specs/`, `docs/areas/`, `.githooks/`, `scripts/docs_check.py` (+ tests);
  - `.claude/settings.json`, `.claude/hooks/` and all eight skills.
- `backlog/` holds the cards from the handoff, and the roadmap holds Phases 1–4.
- All checks in [Tests](#tests) pass. The upstream README, CONTRIBUTING, lint and format config and release script are unchanged.

## Tests

In the container:

1. **Toolchain.**
   - `node -v` prints 22.x, and `pnpm -v` prints 12.15.0.
   - `python3 --version` is ≥ 3.10, and `bash --version` is ≥ 5.
   - `jq` and `xvfb-run` exist.
   - `git config --system core.hooksPath` prints `.githooks`, and `git config --local core.hooksPath` prints nothing.
   - `/sandbox` shows no Dependencies tab, and a sandboxed `ls` runs without a `bwrap` error.
   - `git status` is clean after `pnpm install --frozen-lockfile`.
2. **App checks:** `pnpm lint && pnpm typecheck && pnpm test && pnpm build && pnpm check-l10n`.
3. **Integration tests:** `pnpm run build:extension && xvfb-run -a pnpm run test:integration`.
4. **Docs check:** `./scripts/docs_check.py --check` exits 0, and `python3 -m unittest discover -s scripts -t .` passes.
5. **commit-msg**, tried by hand with message files in `$TMPDIR`.
   - Rejected: `Bad subject`, `Merge branch 'x'`.
   - Accepted: `ci: bump node`, `chore: release v1.14.2`, `fix(extension): keep lane order (#12)`.
6. **Claude Code hooks**, as in the template's TEMPLATE.md step 4.
   - `session-context.sh` lists this spec under Specs in progress.
   - `worktree-summary.sh` prints nothing.
   - In a trial worktree, `post-checkout` installs and the summary shows one line. Remove the worktree afterwards.
7. **pre-commit.**
   - Commit 5 runs every area's checks.
   - A staged lint error is rejected (undo it with `git restore`).
   - `.githooks/pre-commit main` also builds.
8. **Package contents:** `pnpm exec vsce ls --no-dependencies | grep -E '^(\.claude|\.devcontainer|\.githooks|backlog|docs/specs)/|CLAUDE\.md'` prints nothing.
9. **F5:** Running Extensions shows the dev build, and the board opens.
10. **Board:** the main window shows the 16 cards in Backlog, in a0…aF order, with the phase epics.
11. **Rebuild:** after a container rebuild, the Claude login persists and `node_modules` reinstalls.
12. **CI**, after the user pushes and opens a PR within the fork: action-setup v6 installs pnpm 12 on Node 22, and all jobs pass.

## Explicitly out of scope

- Any fix to the extension itself. Bugs 1–4 and the other handoff items become backlog cards here.
- Renaming the extension, a new publisher, a settings prefix, publishing. These are Phase 4 cards.
- Writing the area docs. That's the card `area-docs-baseline`.
- Changing upstream's README, CONTRIBUTING, Prettier/ESLint config, `scripts/release.ts` or CHANGELOG.

## Decisions

- **pnpm 12 now, not upstream's 9.15.9.**
  - pnpm 9 reached end of life on 2026-04-30. The [GitHub Advisory Database](https://github.com/advisories?query=pnpm) lists 25 advisories affecting 9.15.9, about 14 of them high, fixed only in 10.34.5+ and 11.11+.
  - pnpm 9 also runs every dependency's install scripts. pnpm 10+ blocks them unless they're allow-listed, and newer versions add `minimumReleaseAge` against freshly compromised releases.
  - The bigger diff against upstream is accepted. Upstream is still on pnpm 9, so a fix that touches the lockfile has to be regenerated on the upstream PR branch.
- **Install scripts: only esbuild.** `keytar` is only used by `vsce login`'s credential store, and CI uses env PATs. `@vscode/vsce-sign` stays off unless `pnpm package` needs it. `minimumReleaseAge: 1440` is set explicitly, because the pnpm 11 default is unverified.
- **A devcontainer.** The macOS host has bash 3.2 and no GNU coreutils, so the template's hooks don't run there. The container uses Node 22, and CI moves from Node 20 (EOL since April 2026) to 22.
- **The hooks path lives in the container's system git config** (`/etc/gitconfig`), not in `.git/config`. The host and the container share `.git/config` through the bind mount, so a repo-level setting would also run the hooks on the Mac, under bash 3.2 and with the host's `node_modules`. `--global` isn't used because VS Code copies the host's `.gitconfig` into the container. On the Mac, commits run no hooks.
- **Claude Code's Bash sandbox in the container.** On Linux it needs `bubblewrap` and `socat`; if they're missing, Claude Code runs commands unsandboxed without an error ([Sandboxing › Set up Linux and WSL2](https://code.claude.com/docs/en/sandboxing#set-up-linux-and-wsl2)).
  - In an unprivileged container, bubblewrap can't mount a fresh `/proc`. `sandbox.enableWeakerNestedSandbox: true` reuses the container's `/proc`, which is acceptable because the container is the outer boundary ([Bubblewrap fails to start inside a container](https://code.claude.com/docs/en/sandboxing#bubblewrap-fails-to-start-inside-a-container)). It goes in the container's user settings (`/home/node/.claude/settings.json`), so it never applies on the host. The user sets it by hand: the auto-mode classifier blocks Claude from writing its own sandbox settings.
  - Electron can't create user namespaces inside the sandbox (`No usable sandbox!`), so the e2e command is listed in `sandbox.excludedCommands` in the project's `.claude/settings.json` ([Chromium or rootless Podman fails inside the sandbox](https://code.claude.com/docs/en/sandboxing#chromium-or-rootless-podman-fails-inside-the-sandbox-on-linux)). That leaves upstream's test runner unchanged.
- **The full template.** Specs and the fold, area docs, breadcrumbs, `Superseded-by` and all eight skills, so the fork works spec-driven like the template's origin project. The docs are thin so far; `area-docs-baseline` is the first Phase 1 card.
- **Upstream's conventions win.**
  - The README is the Marketplace page, and it and CONTRIBUTING get no fork workflow. The template's root README sections go into `docs/development.md` instead.
  - Breadcrumbs still start at `[README](../README.md)`, which is only a link and doesn't change the README. Done Scaffold/Infra specs fold into `docs/development.md`.
  - Prettier is configured, but the code doesn't follow it, so nothing is reformatted and the hook has no Prettier step.
  - Upstream's commit style already uses the `ci:` type, so the commit-msg hook accepts it.
- **Card status changes get their own commits** (`docs(backlog): start <id>` and `docs(backlog): finish <id>`), so code commits cherry-pick onto `upstream/main` without touching `backlog/`.
- **`order` keys unique across the whole board.** The installed 1.14.1 throws when two neighbouring cards share a key (bug 2), so `/park` takes the highest key on the board until that fix ships.
- **Explore findings for the cards.**
  - **Bug 1 is confirmed.** `KanbanPanel._moveFeature` filters the target column without the epic lane (`src/extension/KanbanPanel.ts:618-620`; the key is generated at L626). The `moveFeature` message has no lane field (`src/shared/types.ts:127`), while `moveAllCards` (L138) has one. The webview computes the index per lane (`KanbanBoard.tsx:89`, `:109`; `App.tsx:339-344`).
  - **Bug 2 is confirmed.** `case 'moveFeature'` (`KanbanPanel.ts:121-123`) has no try/catch. Status and `modified` are changed in memory before `generateKeyBetween` can throw (L611-615).
  - **Bug 3, as the handoff states it, is partly wrong.**
    - The trim happens in the parser (`src/shared/featureFrontmatter.ts:37`, `body.trim()`), not in `serializeFeature`.
    - `modified` is bumped by the `KanbanPanel` callers (L612, 678, 791, 878, 1003, 1030), not by `serializeFeature`.
    - The serializer (L42-61) does drop unknown frontmatter fields.
  - **Other findings.**
    - `.vscodeignore` would ship `.claude/worktrees/**` in the `.vsix`: vsce doesn't read `.gitignore`.
    - `release.yml` publishes as LachyFS on any `v*` tag push, so no tags go to origin before Phase 4.
    - The integration tests need `build:extension` first.
    - On Debian bookworm, CI's `libasound2t64` is called `libasound2`.
    - `_moveFeature` has no unit tests.

## Implementation order

### 1. Spec (host)

Create the branch `chore/agent-workflow` from `main` by hand, since `/branch` doesn't exist in the fork yet. Write this spec.

Commit: `docs: add spec 0001 for the fork setup`.

### 2. pnpm 12 (host)

- Keep the `packageManager: pnpm@12.15.0` change in `package.json` and the env-lockfile document at the top of `pnpm-lock.yaml`. Homebrew pnpm 12 generated both.
- `pnpm-workspace.yaml`:
  - `allowBuilds`: `esbuild: true`, `keytar: false`, `'@vscode/vsce-sign': false`;
  - `minimumReleaseAge: 1440`.
- `.github/workflows/ci.yml` and `release.yml`: `pnpm/action-setup@v4` → `@v6`.
- Verify on the host:
  - `pnpm install --frozen-lockfile` changes nothing beyond these files;
  - `pnpm lint && pnpm typecheck && pnpm test && pnpm build && pnpm package`;
  - `pnpm exec vsce ls --no-dependencies`.

Commit: `build: move to pnpm 12 and allow install scripts only for esbuild`.

### 3. Devcontainer (host)

**`.devcontainer/Dockerfile`**

- Base image: `mcr.microsoft.com/devcontainers/typescript-node:22-bookworm`.
- One apt layer: `xvfb xauth libnspr4 libnss3 libatk1.0-0 libatk-bridge2.0-0 libgtk-3-0 libglib2.0-0 libgbm1 libxkbcommon0 libasound2 libxss1 libsecret-1-0 jq bubblewrap socat`.
- pnpm is installed in `post-create.sh` with `npm install -g`, using the version from `packageManager`. Corepack isn't used: it's unclear whether it handles pnpm 12's binary distribution.

**`.devcontainer/devcontainer.json`**

- Feature: `ghcr.io/anthropics/devcontainer-features/claude-code:1`.
- Extensions: `dbaeumer.vscode-eslint`, `esbenp.prettier-vscode`, `anthropic.claude-code`, `LachyFS.kanban-markdown`.
- Named volumes:
  - `/home/node/.claude`, so the Claude login survives a rebuild;
  - `node_modules`, because the host's `node_modules` holds darwin binaries.
- A read-only bind of `${localEnv:HOME}/git/agentic_template` to `/workspaces/agentic_template`, as the copy source for steps 5–6. It's temporary and is removed in step 9, because the source path exists only on this Mac and the container won't start without it.
- `containerEnv`: `CLAUDE_CONFIG_DIR=/home/node/.claude`.
- `remoteUser: node`. Add `runArgs: ["--shm-size=1g"]` only if Electron crashes.

**`.devcontainer/post-create.sh`**

- chown the two volumes;
- `sudo npm install -g <packageManager>`;
- `pnpm install --frozen-lockfile`;
- `sudo git config --system core.hooksPath .githooks`;
- `chmod +x` the hooks and `scripts/docs_check.py`.

Commit: `build(devcontainer): add a devcontainer with node 22, pnpm 12 and xvfb`.

### 4. CI on Node 22 (host), then the handover

In `ci.yml` (twice) and `release.yml`, change `node-version: 20` to `22`.

Commit: `ci: run the workflows on node 22`.

Then the user reopens the folder in the container and starts a new session: "carry out spec 0001 from step 5". In the container, recreate two things the host had:

- the feedback memory "use subagents to keep the main context clean";
- the English-docs preference in `~/.claude/CLAUDE.md`.

Before starting that session, the user adds `"sandbox": { "enableWeakerNestedSandbox": true }` to `/home/node/.claude/settings.json` in the container, then runs `/sandbox` to check that it shows no Dependencies tab (see [Decisions](#decisions)).

### 5. Workflow docs, git hooks, docs check (container)

Copy from `/workspaces/agentic_template`, keeping all of it: specs, area docs, breadcrumbs, `Superseded-by`.

**`CLAUDE.md`.** Fill in the FILL INs.

- Scope Control, the risky list:
  - the card file format (`src/shared/featureFrontmatter.ts`, the filename patterns in `featureFileUtils.ts`);
  - `workspaceState` keys;
  - the `contributes.configuration` schema;
  - command and view IDs;
  - anything that stops a fix from cherry-picking onto `upstream/main`.
- Across folders:
  - `src/shared/types.ts` is the host↔webview contract, so change both sides in one commit.
  - `src/extension` and `src/shared` use relative imports only and no DOM, because `tsconfig.integration.json` compiles them without the `@/` alias.
  - New UI strings need en/es/pt entries in `l10n/` or `package.nls*.json`, checked with `pnpm check-l10n`.
- Testing: the e2e command is `pnpm run build:extension && xvfb-run -a pnpm run test:integration`. It covers `src/extension/`, `src/shared/` and `tests/integration/`, and is described in [README › Testing](../../README.md#testing).
- New section `## Fork and upstream`:
  - upstream's conventions win;
  - never reformat upstream code;
  - commits meant for upstream touch no fork-only files;
  - card status changes go in their own `docs(backlog)` commits;
  - match the comment density of the file being edited;
  - link to `docs/git-workflow.md#upstream`.
- The README and CONTRIBUTING get no fork workflow.

**`docs/CLAUDE.md`.** Keep all sections.

- Labels: kinds `feature enhancement bug idea chore`; areas `extension` (host + `src/shared`), `webview`, `infra`, `workflow`.
- Finishing a card is its own `docs(backlog): finish <id>` commit.
- Done Scaffold/Infra specs fold into `docs/development.md`.

**`docs/git-workflow.md`.**

- Change `README.md#checks` to `development.md#checks`.
- Types table:
  - add `ci`;
  - `chore` covers deps, tooling and release scripts (as upstream uses it);
  - `build` covers the devcontainer, toolchain and package manager.
- `### Releases`:
  - `pnpm release:*` writes the `chore: release vX.Y.Z` commit and the tag;
  - CHANGELOG is written by hand first;
  - no `v*` tags pushed to origin before Phase 4.
- `## Upstream`:
  - Sync: `git merge upstream/main -m "chore: merge upstream <ref>"`. Merge, not rebase, since `main` is pushed. Then run `.githooks/pre-commit ORIG_HEAD`.
  - PRs: a `pr/<card-id>` branch from `upstream/main`, cherry-pick the code commits, then run CONTRIBUTING's checks by hand. Upstream is on pnpm 9, so a lockfile change is regenerated there.
- One line saying the hook makes the commit convention strict for the fork's own commits.

**New docs.**

- `docs/development.md`: Layout, Devcontainer, Checks, Git workflow, Doc checks.
- `docs/roadmap.md`: the vision. The phases come in step 7.
- `docs/architecture.md`:
  - goals and constraints;
  - building blocks: extension, webview, shared;
  - decisions: fractional-indexing order per column; fixed frontmatter plus Markdown;
  - risks.
- `docs/areas/.gitkeep`.

**`.githooks/`.**

- `commit-msg`: add `ci` to `types`.
- `pre-commit`, function `check_app`:
  - runs `pnpm lint`, `pnpm typecheck` and `pnpm test`, plus `pnpm build` only in merge mode;
  - triggers on `src/ tests/ package.json pnpm-lock.yaml pnpm-workspace.yaml 'tsconfig*.json' vite.config.ts vitest.config.mts eslint.config.mjs tailwind.config.js postcss.config.mjs`.
- `pre-commit`, function `check_l10n`:
  - runs `pnpm check-l10n` on `l10n/ 'package.nls*.json'`;
  - kept only if it's green on HEAD.
- `pre-commit`: no Prettier step.
- `post-checkout`: `pnpm install --frozen-lockfile --prefer-offline`.

**`scripts/`.**

- `docs_check.py`, `test_docs_check.py` and `__init__.py` as they are. Only adapt `PARENT_RULES` if `docs/development.md` has to be the parent of something.
- `scripts/README.md`: add one line noting that `release.ts` and `check-l10n.ts` are upstream's tsx scripts.

**Upstream files.** Minimal merges only.

- `.gitignore`: replace line 11, `.claude/`, with:
  - `/.claude/worktrees/`
  - `.claude/settings.local.json`
  - `.claude/.cc-writes`
  - `__pycache__/`
- `.vscodeignore`: add `.claude/** .devcontainer/** .githooks/** backlog/** **/CLAUDE.md docs/*.md docs/specs/** docs/areas/** scripts/*.py scripts/README.md **/__pycache__/** pnpm-workspace.yaml`.
- `.vscode/settings.json`: add the four `kanban-markdown.*` keys.
- `.vscode/extensions.json`: add `LachyFS.kanban-markdown`.
- vitest, tsconfig and eslint stay unchanged: their globs are root-relative and don't reach `.claude/worktrees/`.

Run `./scripts/docs_check.py --fix`, then `chmod +x` the hooks.

Commit: `chore(workflow): add the agent workflow docs, git hooks and docs check`.

### 6. Claude Code settings, hooks, skills (container)

Copy all of `.claude/`: `settings.json`, the three hooks, and the skills `branch`, `merge`, `orchestrate`, `park`, `refine`, `docs-consistency`, `docs-drift` and `memory-review`.

Adapt:

- `/branch`:
  - start a card with its own `docs(backlog): start <id>` commit;
  - there's no dev server;
  - `.vscode-test/` is about 160 MB per worktree.
- `/merge`:
  - list the upstream-able commits;
  - use the xvfb e2e command.
- `/orchestrate`: the same e2e command.
- `/park`: take the highest `order` key on the whole board, until bug 2 is fixed.
- `/docs-consistency`: read `docs/development.md` where it reads the root README's workflow sections.

Add to `.claude/settings.json`: `"sandbox": { "excludedCommands": ["pnpm run build:extension", "xvfb-run -a pnpm run test:integration"] }`. Every command in a call has to match an entry, so the e2e call is these two commands exactly.

Then `chmod +x .claude/hooks/*.sh`.

Commit: `chore(workflow): add claude code settings, hooks and skills`.

### 7. Roadmap phases and backlog cards (container)

Phases:

1. **Phase 1: Ordering Fixes.** Done when:
   - a drop in a lane keeps its position after reload;
   - equal keys no longer throw, and errors are visible;
   - both have unit tests;
   - the fixes are self-contained commits.
2. Phase 2: Card Editing
3. Phase 3: Board Polish
4. Phase 4: Publish

Card format:

- frontmatter in `serializeFeature`'s field order;
- `status: backlog`;
- `# Title` directly after `---`;
- body: Goal, cause with file:line, **Done when**, open questions, `**Needs:**`.

| order | id | epic | prio | labels |
|---|---|---|---|---|
| a0 | `area-docs-baseline`: area docs for `extension` (message switch, move and order, file watching, card format) and `webview` (store, drag and drop, editor), linked from Building blocks; the fold target for Phase 1 specs | 01 Ordering Fixes | high | chore, workflow |
| a1 | `epic-lane-drop-order` (bug 1). Open question: extract the key computation into a pure, testable function | 01 | high | bug, extension |
| a2 | `equal-order-keys` (bug 2): rebalance with `generateNKeysBetween`, mutate only after the key is known, show a visible en/es/pt error. Open question: rebalance only the run of equal keys, or the whole column | 01 | high | bug, extension |
| a3 | `sample-board`: a board for the Extension Development Host with epics, shared keys, a `ready` column and long bodies | 01 | medium | chore, infra |
| a4 | `status-options-from-columns` (#61) | 02 Card Editing | high | bug, webview |
| a5 | `serializer-keeps-card-files` (bug 3, corrected). Touches persistence, so it gets a spec first | 02 | medium | bug, extension |
| a6 | `clickable-links` (#64, #68) | 02 | medium | feature, webview |
| a7 | `editor-task-lists` (#59). Needs a new TipTap dependency | 02 | medium | feature, webview |
| a8 | `label-colours` (#74): a `labelColors` setting | 03 Board Polish | medium | feature, webview |
| a9 | `send-to-top-bottom`. **Needs:** `epic-lane-drop-order` | 03 | low | feature, webview |
| aA | `column-drop-rules` (bug 4) | 03 | low | enhancement, extension |
| aB | `fork-name-and-publisher` (handoff §3), including launch.json `--disable-extension=LachyFS.kanban-markdown` | 04 Publish | medium | chore, infra |
| aC | `settings-prefix`. **Needs:** `fork-name-and-publisher` | 04 | medium | enhancement, extension |
| aD | `changelog-catch-up` | 04 | low | chore, infra |
| aE | `publish-extension`. **Needs:** aB, aC. Use Entra ID after 2026-12-01; settle the tag scheme | 04 | medium | chore, infra |
| aF | `markdown-round-trip-spike`, which also covers "the editor feels immature" | XX Editor v2 | low | idea, webview |

Run `./scripts/docs_check.py --fix`.

Commit: `docs(backlog): add the roadmap phases and the cards from the fork handoff`.

Then delete the untracked `agent-handoff.md`.

### 8. Verify (container)

Run [Tests](#tests).

### 9. Close and merge (container)

Remove the template mount from `.devcontainer/devcontainer.json`, then rebuild the container to check that it still starts.

Commit: `build(devcontainer): drop the template mount`.

Set this spec to `Done — <date>` and fold what's still current into `docs/development.md`. Then delete the spec on the same branch.

Merge through `/merge` with `--no-ff`. Subject: `chore(workflow): bring in pnpm 12, the devcontainer, the agent workflow and the backlog`.

### 10. Next

Run `/refine area-docs-baseline epic-lane-drop-order equal-order-keys`, then start Phase 1, spec-driven.
