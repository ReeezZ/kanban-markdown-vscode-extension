import { describe, it, expect } from 'vitest'
import { computeMoveOrder } from '../../src/shared/order'

function c(id: string, status: string, order: string) {
  return { id, status, order }
}

// todo column in key order: t1 (a0), t2 (a1), t3 (a2); other columns use keys in between on purpose
const BOARD = [
  c('t1', 'todo', 'a0'),
  c('t2', 'todo', 'a1'),
  c('t3', 'todo', 'a2'),
  c('p1', 'in-progress', 'a0V'),
  c('p2', 'in-progress', 'a1V')
]

/** Asserts that `key` sorts strictly between `before` and `after` (null = open end). */
function expectBetween(key: string, before: string | null, after: string | null): void {
  if (before !== null) expect(key > before).toBe(true)
  if (after !== null) expect(key < after).toBe(true)
}

describe('computeMoveOrder', () => {
  it('returns a key for an empty column', () => {
    const key = computeMoveOrder(BOARD, 't1', 'review', 0)
    expect(typeof key).toBe('string')
    expect(key.length).toBeGreaterThan(0)
  })

  it('places before the first card at index 0', () => {
    expectBetween(computeMoveOrder(BOARD, 'p1', 'todo', 0), null, 'a0')
  })

  it('places after the last card at the end', () => {
    expectBetween(computeMoveOrder(BOARD, 'p1', 'todo', 3), 'a2', null)
  })

  it('places between the neighbours at a middle index', () => {
    expectBetween(computeMoveOrder(BOARD, 'p1', 'todo', 2), 'a1', 'a2')
  })

  it('clamps a negative index to the start', () => {
    expectBetween(computeMoveOrder(BOARD, 'p1', 'todo', -5), null, 'a0')
  })

  it('clamps an index past the end to the end', () => {
    expectBetween(computeMoveOrder(BOARD, 'p1', 'todo', 99), 'a2', null)
  })

  it('leaves the moved card out of its own column', () => {
    // without t1 the column is [t2, t3], so index 1 is between them
    expectBetween(computeMoveOrder(BOARD, 't1', 'todo', 1), 'a1', 'a2')
    // and index 2 is the end
    expectBetween(computeMoveOrder(BOARD, 't1', 'todo', 2), 'a2', null)
  })

  it('ignores cards in other columns', () => {
    // p1 (a0V) sits between t1 and t2 by key, but is in another column
    const key = computeMoveOrder(BOARD, 't3', 'todo', 1)
    expectBetween(key, 'a0', 'a1')
  })

  it('sorts the column by key rather than by array order', () => {
    const shuffled = [BOARD[2], BOARD[0], BOARD[4], BOARD[1], BOARD[3]]
    expectBetween(computeMoveOrder(shuffled, 'p1', 'todo', 1), 'a0', 'a1')
  })
})
