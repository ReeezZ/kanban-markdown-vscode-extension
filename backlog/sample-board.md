---
id: "sample-board"
status: "backlog"
priority: "medium"
assignee: null
epic: "01 Ordering Fixes"
dueDate: null
created: "2026-10-23T15:04:03.000Z"
modified: "2026-10-23T15:04:03.000Z"
completedAt: null
labels: ["chore", "infra"]
order: "a3"
---
# Sample board for the Extension Development Host

**Goal:** pressing F5 opens a board I can drag on without touching the real `backlog/`.

The board is a copy in the style of real cards: epics, cards that share `order` keys, a `ready` column and long bodies. It lets me check ordering by hand and see with `git diff` that a save changes only what was edited.

**Done when**

- [ ] a sample folder with cards in at least two epics, shared keys, `ready` and long bodies
- [ ] `launch.json` opens the Extension Development Host on it, with the columns set in its own settings
- [ ] the folder is not shown as a second board of the repo (name and `.vscodeignore` checked)
- [ ] a short note in `docs/development.md` says how to use it

**Open questions**

- Where does it live: a `test-project/` folder is already in `.gitignore`; is a tracked sample folder better?
- Does the docs check need to skip the sample cards, so their fake epics don't fail it?

**Needs:** none