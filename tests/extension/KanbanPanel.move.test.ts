import { describe, it, expect, vi, beforeEach, afterEach } from 'vitest'
import path from 'path'
import type { Feature } from '../../src/shared/types'

vi.mock('vscode', async () => (await import('./fakeVscode')).vscodeModule)

import { fake, createFakePanel, createFakeContext } from './fakeVscode'
import { KanbanPanel } from '../../src/extension/KanbanPanel'

// ---------------------------------------------------------------------------
// Board fixture
// ---------------------------------------------------------------------------

const FEATURES_DIR = '/workspace/.devtool/features'
const DONE_DIR = path.join(FEATURES_DIR, 'done')
const OLD = '2026-01-01T00:00:00.000Z'
const NOW = '2026-02-03T04:05:06.000Z'

interface CardSpec {
  id: string
  status: string
  order: string
  completedAt?: string
}

/** Card file text written by hand, so the fixture doesn't depend on the serializer under test. */
function cardText(c: CardSpec): string {
  return [
    '---',
    `id: "${c.id}"`,
    `status: "${c.status}"`,
    'priority: "medium"',
    'assignee: null',
    'epic: null',
    'dueDate: null',
    `created: "${OLD}"`,
    `modified: "${OLD}"`,
    `completedAt: ${c.completedAt ? `"${c.completedAt}"` : 'null'}`,
    'labels: []',
    `order: "${c.order}"`,
    '---',
    '',
    `# ${c.id}`
  ].join('\n')
}

function cardPath(c: CardSpec): string {
  return path.join(c.status === 'done' ? DONE_DIR : FEATURES_DIR, `${c.id}.md`)
}

// Distinct keys across the board; each column sorted by key.
const CARDS: CardSpec[] = [
  { id: 't1', status: 'todo', order: 'a0' },
  { id: 't2', status: 'todo', order: 'a1' },
  { id: 't3', status: 'todo', order: 'a2' },
  { id: 'p1', status: 'in-progress', order: 'a3' },
  { id: 'p2', status: 'in-progress', order: 'a4' },
  { id: 'd1', status: 'done', order: 'a5', completedAt: OLD },
  { id: 'd2', status: 'done', order: 'a6', completedAt: OLD }
]

/** Reads a card file back as frontmatter key/value pairs. */
function readCard(p: string): Record<string, string> {
  const text = fake.fs.files.get(p)
  if (text === undefined) throw new Error(`no file at ${p}`)
  const fm = text.split('---')[1]
  const out: Record<string, string> = {}
  for (const line of fm.split('\n')) {
    const m = line.match(/^(\w+):\s*(.*)$/)
    if (m) out[m[1]] = m[2].replace(/^"|"$/g, '')
  }
  return out
}

// ---------------------------------------------------------------------------
// Panel harness
// ---------------------------------------------------------------------------

let harness: ReturnType<typeof createFakePanel>

async function openBoard(): Promise<void> {
  for (const c of CARDS) fake.fs.writeText(cardPath(c), cardText(c))
  harness = createFakePanel()
  KanbanPanel.revive(harness.panel as never, { fsPath: '/extension' } as never, createFakeContext() as never)
  await harness.send({ type: 'ready' })
  harness.panel.webview.postMessage.mockClear()
  fake.fs.writeFile.mockClear()
  fake.fs.rename.mockClear()
}

function move(featureId: string, newStatus: string, newOrder: number): Promise<void> {
  return harness.send({ type: 'moveFeature', featureId, newStatus, newOrder })
}

function lastInit(): Feature[] {
  const inits = harness.posted<{ features: Feature[] }>('init')
  expect(inits.length).toBeGreaterThan(0)
  return inits[inits.length - 1].features
}

/** Card ids of one column in board order, as the webview would show them. */
function column(features: Feature[], status: string): string[] {
  return features
    .filter(f => f.status === status)
    .sort((a, b) => (a.order < b.order ? -1 : a.order > b.order ? 1 : 0))
    .map(f => f.id)
}

beforeEach(async () => {
  fake.reset()
  vi.useFakeTimers()
  vi.setSystemTime(new Date(NOW))
  await openBoard()
})

afterEach(() => {
  KanbanPanel.currentPanel?.dispose()
  vi.useRealTimers()
})

// ---------------------------------------------------------------------------
// moveFeature
// ---------------------------------------------------------------------------

