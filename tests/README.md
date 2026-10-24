[README](../README.md) › Tests

# Tests

How the tests are split, where a new one goes, and why. The commands and the checks that run them are in [Tests in docs/development.md](../docs/development.md#tests).

## Layers

- **Unit and component tests** run in Vitest (`pnpm test`), with no VS Code. `vitest.config.mts` picks the environment per folder:
  - `tests/shared/` runs in node, against the code both sides share.
  - `tests/webview/` runs in jsdom. Components render with the real store; `src/webview/vscodeApi` is mocked, so a test reads what the webview posts.
  - `tests/extension/` runs in node. `vscode` is replaced by the fake in `tests/extension/fakeVscode.ts` (see [The fake vscode module](#the-fake-vscode-module)).
- **Integration tests** run in Mocha inside a real VS Code started by `@vscode/test-electron` (`pnpm test:integration`). `tsc` compiles them, with `src/extension` and `src/shared`, into `out/`, apart from the esbuild bundle the extension runs from. So a test imports its own copy of a module, not the running extension's, and `activate()` returns nothing a test could reach. They suit what needs the real `vscode`: file system behaviour, activation, commands.
- **No UI tests** drive the real webview; the idea is parked in the [backlog](../backlog/) (`webview-smoke-tests`).

## Where a test goes

- Logic that doesn't import `vscode` (most of `src/shared/`, pure helpers): a plain unit test. Moving logic out of `vscode`-bound code into such a function is the cheapest way to test it.
- Host code that imports `vscode`: `tests/extension/`, on the fake. `KanbanPanel` is built with `KanbanPanel.revive()` and driven by the messages the webview would send.
- What the fake can't answer, such as real fs semantics or when watcher events arrive: an integration test.
- The webview: component tests in jsdom, through the store and DOM events. jsdom has no `DragEvent` and no layout, so a drag test sets `clientY` on the event itself and stubs `getBoundingClientRect`; passed in the event's init, `clientY` is dropped silently.
- Host↔webview messages: each side on its own, against the types in `src/shared/types.ts`. The host tests read what the fake panel's `postMessage` received; the webview tests read the mocked `vscodeApi`.

## The fake vscode module

`vscode` isn't an npm package: the extension host supplies it at runtime, and `@types/vscode` holds only its types. Any test outside VS Code needs a stand-in. Ours is one module shared by the extension tests, mocked with `vi.mock('vscode', …)` in each test file that needs it:

- an in-memory fs, a configuration map, a `workspaceState` memento, a watcher, and a webview panel that records `postMessage` and lets the test send messages;
- fs operations fire no watcher events. A test fires them by hand, so it decides when the panel sees a change (`fake.onRename` fires one during a rename);
- it holds only what a test needs. A new test adds to it, not a second stub.

Its behaviour is our reading of VS Code's, and nothing checks it against the real one yet: whether `writeFile` creates parent folders, whether `rename` onto an existing file throws, when watcher events arrive. Contract tests for that are parked (`fake-vscode-contract-tests`). Tests in `tests/` aren't typechecked or linted either, so the fake isn't held to the `vscode` types (`typecheck-tests`).

## Decisions

- **Own fake rather than `jest-mock-vscode`.** It's the maintained library for this (Code Spell Checker uses it with Vitest), but what the panel tests need is missing there: the webview panel and the file watcher are bare mocks, `rename`, `delete` and `readDirectory` are empty stubs, and the rest of the fs goes to the real disk.
- **Mock the module rather than wrap the API.** Larger extensions put the `vscode` API behind their own interfaces and inject them (vscode-python), or keep logic in packages that don't import `vscode` (GitLens), which keeps fakes small. `KanbanPanel` is upstream code calling `vscode` directly, so the module mock fits it as it is; injecting its fs and watcher is an option for the review refactors.
- **Mocha stays for the integration tests.** Vitest can't run inside the extension host; Microsoft's runners (`@vscode/test-electron`, `@vscode/test-cli`) use Mocha. Moving to `@vscode/test-cli` is parked (`integration-test-runner`).
- **Two coverage reports.** `pnpm test:coverage` covers the Vitest tests only; merging in the integration tests isn't a documented practice, and their compiled `out/` files don't map line for line onto the sources Vitest measures.
