import { describe, expect, it } from 'vitest'

import {
  getDefaultExportWeekdays,
  resolveWeekdaysToDates
} from './exportWeekdays'

describe('getDefaultExportWeekdays', () => {
  it('returns saturday and sunday on friday', () => {
    const friday = new Date('2026-02-20T08:00:00')
    expect(getDefaultExportWeekdays(friday)).toEqual(['sat', 'sun'])
  })

  it('returns sunday on saturday', () => {
    const saturday = new Date('2026-02-21T08:00:00')
    expect(getDefaultExportWeekdays(saturday)).toEqual(['sun'])
  })

  it('returns empty selection on non-friday/saturday', () => {
    const tuesday = new Date('2026-02-17T08:00:00')
    expect(getDefaultExportWeekdays(tuesday)).toEqual([])
  })
})

describe('resolveWeekdaysToDates', () => {
  it('resolves selected weekdays to next occurrences within seven days', () => {
    const friday = new Date('2026-02-20T08:00:00')
    const result = resolveWeekdaysToDates(['sun', 'sat'], friday)

    expect(result).toEqual([
      { day: 'sat', date: '2026-02-21', deltaDays: 1 },
      { day: 'sun', date: '2026-02-22', deltaDays: 2 }
    ])
  })

  it('resolves same-day weekday with zero delta', () => {
    const monday = new Date('2026-02-16T08:00:00')
    const result = resolveWeekdaysToDates(['mon'], monday)

    expect(result).toEqual([{ day: 'mon', date: '2026-02-16', deltaDays: 0 }])
  })
})
