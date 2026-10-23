# AI Assistant Instructions

## General AI Assistant Behavior

### Clarification & Context-Gathering

- Ask specific questions to clarify the task, requirements, or any ambiguous details. Do not assume.
- Gather necessary context (read files, check docs, search the codebase, check recent git log/commit messages) before proposing an approach — commit messages in this repo record what was deliberately deferred from a slice, which matters for "continue" style requests.
- The session-context hook already gives the branch, uncommitted changes, the last 10 first-parent commits and the specs in progress; don't re-run those, only look further when that isn't enough (older history, finished specs not yet folded).
- Always consider the questions: What information is missing? What assumptions am I making?
- Also consider: What is the user's goal?

### Critical Review & Honest Feedback

- Do not flatter the user; give honest, critical feedback and challenge assumptions where appropriate.
- Review code, tasks, and requirements with a critical mindset: identify issues, suggest improvements, question design decisions.
- If fundamental problems are found, recommend stepping back and reconsidering the approach rather than patching around it.

### Communication & Output Style

- Structure output as clear, actionable bullet points, questions, or concrete suggestions, with specific examples.
- Don't go "over the top" in code comments, docs, or commit messages. Stay grounded — no invented metrics, no salesy language.
- This is a single-person project used partly for learning. Favor explaining unfamiliar concepts before implementing them over silently producing finished code.
- Read files with the Read tool (`offset`/`limit` for a part) and change them with Edit, or Write for new files; not with `cat`, `sed`, `head`, `tail` or heredoc scripts in Bash. A script edit hides the diff from the user, and every Bash call may need a manual confirmation. Bash is for tests, lint, git and searches.

### Scope Control & Risk Guardrails

