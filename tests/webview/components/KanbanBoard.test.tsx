// @vitest-environment jsdom
import { describe, it, expect, vi, beforeEach } from 'vitest'
import { render, screen, within, fireEvent, createEvent } from '@testing-library/react'
import userEvent from '@testing-library/user-event'
import { KanbanBoard } from '../../../src/webview/components/KanbanBoard'
import { useStore } from '../../../src/webview/store'
import type { Feature, KanbanColumn } from '../../../src/shared/types'

// ---------------------------------------------------------------------------
// Mock vscode API
// ---------------------------------------------------------------------------

const { mockPostMessage } = vi.hoisted(() => ({ mockPostMessage: vi.fn() }))

vi.mock('../../../src/webview/vscodeApi', () => ({
  vscode: { postMessage: mockPostMessage }
}))

// ---------------------------------------------------------------------------
// Store reset
// ---------------------------------------------------------------------------

const initialState = useStore.getState()

beforeEach(() => {
  useStore.setState(initialState, true)
  mockPostMessage.mockClear()
})

// ---------------------------------------------------------------------------
// Helpers
// ---------------------------------------------------------------------------

const DEFAULT_COLUMNS: KanbanColumn[] = [
  { id: 'backlog', name: 'Backlog', color: '#6b7280' },
  { id: 'todo',    name: 'To Do',   color: '#3b82f6' },
  { id: 'done',    name: 'Done',    color: '#22c55e' },
]

function makeFeature(overrides: Partial<Feature> = {}): Feature {
  return {
    id: 'feat-1',
    status: 'backlog',
    priority: 'medium',
    assignee: null,
    epic: null,
    dueDate: null,
    created: '2026-01-01T00:00:00.000Z',
    modified: '2026-01-01T00:00:00.000Z',
    completedAt: null,
    labels: [],
    order: 'a0',
    content: '# My Feature',
    filePath: '/workspace/features/feat.md',
    ...overrides
  }
}

function setup(overrides: {
  onFeatureClick?: (feature: Feature) => void
  onAddFeature?: (status: string) => void
  onMoveFeature?: (featureId: string, newStatus: string, newOrder: number) => void
  epicFilter?: string | null
} = {}) {
  const onFeatureClick: (feature: Feature) => void = overrides.onFeatureClick ?? vi.fn()
  const onAddFeature: (status: string) => void     = overrides.onAddFeature   ?? vi.fn()
  const onMoveFeature: (featureId: string, newStatus: string, newOrder: number) => void = overrides.onMoveFeature ?? vi.fn()
  const user = userEvent.setup()
  render(
    <KanbanBoard
      onFeatureClick={onFeatureClick}
      onAddFeature={onAddFeature}
      onMoveFeature={onMoveFeature}
      {...(overrides.epicFilter !== undefined ? { epicFilter: overrides.epicFilter } : {})}
    />
  )
  return { user, onFeatureClick, onAddFeature, onMoveFeature }
}

// ---------------------------------------------------------------------------
// Rendering — columns
// ---------------------------------------------------------------------------

describe('KanbanBoard — column rendering', () => {
  it('renders one column per entry in the store', () => {
    useStore.setState({ columns: DEFAULT_COLUMNS })
    setup()
    expect(screen.getByText('Backlog')).toBeInTheDocument()
    expect(screen.getByText('To Do')).toBeInTheDocument()
    expect(screen.getByText('Done')).toBeInTheDocument()
  })

  it('renders nothing when there are no columns', () => {
    useStore.setState({ columns: [] })
    const noopClick: (feature: Feature) => void = vi.fn()
    const noopAdd: (status: string) => void = vi.fn()
    const noopMove: (id: string, status: string, order: number) => void = vi.fn()
    render(<KanbanBoard onFeatureClick={noopClick} onAddFeature={noopAdd} onMoveFeature={noopMove} />)
    // No column headings
    expect(screen.queryByRole('heading', { level: 3 })).not.toBeInTheDocument()
  })
})

// ---------------------------------------------------------------------------
// Rendering — features in columns
// ---------------------------------------------------------------------------

