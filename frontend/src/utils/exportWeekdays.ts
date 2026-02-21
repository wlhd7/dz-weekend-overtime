import type { DayKey } from './rollingDayOptions'

export type ResolvedExportDate = {
  day: DayKey
  date: string
  deltaDays: number
}

export const EXPORT_WEEKDAY_OPTIONS: Array<{ label: string; value: DayKey }> = [
  { label: '周一', value: 'mon' },
  { label: '周二', value: 'tue' },
  { label: '周三', value: 'wed' },
  { label: '周四', value: 'thu' },
  { label: '周五', value: 'fri' },
  { label: '周六', value: 'sat' },
  { label: '周日', value: 'sun' }
]

const DAY_TO_JS_INDEX: Record<DayKey, number> = {
  sun: 0,
  mon: 1,
  tue: 2,
  wed: 3,
  thu: 4,
  fri: 5,
  sat: 6
}

export const DAY_LABELS: Record<DayKey, string> = {
  mon: '周一',
  tue: '周二',
  wed: '周三',
  thu: '周四',
  fri: '周五',
  sat: '周六',
  sun: '周日'
}

export const getDefaultExportWeekdays = (now: Date = new Date()): DayKey[] => {
  const today = now.getDay()
  if (today === 5) {
    return ['sat', 'sun']
  }
  if (today === 6) {
    return ['sun']
  }
  return []
}

export const resolveWeekdaysToDates = (
  selectedDays: DayKey[],
  now: Date = new Date()
): ResolvedExportDate[] => {
  const today = new Date(now)
  const todayIndex = today.getDay()

  const uniqueDays = Array.from(new Set(selectedDays))
  const resolved = uniqueDays.map((day) => {
    const targetIndex = DAY_TO_JS_INDEX[day]
    const deltaDays = (targetIndex - todayIndex + 7) % 7
    const date = new Date(today)
    date.setHours(0, 0, 0, 0)
    date.setDate(today.getDate() + deltaDays)

    return {
      day,
      date: formatDate(date),
      deltaDays
    }
  })

  resolved.sort((a, b) => a.deltaDays - b.deltaDays)
  return resolved
}

const formatDate = (input: Date): string => {
  const year = input.getFullYear()
  const month = String(input.getMonth() + 1).padStart(2, '0')
  const day = String(input.getDate()).padStart(2, '0')
  return `${year}-${month}-${day}`
}
