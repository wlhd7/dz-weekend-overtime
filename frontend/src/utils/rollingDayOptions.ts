export type DayKey = 'mon' | 'tue' | 'wed' | 'thu' | 'fri' | 'sat' | 'sun'

export type DayOption = {
  label: string
  value: DayKey
}

const WEEKDAY_TOKENS: DayKey[] = ['sun', 'mon', 'tue', 'wed', 'thu', 'fri', 'sat']
const WEEKDAY_LABELS = ['周日', '周一', '周二', '周三', '周四', '周五', '周六']

export const buildRollingDayOptions = (): DayOption[] => {
  const today = new Date()
  const options: DayOption[] = []

  for (let i = 1; i <= 7; i += 1) {
    const current = new Date(today)
    current.setDate(today.getDate() + i)
    const dayIndex = current.getDay()
    const month = current.getMonth() + 1
    const day = current.getDate()
    options.push({
      label: `${month}月${day}日 ${WEEKDAY_LABELS[dayIndex]}`,
      value: WEEKDAY_TOKENS[dayIndex]
    })
  }

  return options
}

export const getTomorrowToken = (): DayKey => {
  const tomorrow = new Date()
  tomorrow.setDate(tomorrow.getDate() + 1)
  return WEEKDAY_TOKENS[tomorrow.getDay()]
}
