import { generateKeyBetween } from 'fractional-indexing'
import type { Feature } from './types'

/**
 * The `order` key a card gets when it is moved to `index` in the `newStatus`
 * column. Shared by the host (which writes it) and the webview (which shows
 * the move before the host confirms it), so both land the card in the same place.
 *
 * `index` is a position in the target column without the moved card, sorted
 * by `order`; it is clamped to that column. Throws (from `generateKeyBetween`)
 * when the two neighbours at `index` share a key.
 */
export function computeMoveOrder(
  features: readonly Pick<Feature, 'id' | 'status' | 'order'>[],
  featureId: string,
  newStatus: string,
  index: number
): string {
  const targetColumn = features
    .filter(f => f.status === newStatus && f.id !== featureId)
    .sort((a, b) => (a.order < b.order ? -1 : a.order > b.order ? 1 : 0))

  const clamped = Math.max(0, Math.min(index, targetColumn.length))
  const before = clamped > 0 ? targetColumn[clamped - 1].order : null
  const after = clamped < targetColumn.length ? targetColumn[clamped].order : null
  return generateKeyBetween(before, after)
}
