/**
 * In-memory stand-in for the `vscode` module, enough to construct a
 * `KanbanPanel` and drive it through webview messages in Vitest.
 *
 * Use it from a test file with
 *   vi.mock('vscode', async () => (await import('./fakeVscode')).vscodeModule)
 * and import `fake` from this module to set up files and settings and to
 * read what the panel did. Call `fake.reset()` in `beforeEach`.
 *
 * The fs is a map of file paths to text. Its operations never fire watcher
 * events: a test fires them by hand through `fake.watchers`, so it controls
 * when (and whether) the panel sees a change. `fake.onRename` is called
 * inside `rename`, for tests that need an event while a rename is in flight.
 */
import path from 'path'
import { vi } from 'vitest'

// ---------------------------------------------------------------------------
// Events and disposables
// ---------------------------------------------------------------------------

interface Disposable { dispose(): void }

type Listener<T> = (e: T) => unknown

class FakeEventEmitter<T> {
  private listeners: Listener<T>[] = []

  /** Matches the `vscode.Event` call shape: (listener, thisArgs?, disposables?). */
  event = (listener: Listener<T>, _thisArgs?: unknown, disposables?: Disposable[]): Disposable => {
    this.listeners.push(listener)
    const d = { dispose: () => { this.listeners = this.listeners.filter(l => l !== listener) } }
    disposables?.push(d)
    return d
  }

  /** Calls every listener and returns what they returned (promises included). */
  fire(e: T): unknown[] {
    return this.listeners.map(l => l(e))
  }
}

// ---------------------------------------------------------------------------
// Uri, enums, patterns
// ---------------------------------------------------------------------------

export interface FakeUri {
  fsPath: string
  path: string
  scheme: string
  toString(): string
}

function uriFile(p: string): FakeUri {
  return { fsPath: p, path: p, scheme: 'file', toString: () => `file://${p}` }
}

const Uri = {
  file: uriFile,
  joinPath: (base: FakeUri, ...segments: string[]) => uriFile(path.join(base.fsPath, ...segments))
}

const FileType = { Unknown: 0, File: 1, Directory: 2, SymbolicLink: 64 }
const ViewColumn = { Active: -1, Beside: -2, One: 1, Two: 2, Three: 3 }

class RelativePattern {
  constructor(public base: string, public pattern: string) {}
}

// ---------------------------------------------------------------------------
// File system
// ---------------------------------------------------------------------------

function enoent(p: string): Error {
  return Object.assign(new Error(`ENOENT: ${p}`), { code: 'FileNotFound' })
}

class FakeFs {
  files = new Map<string, string>()
  dirs = new Set<string>()

  private addDirWithParents(dir: string): void {
    let d = dir
    while (!this.dirs.has(d)) {
      this.dirs.add(d)
      const parent = path.dirname(d)
      if (parent === d) break
      d = parent
    }
  }

  writeText(p: string, content: string): void {
    this.addDirWithParents(path.dirname(p))
    this.files.set(p, content)
  }

  readDirectory = vi.fn(async (uri: FakeUri): Promise<[string, number][]> => {
    const dir = uri.fsPath
    if (!this.dirs.has(dir)) throw enoent(dir)
    const entries: [string, number][] = []
    for (const p of this.files.keys()) {
      if (path.dirname(p) === dir) entries.push([path.basename(p), FileType.File])
    }
    for (const d of this.dirs) {
      if (d !== dir && path.dirname(d) === dir) entries.push([path.basename(d), FileType.Directory])
    }
    return entries
  })

  readFile = vi.fn(async (uri: FakeUri): Promise<Uint8Array> => {
    const content = this.files.get(uri.fsPath)
    if (content === undefined) throw enoent(uri.fsPath)
    return new TextEncoder().encode(content)
  })

  writeFile = vi.fn(async (uri: FakeUri, bytes: Uint8Array): Promise<void> => {
    this.writeText(uri.fsPath, new TextDecoder().decode(bytes))
  })

  stat = vi.fn(async (uri: FakeUri) => {
    if (this.files.has(uri.fsPath)) return { type: FileType.File, ctime: 0, mtime: 0, size: 0 }
    if (this.dirs.has(uri.fsPath)) return { type: FileType.Directory, ctime: 0, mtime: 0, size: 0 }
    throw enoent(uri.fsPath)
  })

  rename = vi.fn(async (source: FakeUri, target: FakeUri): Promise<void> => {
    const content = this.files.get(source.fsPath)
    if (content === undefined) throw enoent(source.fsPath)
    if (this.files.has(target.fsPath)) throw new Error(`EEXIST: ${target.fsPath}`)
    fake.onRename?.(source, target)
    this.files.delete(source.fsPath)
    this.writeText(target.fsPath, content)
  })

  createDirectory = vi.fn(async (uri: FakeUri): Promise<void> => {
    this.addDirWithParents(uri.fsPath)
  })

  delete = vi.fn(async (uri: FakeUri): Promise<void> => {
    const p = uri.fsPath
    if (this.files.delete(p)) return
    if (!this.dirs.has(p)) throw enoent(p)
    for (const f of [...this.files.keys()]) if (f.startsWith(p + path.sep)) this.files.delete(f)
    for (const d of [...this.dirs]) if (d === p || d.startsWith(p + path.sep)) this.dirs.delete(d)
  })
}

// ---------------------------------------------------------------------------
// Watcher
// ---------------------------------------------------------------------------

