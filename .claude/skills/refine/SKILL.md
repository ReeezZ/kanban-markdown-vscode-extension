---
name: refine
description: Use when the user asks to refine, groom or get backlog cards ready, or before picking up a card that isn't `ready`. Refines backlog cards with the user until they meet the Definition of Ready — read the card and what it touches, ask the product questions, propose the rewritten card, splits and priority, then apply what the user approves and set its status to ready.
argument-hint: "[card-id ... | epic]  (default: the next unrefined cards)"
---

Refine the cards `$ARGUMENTS` with the user. The user is the product owner and decides; you prepare. The rules for cards, the Definition of Ready (DoR) and the picking order are in the [Backlog section of `docs/CLAUDE.md`](../../../docs/CLAUDE.md#backlog). Read it first.

## 1. Pick the cards

- Card ids: those cards. An epic (`"01 First Release"`, or its number): its open cards with `status: "backlog"`.
- Empty: the next three or so open cards with `status: "backlog"`, in the picking order (Grep `priority:`, `epic:` and `order:` in `backlog/*.md`; `backlog/done/` is skipped).
- Say which cards you picked and why, in one line each, before reading further.

## 2. Read, per card

- The card itself, and the cards it names or that name it (Grep its id, and `Needs:.*<id>`).
- The architecture sections and area docs it touches, and a light Grep of the code for the part of the app it changes, enough to tell what exists already. Don't plan the implementation.
- The other open cards' titles (`# ` lines), for duplicates and overlaps.

Then go through these lenses and note what's unclear or missing:

- **Product:** what changes for the person using the product, and the smallest version that's still useful.
- **UX:** where it lives in the UI, which existing controls it reuses, how it works on the smallest screen or panel it has to fit.
- **Data and interfaces:** a change to stored data or settings, a migration, a new or changed API, command or contribution point.
- **Architecture:** does it touch a decision in `docs/architecture.md` or need a new one.
- **Testing:** how it will be checked to work.
- **Risk:** persistence or auth means planning first ([Scope Control](../../../CLAUDE.md#scope-control--risk-guardrails) in the root `CLAUDE.md`).
- **Size:** does it fit one branch, or should it be split.

## 3. Ask

- Ask only what the user has to decide: product choices, scope, priority. Answer the rest yourself from the code and docs and say what you found.
- AskUserQuestion with your recommendation as the first option. Keep each round to a few questions; several small rounds beat one wall of them.
- If a card turns out to be built already, a duplicate, or no longer wanted, say so and ask whether to delete or merge it rather than refining it.

## 4. Propose and apply

- Show each rewritten card in full: the body in the DoR's shape, the new `priority`, and any split into new cards (same epic, `order` next to the original). Keep it short; refinement doesn't write the spec into the card.
- After the user's yes: edit the cards, set `status: "ready"` and `modified`. A `**Needs:**` id must name an existing card, written as a link; run `./scripts/docs_check.py --fix` after the edit to make the links from bare ids. Check each card's `epic` against the epic rule in `docs/CLAUDE.md`: a numbered epic is for what blocks the phase's close, so a card that doesn't gets an `XX <Area> vN` epic (a planned version of that area, numbered on, see `docs/CLAUDE.md`), an `XX <Area> Future` epic (maybe some day) or `null`, with its `priority` saying how soon. A card stands on its own: reword or drop a "do this when X is touched anyway" card, and give a `**Needs:**` only for what has to exist before the card can be built.
- Only the cards being refined change. Something noticed on another card is mentioned, not edited.

## 5. Commit

- Commit in small steps as the session goes, each `docs(backlog): …` naming what it covers. Typically: the refined cards with their splits; new ideas that came up, parked as cards with `/park`; a change to the backlog rules. A later round of questions can get its own commit.
- Card edits go straight to `main`. A session that also changes a skill or a rule doc beyond a line can use a branch through `/branch`; say which you'd pick if unsure.
- Finish as root `CLAUDE.md` asks after a commit: whether it's a good point to `/clear`, and what lives only in the conversation.