describe('KanbanBoard — feature placement', () => {
  it('shows a feature card in the correct column', () => {
    useStore.setState({
      columns: DEFAULT_COLUMNS,
      features: [makeFeature({ status: 'todo', content: '# Inbox task' })]
    })
    setup()
    expect(screen.getByText('Inbox task')).toBeInTheDocument()
  })

  it('places features only in their matching column', () => {
    useStore.setState({
      columns: DEFAULT_COLUMNS,
      features: [
        makeFeature({ id: 'a', status: 'backlog', content: '# BacklogCard' }),
        makeFeature({ id: 'b', status: 'done',    content: '# DoneCard' }),
      ]
    })
    setup()
    expect(screen.getByText('BacklogCard')).toBeInTheDocument()
    expect(screen.getByText('DoneCard')).toBeInTheDocument()
    // Both headings present but in different column DOM sections
    const heading1 = screen.getByText('BacklogCard').closest('[class*="rounded-lg"]')
    const heading2 = screen.getByText('DoneCard').closest('[class*="rounded-lg"]')
    expect(heading1).not.toBe(heading2)
  })

  it('shows "No features" when a column has no cards', () => {
    useStore.setState({ columns: DEFAULT_COLUMNS, features: [] })
    setup()
    const noFeatureMessages = screen.getAllByText('No features')
    expect(noFeatureMessages).toHaveLength(DEFAULT_COLUMNS.length)
  })
})

// ---------------------------------------------------------------------------
// Feature count badge
// ---------------------------------------------------------------------------

describe('KanbanBoard — feature count badge', () => {
  it('displays the correct feature count for each column', () => {
    useStore.setState({
      columns: DEFAULT_COLUMNS,
      features: [
        makeFeature({ id: '1', status: 'backlog' }),
        makeFeature({ id: '2', status: 'backlog' }),
        makeFeature({ id: '3', status: 'todo' }),
      ]
    })
    setup()
    // Each column header renders a badge with the count
    // 'Backlog' column has 2, 'To Do' has 1, 'Done' has 0
    const badges = screen.getAllByText(/^\d+$/)
    const badgeValues = badges.map(b => b.textContent)
    expect(badgeValues).toContain('2')
    expect(badgeValues).toContain('1')
    expect(badgeValues).toContain('0')
  })
})

// ---------------------------------------------------------------------------
// onFeatureClick callback
// ---------------------------------------------------------------------------

describe('KanbanBoard — onFeatureClick', () => {
  it('calls onFeatureClick with the feature when a card is clicked', async () => {
    const feature = makeFeature({ status: 'backlog', content: '# Click Me' })
    useStore.setState({ columns: DEFAULT_COLUMNS, features: [feature] })
    const { user, onFeatureClick } = setup()
    await user.click(screen.getByRole('heading', { level: 3, name: 'Click Me' }))
    expect(onFeatureClick).toHaveBeenCalledOnce()
    expect(onFeatureClick).toHaveBeenCalledWith(expect.objectContaining({ id: feature.id }))
  })
})

// ---------------------------------------------------------------------------
// onAddFeature callback
// ---------------------------------------------------------------------------

describe('KanbanBoard — onAddFeature', () => {
  it('calls onAddFeature with the column id when the + button is clicked', async () => {
    useStore.setState({ columns: DEFAULT_COLUMNS })
    const { user, onAddFeature } = setup()
    await user.click(screen.getByTitle('Add to Backlog'))
    expect(onAddFeature).toHaveBeenCalledOnce()
    expect(onAddFeature).toHaveBeenCalledWith('backlog')
  })
})

// ---------------------------------------------------------------------------
// Collapse / expand
// ---------------------------------------------------------------------------

describe('KanbanBoard — collapse/expand', () => {
  it('replaces the column with a collapsed view and posts toggleColumnCollapsed on collapse', async () => {
    useStore.setState({ columns: DEFAULT_COLUMNS })
    const { user } = setup()
    await user.click(screen.getByTitle('Collapse Backlog'))
    // Column content (feature area) gone; collapsed button shows the column name
    // The collapsed button still renders the column name
    expect(mockPostMessage).toHaveBeenCalledWith({ type: 'toggleColumnCollapsed', columnId: 'backlog' })
    expect(screen.queryByTitle('Collapse Backlog')).not.toBeInTheDocument()
  })

  it('re-expands a collapsed column when clicked and posts another toggle message', async () => {
    // Start with column already collapsed
    useStore.setState({
      columns: DEFAULT_COLUMNS,
      collapsedColumns: new Set(['backlog'])
    })
    const { user } = setup()
    // Collapsed column is rendered as a button; click it to expand
    // CollapsedColumn renders the name as readable text
    const collapsedBtn = screen.getByText('Backlog').closest('button')!
    await user.click(collapsedBtn)
    expect(mockPostMessage).toHaveBeenCalledWith({ type: 'toggleColumnCollapsed', columnId: 'backlog' })
    // After expanding, the Collapse button reappears
    expect(screen.getByTitle('Collapse Backlog')).toBeInTheDocument()
  })
})