describe('KanbanPanel moveFeature — within a column', () => {
  it('moves a card up to the given index', async () => {
    await move('t3', 'todo', 0)
    expect(column(lastInit(), 'todo')).toEqual(['t3', 't1', 't2'])
  })

  it('reads the index as a position in the column without the moved card', async () => {
    // t1 leaves index 0, so index 2 is the end of [t2, t3]
    await move('t1', 'todo', 2)
    expect(column(lastInit(), 'todo')).toEqual(['t2', 't3', 't1'])
  })

  it('places a card between its new neighbours', async () => {
    await move('t1', 'todo', 1)
    expect(column(lastInit(), 'todo')).toEqual(['t2', 't1', 't3'])
    const order = readCard(path.join(FEATURES_DIR, 't1.md')).order
    expect(order > 'a1' && order < 'a2').toBe(true)
  })

  it('appends when the index is past the end of the column', async () => {
    await move('t1', 'todo', 99)
    expect(column(lastInit(), 'todo')).toEqual(['t2', 't3', 't1'])
  })

  it('sets modified and leaves status, completedAt and the path unchanged', async () => {
    await move('t3', 'todo', 0)
    const written = readCard(path.join(FEATURES_DIR, 't3.md'))
    expect(written.status).toBe('todo')
    expect(written.modified).toBe(NOW)
    expect(written.completedAt).toBe('null')
    expect(fake.fs.rename).not.toHaveBeenCalled()
  })

  it('keeps completedAt for a reorder inside done', async () => {
    await move('d2', 'done', 0)
    expect(column(lastInit(), 'done')).toEqual(['d2', 'd1'])
    expect(readCard(path.join(DONE_DIR, 'd2.md')).completedAt).toBe(OLD)
  })
})

describe('KanbanPanel moveFeature — to another column', () => {
  it('changes the status and inserts at the index', async () => {
    await move('t2', 'in-progress', 1)
    const features = lastInit()
    expect(column(features, 'in-progress')).toEqual(['p1', 't2', 'p2'])
    expect(column(features, 'todo')).toEqual(['t1', 't3'])
  })

  it('writes the new status and modified, with completedAt still null, in place', async () => {
    await move('t2', 'in-progress', 1)
    const written = readCard(path.join(FEATURES_DIR, 't2.md'))
    expect(written.status).toBe('in-progress')
    expect(written.modified).toBe(NOW)
    expect(written.completedAt).toBe('null')
    expect(fake.fs.rename).not.toHaveBeenCalled()
  })

  it('moves the file into done/ and sets completedAt when moved into done', async () => {
    await move('t1', 'done', 0)
    expect(fake.fs.files.has(path.join(FEATURES_DIR, 't1.md'))).toBe(false)
    const written = readCard(path.join(DONE_DIR, 't1.md'))
    expect(written.status).toBe('done')
    expect(written.completedAt).toBe(NOW)
    expect(written.modified).toBe(NOW)

    const features = lastInit()
    expect(column(features, 'done')).toEqual(['t1', 'd1', 'd2'])
    expect(features.find(f => f.id === 't1')?.filePath).toBe(path.join('.devtool', 'features', 'done', 't1.md'))
  })

  it('moves the file out of done/ and clears completedAt when moved out of done', async () => {
    await move('d1', 'todo', 3)
    expect(fake.fs.files.has(path.join(DONE_DIR, 'd1.md'))).toBe(false)
    const written = readCard(path.join(FEATURES_DIR, 'd1.md'))
    expect(written.status).toBe('todo')
    expect(written.completedAt).toBe('null')
    expect(written.modified).toBe(NOW)

    const features = lastInit()
    expect(column(features, 'todo')).toEqual(['t1', 't2', 't3', 'd1'])
    expect(features.find(f => f.id === 'd1')?.filePath).toBe(path.join('.devtool', 'features', 'd1.md'))
  })
})

describe('KanbanPanel moveFeature — what is written and posted', () => {
  it('writes only the moved card, once', async () => {
    const before = new Map(fake.fs.files)
    await move('t2', 'in-progress', 0)

    expect(fake.fs.writeFile).toHaveBeenCalledOnce()
    expect(fake.fs.writeFile.mock.calls[0][0].fsPath).toBe(path.join(FEATURES_DIR, 't2.md'))
    for (const [p, text] of before) {
      if (p !== path.join(FEATURES_DIR, 't2.md')) expect(fake.fs.files.get(p)).toBe(text)
    }
  })

  it('writes the card before moving it into done/', async () => {
    await move('t1', 'done', 0)
    expect(fake.fs.writeFile).toHaveBeenCalledOnce()
    expect(fake.fs.writeFile.mock.calls[0][0].fsPath).toBe(path.join(FEATURES_DIR, 't1.md'))
    expect(fake.fs.rename).toHaveBeenCalledOnce()
    expect(fake.fs.writeFile.mock.invocationCallOrder[0]).toBeLessThan(fake.fs.rename.mock.invocationCallOrder[0])
  })

  it('posts one init right away, before any watcher event', async () => {
    await move('t3', 'todo', 0)
    expect(harness.posted()).toHaveLength(1)
    expect(harness.posted('init')).toHaveLength(1)
  })

  it('does nothing for an unknown card', async () => {
    await move('nope', 'todo', 0)
    expect(fake.fs.writeFile).not.toHaveBeenCalled()
    expect(harness.posted()).toHaveLength(0)
  })
})
