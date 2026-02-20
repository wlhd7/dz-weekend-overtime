/// <reference types="vitest" />

import { afterEach, describe, expect, it, vi } from 'vitest'
import { buildRollingDayOptions, getTomorrowToken } from './rollingDayOptions'

const DAY_TOKENS = ['sun', 'mon', 'tue', 'wed', 'thu', 'fri', 'sat'] as const

const getToken = (date: Date): string => DAY_TOKENS[date.getDay()]

describe('rolling day options', () => {
  afterEach(() => {
    vi.useRealTimers()
  })

  it('starts options from tomorrow', () => {
    vi.useFakeTimers()
    const baseDate = new Date(2026, 1, 20)
    vi.setSystemTime(baseDate)

    const options = buildRollingDayOptions()
    expect(options).toHaveLength(7)

    const tomorrow = new Date(baseDate)
    tomorrow.setDate(baseDate.getDate() + 1)
    expect(options[0].value).toBe(getToken(tomorrow))
  })

  it('returns tomorrow token', () => {
    vi.useFakeTimers()
    const baseDate = new Date(2026, 1, 20)
    vi.setSystemTime(baseDate)

    const tomorrow = new Date(baseDate)
    tomorrow.setDate(baseDate.getDate() + 1)

    expect(getTomorrowToken()).toBe(getToken(tomorrow))
  })
})