// ---------------------------------------------------------------------------
// Move all cards
// ---------------------------------------------------------------------------

describe('KanbanBoard — moveAllCards', () => {
  it('posts moveAllCards when a target column is chosen from the submenu', async () => {
    useStore.setState({
      columns: DEFAULT_COLUMNS,
      features: [makeFeature({ status: 'backlog' })]
    })
    const { user } = setup()

    // Open the column options menu for Backlog
    const backlogSection = screen.getByTitle('Collapse Backlog').closest('[class*="rounded-lg"]') as HTMLElement
    const menuBtn = within(backlogSection).getByTitle('Column options')
    await user.click(menuBtn)

    // Trigger mouseEnter on the "Move all cards" wrapper div to open submenu
    const moveAllWrapper = screen.getByText('Move all cards in this list').closest('div')!
    fireEvent.mouseEnter(moveAllWrapper)

    // Click 'To Do' as the target — scoped to the Backlog section to avoid
    // matching the 'Collapse To Do' / 'Add to To Do' buttons in other columns
    await user.click(within(backlogSection).getByRole('button', { name: 'To Do' }))

    expect(mockPostMessage).toHaveBeenCalledWith({
      type: 'moveAllCards',
      sourceColumnId: 'backlog',
      targetColumnId: 'todo'
    })
  })

  it('includes epicLane when the board is scoped to an epic swim lane', async () => {
    useStore.setState({
      columns: DEFAULT_COLUMNS,
      features: [makeFeature({ status: 'backlog', epic: 'Payments' })]
    })
    const { user } = setup({ epicFilter: 'Payments' })

    const backlogSection = screen.getByTitle('Collapse Backlog').closest('[class*="rounded-lg"]') as HTMLElement
    const menuBtn = within(backlogSection).getByTitle('Column options')
    await user.click(menuBtn)

    const moveAllWrapper = screen.getByText('Move all cards in this list').closest('div')!
    fireEvent.mouseEnter(moveAllWrapper)

    await user.click(within(backlogSection).getByRole('button', { name: 'To Do' }))

    expect(mockPostMessage).toHaveBeenCalledWith({
      type: 'moveAllCards',
      sourceColumnId: 'backlog',
      targetColumnId: 'todo',
      epicLane: 'Payments'
    })
  })
})

// ---------------------------------------------------------------------------
// Archive all cards (done column only)
// ---------------------------------------------------------------------------

describe('KanbanBoard — archiveAllCards', () => {
  it('posts archiveAllCards when the option is clicked on the done column', async () => {
    useStore.setState({
      columns: DEFAULT_COLUMNS,
      features: [makeFeature({ status: 'done' })]
    })
    const { user } = setup()

    // Open the column options menu for Done
    const doneSection = screen.getByTitle('Collapse Done').closest('[class*="rounded-lg"]') as HTMLElement
    const menuBtn = within(doneSection).getByTitle('Column options')
    await user.click(menuBtn)

    await user.click(screen.getByRole('button', { name: /archive all cards/i }))

    expect(mockPostMessage).toHaveBeenCalledWith({
      type: 'archiveAllCards',
      sourceColumnId: 'done'
    })
  })

  it('does not show "Archive all cards" on non-done columns', async () => {
    useStore.setState({
      columns: DEFAULT_COLUMNS,
      features: [makeFeature({ status: 'backlog' })]
    })
    const { user } = setup()

    const backlogSection = screen.getByTitle('Collapse Backlog').closest('[class*="rounded-lg"]') as HTMLElement
    const menuBtn = within(backlogSection).getByTitle('Column options')
    await user.click(menuBtn)

    expect(screen.queryByRole('button', { name: /archive all cards/i })).not.toBeInTheDocument()
  })
})

// ---------------------------------------------------------------------------
// Layout
// ---------------------------------------------------------------------------

describe('KanbanBoard — layout', () => {
  it('renders with horizontal layout by default', () => {
    useStore.setState({ columns: DEFAULT_COLUMNS, layout: 'horizontal' })
    setup()
    // In horizontal mode the outer wrapper has overflow-x-auto class
    const wrapper = screen.getByText('Backlog').closest('[class*="overflow-x-auto"]')
    expect(wrapper).toBeInTheDocument()
  })

  it('renders with vertical layout when layout is "vertical"', () => {
    useStore.setState({ columns: DEFAULT_COLUMNS, layout: 'vertical' })
    setup()
    const wrapper = screen.getByText('Backlog').closest('[class*="overflow-y-auto"]')
    expect(wrapper).toBeInTheDocument()
  })
})