- Adding a dependency, or touching persistence/auth: propose a short plan and stop before writing code. Also risky here:
  - the card file format (`src/shared/featureFrontmatter.ts`, the filename patterns in `src/extension/featureFileUtils.ts`);
  - `workspaceState` keys;
  - the `contributes.configuration` schema in `package.json`;
  - command and view IDs;
  - anything that stops a fix from cherry-picking onto `upstream/main` (see [Fork and upstream](#fork-and-upstream)).
- For everything else, pick what fits the task: either plan (and write the spec) first, or prototype first and update the docs afterwards, with a spec written after the fact if one is still needed. Prototyping suits small, reversible or look-and-feel changes. Planning first suits work with open design questions or a wide reach. If unsure, say which you'd pick and why.
- Planning a new feature doesn't reshape the roadmap: if it belongs to a roadmap phase or backlog card, find it, and only that item's status changes (the card's `status`, the spec's Status), once the work is done. Work that's decided and done right away (a workflow tweak, a docs fix, a quick idea) needs no card; don't offer one just to have one. Reordering, merging or rewording other roadmap items is a separate request.
- Small, reviewable diffs either way — one component or one endpoint at a time.
- Commits: when a task is done, run `git commit` directly with the proposed message instead of asking in chat first. Claude Code's permission prompt for the commit is the user's review, so asking in chat as well means confirming twice. Never auto-push or auto-deploy. Destructive git operations (force-push, reset --hard, branch delete) require explicit per-instance approval, except `git branch -d` on a branch that was just merged (see [Branches and merges in docs/git-workflow.md](docs/git-workflow.md#branches-and-merges)).
- Don't stop or kill processes the user started (a dev server, a watch task, a debug session), even when one is in the way: name the process and the fix, and leave it to the user.
- Treat any new dependency (package, crate, extension) as a proposal, not an automatic install — check maintenance activity and legitimacy before adding.
- If the user has multiple requests. Separate them into distinct tasks and address them one at a time. Commit each task (see above) and wait for the user before tackling the next one.
- A follow-up that turns up mid-task and isn't needed to finish it: point it out and offer to park it with `/park`, which also checks for an existing card it could extend instead. Don't chase it, and don't write the card without the user's yes. If several turn up in one task, say so: the task may be cut wrong.
- In plan mode, a skill's edits and commits (a card from `/park`, the cards from `/refine`, a new branch) become steps in the plan file, and approving the plan is the user's yes for them; don't ask again. A merge still waits for the user's yes in chat (see [Git](#git)).
- After a task is committed, say whether it's a good point to `/clear`, and list what so far lives only in the conversation (decisions, findings, open questions), offering to write it down first (spec, card, memory). Say "nothing open" if that's the case. Name the model for the next task when it's known ([Model choice](#model-choice)). If the user prefers to compact, suggest a `/compact keep: …` line with those items filled in.

### Model choice

- The default is `opusplan`, starting in plan mode: Opus plans, Sonnet carries out the approved plan. The user sometimes switches with `/model`. The system prompt names the model in use.
- When the current model doesn't fit the task, say so at the start of the reply in one line: the model to switch to and why. Then stop before doing the work, and ask the user to `/model …` or to say to go on anyway. A quick answer or a question back doesn't need the stop. Otherwise say nothing about the model.
  - Opus fits open design questions, debugging whose cause isn't known yet, changes that reach across areas, and reviews.
  - Sonnet fits carrying out an approved plan or spec, mechanical edits, doc syncs and following the commit/merge workflow.
- Whatever hands work on names the model for it, in one line with the reason in a few words:
  - a plan's last line: Sonnet (what `opusplan` switches to) when the steps are spelled out, or Opus when they still need judgement (say which part), then written out as "run `/model opus` before approving", since approving switches `opusplan` to Sonnet;
  - a handoff prompt for a new session or another agent, at its top;
  - the note after a commit (see [Scope Control](#scope-control--risk-guardrails)), when the next task is known.
- Suggest orchestrator mode (the `/orchestrate` skill: Opus hands steps to Sonnet subagents and reviews each) in the plan's model line instead, with the reason in a few words, when the work seems to fit: an approved spec with an Implementation order, broad reading where only conclusions matter, work likely to hit compaction, or parts in separate folders that can run independently. Not for open design questions, debugging an unknown cause, look-and-feel iteration or small diffs. Suggest it mid-task too when work that looked small turns out to reach many files. The user confirms with `/model opus`.

### Documentation Consistency

- Point out any inconsistencies between the README, roadmap, architecture doc, area docs and specs. If a spec is out of date, propose a specific change to the spec or roadmap rather than just noting the mismatch.
- Write each fact in one place. Other docs link to it instead of repeating it; `docs/development.md` holds the repo's layout, checks and workflow notes (the root README is upstream's Marketplace page and stays untouched), `docs/git-workflow.md` the branching, merging and commit conventions, a folder README its folder's own setup, CLAUDE.md only what's specific to the agent.
- Cite a section of a doc with a link to its heading's anchor (`[Testing](CLAUDE.md#testing)`), not a quoted title, so the docs check reports it when the heading is renamed. A bold bullet label has no anchor: give it a heading first, or name it in plain text next to a link to its parent section. Renaming a heading means running `./scripts/docs_check.py --check` before the commit.

### Workflow Improvement

- Point out possible improvements to the workflow; Pain points that would have made solving a solution easier are worth noting, even if they don't block the current task. Suggest ways to improve the workflow for future tasks.

## Project Context Reference

**IMPORTANT**: Always reference the project README, `docs/roadmap.md` for product vision/phased plan, `backlog/` for the cards of each phase, and `docs/architecture.md` for the architectural decisions before proposing new ones.

What each kind of doc holds and how it's written (breadcrumbs, architecture doc, specs, area docs, folder READMEs, folds, roadmap, backlog) is in [docs/CLAUDE.md](docs/CLAUDE.md). It loads once a file under `docs/` is read; read it yourself before editing a folder README or a backlog card.

### Keeping docs in sync

- When the user states a decision, scope change, or a spec/slice completion in conversation, treat that as a signal to check whether the roadmap, the architecture doc, an area doc, or a spec's `Status:` field is now out of date — don't wait to be asked.
- This includes checking for overlapping scope: if the slice just finished reverses or replaces part of something already built (not just extends it), the area doc describing it needs an edit, or an unfolded spec needs a `Superseded-by` line. Check this before moving to the next task, the same way a `Status:` bump is checked.
- Update the docs without being asked, but don't do so silently: point out the mismatch and propose the specific change (which doc, what changes, and whether it's a spec status bump, a `Superseded-by` line, an area doc edit, a roadmap edit, or an architecture doc edit) in the same message where the mismatch is flagged — don't defer the concrete proposal to end-of-task. Only write it once the user confirms.
- If it's unclear whether a decision belongs in the architecture doc or an area doc, whether a change is a full or partial supersession, or which spec a change belongs to, ask rather than guessing.
- Once a phase closes (see Backlog in [docs/CLAUDE.md](docs/CLAUDE.md)), flag the fold of its specs as due without waiting to be asked, the same way other doc-sync checks are flagged.

## Git

- ALWAYS read the current status and diff before writing a commit message.
- Commit messages: brief, factual, no invented percentages or salesperson framing. Should be easy to understand what changed and why.
- Subjects follow the convention in [Commit messages in docs/git-workflow.md](docs/git-workflow.md#commit-messages); a hook rejects ones that don't. Don't bypass it with `--no-verify`.
- Every feature or fix gets a branch. Start every branch with the `/branch` skill and merge only through `/merge`; don't run `git switch -c`, `git worktree add` or `git merge` by hand. The reasons are in [Branches and merges in docs/git-workflow.md](docs/git-workflow.md#branches-and-merges). When unsure whether a change is tiny enough to go straight to `main`, ask.
- Enter a worktree with EnterWorktree's `path`, never its `name`: by name it picks its own branch name and branches from whatever the current checkout has open (`worktree.baseRef` is `head`), which may be another feature branch.
- Never merge without the user's yes in chat, even when the branch is done; `/merge` stops and asks.

## Comments in code

- A comment has to add something the code can't say by itself: an overview of what a piece of code is for, the concepts it's built on, and its API (how to use it, what callers get back, what they must handle).
- Modules and exported functions, hooks, components and types that other code builds on get a doc comment (`/** */` in TS, or the language's equivalent) covering that overview, concepts and API. Keep it short, and skip it when the name and signature already say everything. We don't need a translation from code to English, just a summary of the _why_ and _what for_.
- Inside a function body, comment only a non-obvious _why_ (a hidden constraint, a workaround, a subtle invariant), never _what_ the code does line by line.

## Across folders

Rules for one folder only are in its own CLAUDE.md (none yet), which loads once a file in that folder is read. What stays here applies to more than one folder or has to apply before any file there is read.

- `src/shared/types.ts` is the host↔webview contract. Change both sides (`src/extension` and `src/webview`) in one commit.
- `src/extension` and `src/shared` use relative imports only and no DOM types, because `tsconfig.integration.json` compiles them without the `@/` alias.
- New UI strings need en/es/pt entries in `l10n/` or `package.nls*.json`. Check them with `pnpm check-l10n`.

### Testing

- New logic gets a test the user (or a separate review pass) can verify actually constrains behavior — not one written by the same pass that implements the logic being tested.
- If the repo has an end-to-end suite: when a task that touches `src/extension/`, `src/shared/` or `tests/integration/` is nearly done, start it yourself without asking (`pnpm run build:extension && env -u ELECTRON_RUN_AS_NODE xvfb-run -a pnpm run test:integration`, see [README › Testing](README.md#testing)). The `env -u` is for the agent only: in the Claude Code IDE extension, commands inherit the extension host's `ELECTRON_RUN_AS_NODE=1`, which makes the test VS Code start as plain Node (`Cannot find module …/fixtures/workspace`). A terminal and CI don't set it, so the command in [Checks](docs/development.md#checks) does without. Run it with `run_in_background`, output to a log at a path the user can find, and a hard time limit; never as a blocking foreground call, and never piped through `tail`, which hides progress. Report from the log and delete it afterwards. If the run hangs, say so and move on; the attempt is what counts. If a stale earlier run holds its ports, report it instead of killing it. Don't wait for the run with a `pgrep -f <name>` loop, which matches itself: wait for the harness's exit notification.

## Fork and upstream

This repo is a fork of `LachyFS/kanban-markdown-vscode-extension`. The steps for syncing and for upstream PRs are in [Upstream in docs/git-workflow.md](docs/git-workflow.md#upstream).

- Upstream's conventions win over this file's where they overlap: formatting, naming, folder layout.
- Never reformat upstream code. Prettier is configured upstream, but the code doesn't follow it; don't run it over files.
- A commit meant for upstream touches no fork-only file (`docs/`, `backlog/`, `.claude/`, `.githooks/`, `scripts/*.py`, `CLAUDE.md`).
- Card status changes go in their own `docs(backlog)` commits, so the code commits cherry-pick without `backlog/`.
- Match the comment density of the file being edited. The rules in [Comments in code](#comments-in-code) apply to new files; in an upstream file, follow its style.
- The README and CONTRIBUTING are upstream's. They get no fork workflow; it lives in [docs/development.md](docs/development.md).
