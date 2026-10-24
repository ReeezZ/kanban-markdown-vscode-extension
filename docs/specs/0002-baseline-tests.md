[README](../../README.md) › [Roadmap](../roadmap.md) › 0002 Baseline tests

# 0002 Baseline tests

## Status

Done — 2026-10-24

- Phase: 01 Foundation
- Card: baseline-tests
- Architecture: [Risks](../architecture.md#risks)

## Goal

Pin how a card move behaves today, in the standard view with distinct keys, so a refactor that changes where a moved card lands, what is written, or what the webview is told fails a test. Nothing changes for the person using the board.

Three seams:

- a fake `vscode` module, so `KanbanPanel` runs in Vitest: the tests send `moveFeature` and check the files and the posted messages;
- one pure key function in `src/shared`, used by the host and the webview instead of the two copies in `_moveFeature` and `App.tsx`;
- the existing `KanbanBoard` render harness, driven with drag events, for the webview's drop-index mapping.

## Done means

- `moveFeature` through the panel is covered: a reorder within a column, a status change, a move into `done` and one out of it (the file moves, `completedAt` set or cleared, `modified` set), and only the moved card's file written.
- `computeMoveOrder` in `src/shared/order.ts` is the only place a move's key is computed. `_moveFeature` and `App.tsx` call it, and it has unit tests.
- The watcher is covered for a move: events dropped while `_migrating` is set, one reload 100 ms after the last of several events, and the open card re-sent when its file differs from its last save (not when it matches).
- The drop-index mapping is covered: filtered index to column index, a downward move in the same column, a drop on its own position sends nothing, a drop on empty column space appends.
- The tests run in `pnpm test`. `KanbanPanel.ts` is in `coverage.include` and no longer in `coverage.exclude` in `vitest.config.mts`.

## Tests

- `tests/extension/fakeVscode.ts`: the fake (see Fake vscode module in [Decisions](#decisions)).
- `tests/extension/KanbanPanel.move.test.ts`: moves through the panel, and the watcher.
- `tests/shared/order.test.ts`: `computeMoveOrder`, covering:
  - an empty column;
  - index 0, the end and the middle;
  - a clamped negative index and a clamped index past the end;
  - the moved card excluded from its own column;
  - other columns ignored;
  - unsorted input.
- `tests/webview/components/KanbanBoard.test.tsx`: new drop cases. `getBoundingClientRect` is stubbed per card, so `clientY` picks before or after.

All of them pin the standard view (`epicFilter` undefined) with distinct keys.

## Explicitly out of scope

- A drop in an epic lane and equal keys: known bugs, pinned with their fixes (`epic-lane-drop-order`, `equal-order-keys`).
- The open card after a move across the `done` boundary: the watcher event's path is the old one, so the editor isn't refreshed. Close to `editor-save-overwrites-other-card`, and left to that card.
- Whether VS Code delivers watcher events while `_migrating` is still set. The test fires the event during the rename, so it pins the guard's logic, not real timing.
- Other messages, move all, archive, loading and its migrations, labels, the sidebar (see `code-review-passes`).
- Extracting the drop-index mapping from `KanbanBoard.tsx`.

## Decisions

- **Key function takes the whole move.** `computeMoveOrder(features, featureId, newStatus, index): string` filters the target column without the moved card, sorts by `order`, clamps the index and calls `generateKeyBetween`. It lives in `src/shared/order.ts`, since both sides import `src/shared` and `fractional-indexing` already. Taking only the neighbour keys would leave the filter and sort duplicated, and the epic-lane fix will need to add a lane parameter in one place.
- **Panel tests before the extraction.** The panel tests run green against today's `_moveFeature` first, so the extraction is a refactor under test.
- **Fake vscode module.** One module shared by the extension tests, mocked with `vi.mock('vscode', …)`. The panel is built with `KanbanPanel.revive(fakePanel, extensionUri, fakeContext)` because the constructor is private. The test sends messages through the captured `onDidReceiveMessage` handler and reads `postMessage` calls. The fake holds:
  - an in-memory fs (a `Map` from path to content, directories derived from the paths) implementing `readDirectory`, `readFile`, `writeFile`, `stat`, `rename`, `createDirectory` and `delete`, with spies;
  - `Uri.file`, `Uri.joinPath`, `FileType`, `RelativePattern` and `ViewColumn`;
  - `workspace.workspaceFolders`, `getConfiguration` (a settable map, so `get(key, default)` falls back to the default) and `onDidChangeConfiguration`;
  - `env.language`, a `workspaceState` memento and `window` message stubs;
  - `createFileSystemWatcher`, returning a watcher the test fires by hand (`fireChange`, `fireCreate`, `fireDelete`).

  fs operations fire no watcher events by themselves. A test fires them, or sets a hook on `rename` for the `_migrating` case. Fake timers drive the 100 ms debounce and fix `modified` and `completedAt` (`vi.setSystemTime`, `advanceTimersByTimeAsync`). It extends the in-memory pattern of `tests/extension/featureFileUtils.test.ts` rather than replacing it; that test keeps its own stub.
- **Drop mapping tested through the component.** The existing render harness and drag events cover it without moving code. If the epic-lane fix needs a pure function, it can extract one then, under these tests.

## Implementation order

1. `test(extension): add a fake vscode module and pin moveFeature through the panel`. Fake plus panel move tests, against today's code.
2. `refactor: compute a move's order key in one shared function`. Add `src/shared/order.ts`, call it from `_moveFeature` and `App.tsx`, panel tests still green.
3. `test(shared): cover computeMoveOrder`.
4. `test(extension): pin the watcher's guard, debounce and editor refresh`.
5. `test(webview): pin the drop-index mapping in KanbanBoard`.
6. `test: include KanbanPanel in coverage`, in `vitest.config.mts`.