// ---------------------------------------------------------------------------
// Drag and drop — drop index sent to onMoveFeature
// ---------------------------------------------------------------------------

describe('KanbanBoard — drop index', () => {
  // To Do in key order: A, B, C, D, E. The priority filter hides B and D,
  // so the column shows A, C, E. X waits in Backlog.
  function setupBoard() {
    useStore.setState({
      columns: DEFAULT_COLUMNS,
      priorityFilter: 'high',
      features: [
        makeFeature({ id: 'A', status: 'todo', order: 'a0', priority: 'high', content: '# Card A' }),
        makeFeature({ id: 'B', status: 'todo', order: 'a1', priority: 'low',  content: '# Card B' }),
        makeFeature({ id: 'C', status: 'todo', order: 'a2', priority: 'high', content: '# Card C' }),
        makeFeature({ id: 'D', status: 'todo', order: 'a3', priority: 'low',  content: '# Card D' }),
        makeFeature({ id: 'E', status: 'todo', order: 'a4', priority: 'high', content: '# Card E' }),
        makeFeature({ id: 'X', status: 'backlog', order: 'a5', priority: 'high', content: '# Card X' })
      ]
    })
    return setup()
  }

  function card(title: string): HTMLElement {
    const el = screen.getByText(title).closest('[draggable="true"]') as HTMLElement | null
    if (!el) throw new Error(`no draggable card for ${title}`)
    // jsdom has no layout: give every card a 100px box, so clientY picks its upper or lower half
    el.getBoundingClientRect = () => ({ top: 0, bottom: 100, height: 100, left: 0, right: 0, width: 0, x: 0, y: 0, toJSON: () => ({}) })
    return el
  }

  function todoColumn(): HTMLElement {
    return screen.getByText('To Do').closest('[class*="rounded-lg"]') as HTMLElement
  }

  const dataTransfer = { setData: () => {}, effectAllowed: '', dropEffect: '' }

  function dragStart(title: string): void {
    fireEvent.dragStart(card(title), { dataTransfer })
  }

  function dragOver(title: string, half: 'upper' | 'lower'): void {
    const el = card(title)
    // jsdom has no DragEvent, so clientY from the init dict would be dropped
    const event = createEvent.dragOver(el, { dataTransfer })
    Object.defineProperty(event, 'clientY', { value: half === 'upper' ? 10 : 90 })
    fireEvent(el, event)
  }

  function drop(target: HTMLElement): void {
    fireEvent.drop(target, { dataTransfer })
  }

  it('maps a drop before a visible card to that card\'s position in the full column', () => {
    const { onMoveFeature } = setupBoard()
    dragStart('Card X')
    dragOver('Card C', 'upper')
    drop(card('Card C'))
    // C is at index 2 of A, B, C, D, E
    expect(onMoveFeature).toHaveBeenCalledWith('X', 'todo', 2)
  })

  it('places a drop after the last visible card right after it', () => {
    const { onMoveFeature } = setupBoard()
    dragStart('Card X')
    dragOver('Card E', 'lower')
    drop(card('Card E'))
    expect(onMoveFeature).toHaveBeenCalledWith('X', 'todo', 5)
  })

  it('appends a drop on empty column space after the last visible card', () => {
    const { onMoveFeature } = setupBoard()
    dragStart('Card X')
    drop(todoColumn())
    expect(onMoveFeature).toHaveBeenCalledWith('X', 'todo', 5)
  })

  it('corrects the index for a downward move in the same column', () => {
    const { onMoveFeature } = setupBoard()
    dragStart('Card A')
    dragOver('Card C', 'lower')
    drop(card('Card C'))
    // shown: A, C, E → A lands before E; without A the column is B, C, D, E, so E is at 3
    expect(onMoveFeature).toHaveBeenCalledWith('A', 'todo', 3)
  })

  it('sends nothing for a drop on the card\'s own position', () => {
    const { onMoveFeature } = setupBoard()
    dragStart('Card C')
    dragOver('Card C', 'upper')
    drop(card('Card C'))
    dragStart('Card C')
    dragOver('Card C', 'lower')
    drop(card('Card C'))
    expect(onMoveFeature).not.toHaveBeenCalled()
  })
})
