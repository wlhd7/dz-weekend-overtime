<template>
  <div class="info">
    <h2>今日标注名单 ({{ today }}日)</h2>
    
    <div v-for="option in dayOptions" :key="option.value" class="day-section">
      <h3>{{ option.label }}</h3>
      <div class="department-section">
        <div
          v-for="dept in Object.keys(dayStats[option.value]?.normal || {})"
          :key="dept"
          class="dept-group"
        >
          <h4>{{ dept }}: {{ dayStats[option.value]?.normal?.[dept]?.join(', ') }}</h4>
        </div>
        <div
          v-for="dept in Object.keys(dayStats[option.value]?.evection || {})"
          :key="'evec-' + dept"
          class="dept-group"
        >
          <h4>{{ dept }} evection: {{ dayStats[option.value]?.evection?.[dept]?.join(', ') }}</h4>
        </div>
      </div>
    </div>
  </div>
</template>

<script lang="ts">
import { ref, onMounted } from 'vue'
import api from '../utils/api'
import {
  buildRollingDayOptions,
  type DayKey,
  type DayOption
} from '../utils/rollingDayOptions'

type DepartmentStats = Record<string, string[]>

type DayStats = {
  normal: DepartmentStats
  evection: DepartmentStats
}

type StatisticsResponse = {
  today: number
  days: Record<DayKey, DayStats>
}

const buildEmptyDayStats = (): Record<DayKey, DayStats> => {
  const dayTokens: DayKey[] = ['sun', 'mon', 'tue', 'wed', 'thu', 'fri', 'sat']
  return dayTokens.reduce((acc, key) => {
    acc[key] = { normal: {}, evection: {} }
    return acc
  }, {} as Record<DayKey, DayStats>)
}

export default {
  name: 'Info',
  setup() {
    const today = ref(0)
    const dayOptions = ref<DayOption[]>(buildRollingDayOptions())
    const dayStats = ref<Record<DayKey, DayStats>>(buildEmptyDayStats())

    const fetchStatistics = async (): Promise<void> => {
      try {
        const response = await api.get<StatisticsResponse>('/info/statistics')
        const data = response.data

        today.value = data.today
        dayStats.value = { ...buildEmptyDayStats(), ...data.days }
      } catch (error) {
        console.error('Failed to fetch statistics:', error)
      }
    }

    onMounted(() => {
      fetchStatistics()
    })

    return {
      today,
      dayOptions,
      dayStats
    }
  }
}
</script>

<style scoped>
.info {
  max-width: 1000px;
  margin: 0 auto;
  padding: 20px;
}

.day-section {
  margin: 30px 0;
}

.department-section {
  margin-top: 15px;
}

.dept-group {
  margin: 10px 0;
  padding: 5px 0;
  border-bottom: 1px solid #eee;
}

h2 {
  color: #333;
  text-align: center;
}

h3 {
  color: #666;
  border-bottom: 2px solid #ddd;
  padding-bottom: 5px;
}

h4 {
  color: #555;
  margin: 5px 0;
}
</style>
