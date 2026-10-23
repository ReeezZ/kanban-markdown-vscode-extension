---
id: "code-review-passes"
status: "backlog"
priority: "high"
assignee: null
epic: "01 Foundation"
dueDate: null
created: "2026-10-23T16:30:00.000Z"
modified: "2026-10-23T16:30:00.000Z"
completedAt: null
labels: ["chore", "extension"]
order: "a0s"
---
# Code review passes

**Goal:** the code quality of the extension host, the webview and `src/shared` is reviewed once, and the findings are cards, so the refactors that should come before the fixes are chosen deliberately.

One pass per area, after the area docs and the baseline tests exist. A finding is a card (correctness, structure, tests), not a fix made on the spot. The ones that should come before the Phase 2 fixes go into `01 Foundation`; the rest into a later epic.

**Done when**

- [ ] a review pass is done for the host, the webview and `src/shared`
- [ ] every finding is a card or is dropped, with the reason
- [ ] each card has an epic: Foundation if it must come before the fixes, otherwise later
- [ ] the roadmap's Foundation items still match what the review found

**Out of scope:** doing the refactors; each one is its own card.

**Open questions**

- Which lenses per pass (structure, correctness, tests, naming)?

**Findings from the extension docs pass** (raw input for the host pass, unsorted into cards; from reading, not running):

- Move: `generateKeyBetween` throws after `_moveFeature` has changed the card in memory, so memory and file differ; in the webview the throw drops the move silently. No `writeFile` in the move paths is caught.
- Move: the field `newOrder` is an index, not a key; the key is computed twice (webview and host) from possibly different card lists.
- Contract: the host's message handler is untyped; `focusMenuBar` and `startWithAI` are missing from `WebviewMessage`; `featuresUpdated` is never sent.
- Watcher: `_migrating` drops events instead of deferring them; plain writes aren't guarded, so each causes a second full load; `_lastWrittenContent` only knows editor saves, so a drag on the open card reloads the editor (check whether unsaved editor text is lost).
- Load: migrations (old status folders, done reconcile, integer orders) run on every load, including watcher reloads; the order migration rewrites every card of the column; any error empties the board silently; a file without frontmatter vanishes silently.
- Duplication: three frontmatter parsers (shared, sidebar, `FeatureHeaderProvider`), two serializers, two card loaders, the default columns three times with `DEFAULT_COLUMNS` unused, the features directory resolved in four places, the sort comparator about seven times, the done-folder move block four times.
- Dead code: `FeatureHeaderProvider.ts` and `src/shared/editorTypes.ts` are never registered or built.
- `addFeature` command: bypasses the panel and ignores `filenamePattern`, `defaultStatus`, `defaultPriority`, `addNewCardsToTop` and name clashes (can overwrite a card).
- Ids: a name clash on a move or create suffixes the filename but not the frontmatter `id`.
- `_updateFeature` merges unvalidated fields from the webview (`id`, `filePath` included); the `createFeature` handler opens the last card in the list, assuming the create succeeded.
- Sidebar: re-opens the board each time it becomes visible; waits a fixed 500 ms for the board; its watcher and config listener are never disposed.
- Frontmatter: no escaping of `"`, labels with commas split on reading, missing `created`/`modified` read as "now" on every load (feeds into filename migration).
- English-only strings outside `l10n/`: the filename-migration message, the AI prompt, `<html lang="en">`, the hardcoded default columns.
- Test gaps: nothing covers `_moveFeature`, `_moveAllCards`, `_archiveAllCards`, `_loadFeatures` and its migrations, the watcher, label operations, the sidebar, or the webview's drop-index mapping.

**Needs:** [`baseline-tests`](baseline-tests.md), [`area-docs-baseline`](area-docs-baseline.md)
