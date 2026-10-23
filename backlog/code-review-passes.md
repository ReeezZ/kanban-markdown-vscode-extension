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

**Findings from the webview docs pass** (raw input for the webview pass, unsorted into cards; from reading, not running; already covered by a card: the lane index in [`epic-lane-drop-order`](epic-lane-drop-order.md), the hard-coded status list in [`status-options-from-columns`](status-options-from-columns.md), the throw on equal keys in [`equal-order-keys`](equal-order-keys.md), the body re-serialisation in [`markdown-round-trip-spike`](markdown-round-trip-spike.md)):

- Editor, data loss: the save timers keep the `onSave` of the card they were started on, the editor isn't remounted per card (no `key`, `App.tsx:384`), and `featureContent` doesn't cancel them. Opening card B within 800 ms of an edit to card A writes B's body into A's file, with B's fields after a body edit or A's after a field edit (`FeatureEditor.tsx:562-564`, `:606-609`, `App.tsx:262-270`).
- Editor, lost edits: every `featureContent` replaces body and fields with no dirty check (`App.tsx:231-242`, `FeatureEditor.tsx:583-598`); a pending field timer then writes its stale fields back, which can revert a drag's status. Close, "open file" and delete don't flush the timer. Esc saves again after a finished save, since `debounceRef` is never cleared.
- Editor: a card with an empty body isn't loaded (`FeatureEditor.tsx:584`), so the previous card's text stays and is saved into it on the next edit. The editor stays open when its card leaves the board; the host drops those saves silently. The Esc handler is on `window`, so Esc in any input or dialog closes the editor. `handleFrontmatterUpdate` schedules the timer inside a `setState` updater.
- Create dialog: can't be cancelled, since Esc, the close button and a backdrop click all submit (`CreateFeatureDialog.tsx:357-384`). `defaultStatus` is never used: `n` and `triggerCreateDialog` always pass `backlog` (`App.tsx:138`, `:228`). The "+" in an epic lane doesn't preset the epic.
- Delete with undo: an `init` within the 5 s brings the card back while the toast runs, and Undo then adds it twice (`App.tsx:81-88`, `:212`). The editor-initiated delete never sends `closeFeature`.
- Column menu: archive all from an epic lane archives the whole `done` column (no lane in the message, `KanbanBoard.tsx:142-144`; `KanbanPanel.ts:705`). Move all and archive all also move cards hidden by a filter, while the header shows the filtered count.
- Drag and drop: no `dragleave`, so a stale drop target is reused; a drop on another lane shows an allowed cursor and does nothing; the insert position ignores the wrapped rows of the vertical layout; no keyboard alternative, cards aren't focusable, the move-all submenu is hover-only.
- Filters: the collapsed column count is unfiltered, the open one filtered; a filter whose control a display setting hides stays applied; a filter on a vanished label or assignee hides everything. Filters, search and layout are lost on reload.
- Orphan statuses: a card whose status names no column is invisible but counts in lane totals and the toolbar's lists, with no warning.
- Rendering: `KanbanBoard` gets cards through selector functions and redraws only because `App` subscribes to the whole store; moving `App` to selectors would stop the standard board updating. `FeatureCard` also subscribes to the whole store, so every card redraws on any store change.
- Contract: `vscode.postMessage` takes `unknown` (`vscodeApi.ts`), so the webview side isn't checked either; `updateFeature` is declared and handled by the host but never sent; the `init` handler guards fields the type calls required.
- Dead code: `QuickAddInput.tsx`, `PrioritySelect.tsx`, the store's `addFeature`, `updateFeature` and `removeFeature`, `FeatureCard`'s `isDragging` prop, the `dataTransfer` id.
- Duplication: `Dropdown`, `PropertyRow` and the label input are copied between `FeatureEditor` and `CreateFeatureDialog`; the editor uses a native date input, the dialog `DatePicker`; the order comparator is in the store twice and in `App.tsx`; `KanbanEpicBoard` repeats `featureMatchesEpicLane` inline.
- Strings: the `Esc`, `⌘S`, `⌘ Enter` and `⌘B` hints are hard-coded and show `⌘` on every platform. Ctrl/Cmd+B always starts Claude, not the agent picked in the dropdown.

**Needs:** [`baseline-tests`](baseline-tests.md), [`area-docs-baseline`](done/area-docs-baseline.md)