/** A file system watcher whose events only fire when a test calls `fire*`. */
export class FakeWatcher {
  private changeEmitter = new FakeEventEmitter<FakeUri>()
  private createEmitter = new FakeEventEmitter<FakeUri>()
  private deleteEmitter = new FakeEventEmitter<FakeUri>()
  disposed = false

  constructor(public pattern: RelativePattern) {}

  onDidChange = this.changeEmitter.event
  onDidCreate = this.createEmitter.event
  onDidDelete = this.deleteEmitter.event

  fireChange(p: string): void { this.changeEmitter.fire(uriFile(p)) }
  fireCreate(p: string): void { this.createEmitter.fire(uriFile(p)) }
  fireDelete(p: string): void { this.deleteEmitter.fire(uriFile(p)) }

  dispose(): void { this.disposed = true }
}

// ---------------------------------------------------------------------------
// Shared state the tests set up and read
// ---------------------------------------------------------------------------

const configEmitter = new FakeEventEmitter<{ affectsConfiguration(section: string): boolean }>()

export const fake = {
  workspaceRoot: '/workspace',
  fs: new FakeFs(),
  /** Settings by full key, e.g. `kanban-markdown.featuresDirectory`. */
  config: new Map<string, unknown>(),
  watchers: [] as FakeWatcher[],
  onRename: undefined as ((source: FakeUri, target: FakeUri) => void) | undefined,

  /** The watcher the panel set up last (it replaces the old one on a directory change). */
  get watcher(): FakeWatcher {
    const w = this.watchers[this.watchers.length - 1]
    if (!w) throw new Error('no file system watcher was created')
    return w
  },

  reset(): void {
    this.workspaceRoot = '/workspace'
    this.fs = new FakeFs()
    this.config = new Map()
    this.watchers = []
    this.onRename = undefined
  }
}

// ---------------------------------------------------------------------------
// The module object handed to vi.mock('vscode')
// ---------------------------------------------------------------------------

export const vscodeModule = {
  Uri,
  FileType,
  ViewColumn,
  RelativePattern,
  env: { language: 'en' },
  commands: { executeCommand: vi.fn(async () => undefined) },
  window: {
    activeTextEditor: undefined,
    showErrorMessage: vi.fn(async () => undefined),
    showWarningMessage: vi.fn(async () => undefined),
    showInformationMessage: vi.fn(async () => undefined),
    showTextDocument: vi.fn(async () => undefined)
  },
  workspace: {
    // Getters, so the module object always points at the current `fake` state after a reset.
    get fs() { return fake.fs },
    get workspaceFolders() {
      return fake.workspaceRoot ? [{ uri: uriFile(fake.workspaceRoot), name: 'workspace', index: 0 }] : undefined
    },
    getConfiguration: (section?: string) => ({
      get: <T>(key: string, defaultValue?: T): T | undefined => {
        const full = section ? `${section}.${key}` : key
        return fake.config.has(full) ? (fake.config.get(full) as T) : defaultValue
      },
      update: vi.fn(async () => undefined)
    }),
    onDidChangeConfiguration: configEmitter.event,
    createFileSystemWatcher: (pattern: RelativePattern) => {
      const w = new FakeWatcher(pattern)
      fake.watchers.push(w)
      return w
    },
    openTextDocument: vi.fn(async (uri: FakeUri) => ({ uri }))
  }
}

// ---------------------------------------------------------------------------
// Panel and extension context
// ---------------------------------------------------------------------------

/**
 * A webview panel that records what the extension posts and lets the test
 * send messages as if they came from the webview. `send` resolves once the
 * panel's handler has finished.
 */
export function createFakePanel() {
  let handler: ((message: unknown) => Promise<void> | void) | undefined
  const disposeEmitter = new FakeEventEmitter<void>()

  const panel = {
    viewColumn: ViewColumn.One,
    webview: {
      options: {},
      html: '',
      cspSource: 'vscode-resource:',
      asWebviewUri: (uri: FakeUri) => uri,
      postMessage: vi.fn(async (_message: unknown) => true),
      onDidReceiveMessage: (listener: (message: unknown) => Promise<void> | void, _thisArgs?: unknown, disposables?: Disposable[]) => {
        handler = listener
        const d = { dispose: () => { handler = undefined } }
        disposables?.push(d)
        return d
      }
    },
    onDidDispose: disposeEmitter.event,
    reveal: vi.fn(),
    dispose: vi.fn()
  }

  async function send(message: unknown): Promise<void> {
    if (!handler) throw new Error('the panel has no message handler')
    await handler(message)
  }

  /** Messages posted to the webview, optionally only those of one `type`. */
  function posted<T = Record<string, unknown>>(type?: string): T[] {
    const all = panel.webview.postMessage.mock.calls.map(c => c[0] as T & { type: string })
    return type ? all.filter(m => m.type === type) : all
  }

  return { panel, send, posted }
}

/** An extension context with an in-memory `workspaceState`. */
export function createFakeContext() {
  const state = new Map<string, unknown>()
  return {
    subscriptions: [] as Disposable[],
    extensionUri: uriFile('/extension'),
    extensionPath: '/extension',
    workspaceState: {
      get: <T>(key: string, defaultValue?: T): T | undefined =>
        state.has(key) ? (state.get(key) as T) : defaultValue,
      update: vi.fn(async (key: string, value: unknown) => { state.set(key, value) }),
      keys: () => [...state.keys()]
    }
  }
}
