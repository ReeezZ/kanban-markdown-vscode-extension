---
name: docs-drift
description: Use when the user asks whether the docs still match the code, or after a larger change to an area. Compares docs with the code — area docs, development doc and folder READMEs — and sorts each passage that describes the code into wrong, redundant or worth keeping. Proposes fixes and deletions; edits nothing.
context: fork
agent: general-purpose
argument-hint: "[area name | development | README]  (default: all)"
---

Check whether the docs still match the code, and whether they should describe it at all. Don't edit any file: report findings and proposed changes, the user picks which to apply.

Scope: `$ARGUMENTS`. If empty, cover every area doc in `docs/areas/`, `docs/development.md` and the folder READMEs (`git ls-files '*/README.md'`, the root `README.md` apart: it is upstream's, so it's left out unless named). Otherwise only the named area doc (e.g. `webview` → `docs/areas/webview.md`), `development` (`docs/development.md`), or `README` (the folder READMEs and the root `README.md`; findings on the root one are reported, not applied, since it's upstream's).

With more than one item in scope, start one subagent per item, in parallel, each given this file's instructions and its one item. Then merge their reports into one, in the format under [Report](#report). With one item, do it yourself.

Read `docs/CLAUDE.md` first (what an area doc is for), and the comment rules in the root `CLAUDE.md`. If the docs contradict each other, that's `/docs-consistency`'s job; mention it in one line and move on.

## The question for every passage

Docs should complement the code, not mirror it. Code comments cover the what and how of a module; area docs cover behaviour, concepts and decisions with their reasons. For each passage that talks about the code, decide which it is:

1. **Wrong** — the code no longer does this. Check the code itself, not a spec or commit message.
2. **Redundant** — correct, but only restates what the code says: lists of functions, props, constants, CSS values, file paths, step-by-step logic, numbers that live in one place in the code. These are what drift next. Propose deleting or shrinking them, not updating them. Naming the main module a reader starts from is fine.
3. **Worth keeping** — a reason, a rejected alternative, a concept that spans several files, a constraint the code can't show, behaviour as the user sees it, something deliberately not built. Don't report these, unless they're also wrong.

A wrong passage that's also redundant gets "delete", not "update".

## Checks

**Area docs** — for each one: the modules it names exist and still do what it says; Behaviour matches what the UI and API actually do; each Decision still holds in the code; "Not built" items are still not built.

**`docs/development.md`** — commands, scripts, paths and tool names match `package.json`, the scripts, the e2e config in `tests/integration/`, the devcontainer and the hooks; every documented step would work as written. The same for each folder README against its folder.

**Code pointing at docs** — comments in the code that link to a spec or doc that no longer exists.

## Report

Group findings by file. For each finding:

- where (doc file and line, plus the code location that shows it, as Markdown links relative to the repo root),
- **wrong** or **redundant**, and what's wrong in one sentence,
- the proposed change, concretely: replacement text, or "delete lines X–Y", or "shrink to: …".

Mark judgment calls as **(judgment)**. End with a count of wrong vs redundant findings per file. Then add one line: if `/docs-consistency` hasn't been run since the last doc change, suggest running it first, because drift findings assume the docs agree with each other. No praise and no summary of what's fine.
