---
name: memory-review
description: Use when the user asks to review, clean up or sort the auto-memory files. Goes through the auto-memory files with the user — decide per memory whether to keep, update, merge, move into CLAUDE.md / the development doc / an area doc / a skill, or delete — then apply what the user approves.
---

Review the memory files with the user. The memory directory is the one your system prompt names (it holds `MEMORY.md`). This runs in the main conversation because the user decides each verdict; propose first, change nothing until they've answered.

## Read

- Every file in the memory directory, including `MEMORY.md`.
- `CLAUDE.md`, the folder CLAUDE.md files (`git ls-files '*/CLAUDE.md'`), `docs/development.md` and `docs/git-workflow.md`, the card titles (`# ` lines) in `backlog/`, the list of `docs/areas/` and `.claude/skills/`, the headings of `docs/architecture.md`, and the recent first-parent history (`git log --first-parent --oneline -30`). Read an area doc, architecture section or skill only when a memory touches its subject.

## Checks per memory

- **Still current:** a file, function, flag, command or skill it names still exists; nothing in the docs or git history has since overtaken it (a parked item that's now done, a rule the user later changed).
- **Already written down:** CLAUDE.md, `docs/development.md`, an area doc or the architecture doc already says the same. Then the memory goes, or shrinks to the part that isn't written down.
- **Overlap:** it duplicates or contradicts another memory. Propose one merged memory, or ask which side is right.
- **Belongs elsewhere:** `docs/development.md` if it applies to people as well as the agent (setup, workflow; the root `README.md` is the fork's page for users and gets no dev workflow); CLAUDE.md if it's a standing rule for the agent in every session (a folder's own CLAUDE.md if it only applies when working there); a skill if it's a procedure run on demand; an area doc if it's about how part of the app works; a backlog card (through `/park`) if it's an idea or open work. A memory stays a memory if it's a user preference, project context that changes over time, or a pointer that has no better home.
- **Form:** the memory follows the memory format in your system prompt: frontmatter type fits the content, dates are absolute, feedback and project memories have **Why:** and **How to apply:** lines, `[[links]]` name existing memories.
- **Index:** `MEMORY.md` has exactly one line per memory file, no line without a file, and each line's hook still matches its memory.

## Propose

One table, one row per memory (plus a row for index problems):

| # | Memory | Verdict | Target | Reason |

Verdicts: keep, update, merge with #n, move to `<file>` (with the section), delete. Reason is one sentence; for move and update, give the concrete text or section underneath the table. Mark judgment calls **(judgment)**. When you can't tell which of two sources is right, ask instead of proposing. Then stop and wait: the user answers in one go (e.g. "ok except 3 and 7"). Discuss the disputed rows until each has a verdict.

## Apply

- **Memory files and `MEMORY.md`:** edit and delete them directly. They're outside the repo, so there's nothing to commit.
- **Repo files** (CLAUDE.md, `docs/development.md`, area docs, skills): make these changes on a branch started with `/branch`, and commit them. The commit's permission prompt is the user's review. Write each fact in one place: once moved, the memory is deleted rather than left beside it. Merge through `/merge`, which asks first.
- Finish with a list of what changed, in two groups: memory changes and repo commits.
