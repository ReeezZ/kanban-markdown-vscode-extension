[README](../README.md) › Scripts

# Scripts

Repo upkeep scripts that belong to no single part of the app: checks the
pre-commit hook runs, and helpers that span the repo. Scripts that only build
or analyse one folder's data live in that folder.

| Script          | What it does                                                                                                                                                                                         |
| --------------- | ---------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| `docs_check.py` | `--check` (default) the docs' breadcrumbs and relative links (also in the skills) and the backlog cards, or `--fix` the breadcrumbs and card links, see [Breadcrumb](../docs/CLAUDE.md#breadcrumb) and [Backlog](../docs/CLAUDE.md#backlog) in docs/CLAUDE.md |

`release.ts` and `check-l10n.ts` are upstream's tsx scripts (`pnpm release:*`, `pnpm check-l10n`); they are not covered by the rules below.

## Shell or Python

- **Shell** for running commands and handling processes: starting and stopping
  servers, signals, pipes, exit codes. The git hooks in `.githooks/` are the
  example.
- **Python** for parsing or rewriting text and files, or once a script has
  more than about 50–100 lines of logic. `docs_check.py` is the example:
  it parses Markdown, resolves links and rewrites a line in each file, which is
  hard to follow in bash.

Python scripts use the standard library only and need `python3` on the PATH,
so the doc check, which the pre-commit hook runs on every commit, doesn't
depend on a virtualenv. A script that needs a package goes in a folder with
its own toolchain instead. That is also why the link check is regexes over the
text, not lychee or markdown-link-check: the docs use a small part of Markdown
and a hook shouldn't need another toolchain.
Tests for a script are `unittest` files next to it (`test_<name>.py`, also
stdlib, so no pytest needed), run with `python3 -m unittest discover -s scripts -t .`
(`scripts/` is a package, since VS Code discovers from the repo root); the hook
runs them when `scripts/` changes.
A test that runs git in a temp repo must clear the `GIT_*` variables first:
git hooks set `GIT_DIR` and `GIT_INDEX_FILE`, which would otherwise point the
temp repo at the real one and let a test commit land in it.
