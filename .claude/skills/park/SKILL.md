---
name: park
description: Use when the user says to park an idea, note it for later or add a backlog card, or says yes to parking a follow-up that turned up mid-task. Writes the idea as a short new card in `backlog/` (or a line on an overlapping card), after the user's yes, and commits it on its own.
argument-hint: "[the idea]  (default: the one just discussed)"
---

Park `$ARGUMENTS` as a backlog card. Parking keeps an idea from getting lost without starting on it: the card is short, unrefined and not prioritised yet. The card rules are in the [Backlog section of `docs/CLAUDE.md`](../../../docs/CLAUDE.md#backlog) ("Parking an idea" and the fields); read it first.

## 1. The idea

- From the arguments, or else the idea just discussed. If it's unclear which, ask.
- Several ideas: one card each. If they turned up during one task, say that the task may be cut wrong ([Scope Control](../../../CLAUDE.md#scope-control--risk-guardrails) in the root `CLAUDE.md`).

## 2. Overlap

- Grep the titles (`^# `) in `backlog/*.md` and `backlog/done/*.md` for the idea's key words.
- An open card covers it: show that card and ask whether to add a line to it or park a new card anyway.
- A done card covers it: say it's built already and ask whether something is still missing.

## 3. Propose

Show the full card before writing it:

- File `backlog/<id>.md`; `id` is short kebab-case, says what the idea is, and isn't taken.
- `status: "backlog"`, `priority: "low"` (refinement sets the real one), `assignee`, `dueDate`, `completedAt` all `null`.
- `epic` and `labels` (one kind, one area): pick what fits the idea best, given the conversation, the roadmap's open phases and similar cards. `null` and `idea` are common but not the default answer; a bug found mid-task is a `bug`, a follow-up of an open phase may belong in its epic only if the phase can't close without it (the epic rule in `docs/CLAUDE.md`); otherwise it goes to an `XX <Area> vN` epic (a planned version of that area, numbered on, see `docs/CLAUDE.md`), an `XX <Area> Future` epic (maybe some day) or `null`, and `priority` says how soon. A card stands on its own: don't park "do this when X is touched anyway". Ask both with AskUserQuestion, your pick first, unless the user already said; when two fit about equally, say so in the options.
- `created` and `modified`: now, `date -u +%Y-%m-%dT%H:%M:%S.000Z`.
- `order`: after the last card on the board. Keys sort by character code (`0-9 < A-Z < a-z`), so `a0 < a0V < a1 < … < a9 < aA < … < ag`. Until bug 2 is fixed (equal keys; see `order` in the [Backlog section of `docs/CLAUDE.md`](../../../docs/CLAUDE.md#backlog)) every key is unique across the whole board, so take the highest key of all cards (`backlog/*.md`, not `done/`), whatever their epic, and step its last character one up in that sequence (`a3` → `a4`, `a9` → `aA`); a key ending in `z` gets a `V` appended. An empty board starts at `a0`.
- Body: `# <title>`, then two or three lines: what the idea is and what's still open about it. A `**Needs:**` line only if a dependency is already clear. Any card named in the body is a link, ``[`id`](id.md)`` (`./scripts/docs_check.py --fix` writes it from the bare id; pre-commit fails otherwise). No Done-when list; that's refinement's job.

## 4. Write and commit

- After the user's yes: write the card (or the line on the existing card). No other card changes.
- Commit it on its own, on the current branch: stage only that card's file (`git add backlog/<id>.md`), never `-A`, since the task's own changes may be uncommitted. Subject `docs(backlog): park <what>`.
- Mid-task, go back to the task afterwards; the card doesn't change what the task does.
