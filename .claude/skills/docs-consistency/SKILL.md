---
name: docs-consistency
description: Use when the user asks to check the docs against each other, after a fold, or when a phase closes. Checks the docs against each other — roadmap, specs, architecture, area docs, development doc — for contradictions, stale status, broken links and folds that are due. Reports findings and proposed changes, points out the ones that need a decision, and asks how to proceed; edits nothing.
context: fork
agent: general-purpose
---

Check that the project docs agree with each other. Don't read application code; comparing docs to code is `/docs-drift`. Don't edit any file: report findings and proposed changes, the user picks which to apply.

The rules the docs are meant to follow are in `docs/CLAUDE.md` and in [Keeping docs in sync](../../../CLAUDE.md#keeping-docs-in-sync) in the root `CLAUDE.md`. Read that first, then `docs/roadmap.md`, `docs/architecture.md`, every file in `docs/specs/` and `docs/areas/`, `docs/development.md` (where this fork keeps what the template keeps in the root README's workflow sections; the root `README.md` is upstream's Marketplace page, so read it only for contradictions), every folder README (`git ls-files '*/README.md'`) and the cards in `backlog/*.md` and `backlog/done/*.md`.

## Checks

**Links and references**
- Run `./scripts/docs_check.py --check` and report each line it prints as a finding (a wrong breadcrumb is fixed with `./scripts/docs_check.py --fix`; a broken link by hand). It covers breadcrumbs and that every relative Markdown link resolves to an existing file (and heading, if it has an anchor). Then check what it can't: each crumb's parent links down to the page (the architecture doc's Building blocks to each area doc, the roadmap to each open spec).
- Every spec number mentioned anywhere exists. A mention of a deleted spec is only fine in git-history pointers.
- The architecture doc cites no spec numbers and no completion status.
- `Superseded-by:` lines point at a spec or area doc that exists and actually covers the stated scope.

**Status**
- Each spec's header has `Status`, `Phase`, and `Architecture` when it draws from an architecture section, in the form `docs/CLAUDE.md` describes, and the same form as the other specs (e.g. a date on `Done` or not, consistently).
- A spec's status agrees with what the roadmap says about that work, and vice versa: work the roadmap calls done has a `Done` spec or an area doc; a `Done` spec isn't listed as open in the roadmap.
- **Fold due:** a phase marked Done that still has specs in `docs/specs/`.

**Backlog** (cards against the roadmap, specs and docs; the frontmatter, `Needs:` ids and card links are linted by `docs_check.py`, which already ran above, so don't redo that)
- No phase under Shipped in the roadmap has open cards in its epic, and no open phase has all its cards done with its "Done when" items met (a close that's due). A `done` card of a Shipped phase is a missed fold.
- A card isn't already built according to an area doc. A spec's `Card:` names an existing card, and a card's `Spec:` an existing spec.
- **Epic vs Done when:** each "Done when" item of an open phase is covered by a card in its epic or already holds, and each open card in a numbered epic serves one of them. One that doesn't breaks the epic rule in `docs/CLAUDE.md` (**judgment**: it moves to an `XX` epic or `null`, or the roadmap gains the item).
- **Dependencies in prose:** a card's text says it needs, waits for or follows another card ("first", "once X exists", "builds on") without a `**Needs:**` line for it.
- **Dependency order:** a card that ranks above a card it needs in the picking order (priority, then epic, then `order`); a `ready` card that needs a card that is neither `ready` nor done; a `Needs` cycle.
- **Branches:** each `in-progress` card has a branch named after it (`git branch --list`, a slice suffix is fine) or a worktree, and a branch named after a card whose card isn't `in-progress` or done is stale.
- **Stale description:** a card states something about the app today ("nothing is set up yet", "today X does Y") that an area doc contradicts.

**Contradictions**
- An architecture section marked planned isn't described as built elsewhere, and a built one isn't still marked planned.
- Area docs don't contradict the architecture doc, each other, or `docs/development.md` on the same point (e.g. two docs giving different reasons or values for the same thing).
- Tooling and repo setup are described in `docs/development.md` only, not repeated in an area doc, and the fork's workflow isn't added to the root `README.md`. A folder's own setup is in its folder README, linked from the Layout section of `docs/development.md` rather than repeated there.

**Duplication**
- The same content written out in two places (roadmap restating an area doc, two area docs explaining the same mechanism, a spec still holding text that was already folded). One should become a link to the other. Say which one keeps the text.

**Structure**
- Heading levels and section order: a doc's headings nest correctly and follow the same layout as its siblings (specs like other specs, area docs like other area docs), and a section sits under the heading it belongs to.

## Report

Group findings under the headings above; skip empty ones. Number the findings in one sequence across all groups. For each finding:
- where (file and line, as a Markdown link relative to the repo root),
- what's wrong, in one sentence,
- the proposed change, concretely (the replacement text, or "delete line X", or "replace with a link to Y") and its kind: spec status bump, `Superseded-by` line, area doc edit, roadmap edit, or architecture doc edit.

Mark anything that's a judgment call rather than a clear error as **(judgment)**. If something looks off but you can't tell which doc is right, say so and ask instead of picking one. End with a one-line count of findings per group and their total, counted from the numbered findings above, so the total equals the highest number. Don't state a count anywhere else in the report. No praise and no summary of what's fine.

After the count line, add a `### Worth a look` section listing only the findings where the user's call matters: the proposed change might be wrong or incomplete, there is more than one reasonable fix, the change renames something other text cites, or the finding points to a bigger problem than the line it sits on. For each, give its number and one or two sentences on what to decide and what you'd pick. Everything not listed is meant to be applied as proposed. If nothing qualifies, write "Nothing needs a look; all can be applied as proposed." Check a finding before listing it (e.g. grep for citations of a title you propose to rename), so the section holds only real questions. End with one line asking for next steps, e.g. "Apply all as proposed, or say which to change or skip?" This section adds no numbered finding and no count.
