<template>
  <div class="info">
    <h2>今日标注名单 ({{ today }}日)</h2>
    
    <div class="day-section">
      <h3>周六</h3>
      <div class="department-section">
        <div v-for="dept in Object.keys(satNormal)" :key="dept" class="dept-group">
          <h4>{{ dept }}: {{ satNormal[dept].join(', ') }}</h4>
        </div>
        <div v-for="dept in Object.keys(satEvection)" :key="'evec-' + dept" class="dept-group">
          <h4>{{ dept }} evection: {{ satEvection[dept].join(', ') }}</h4>
        </div>
      </div>
    </div>

    <div class="day-section">
      <h3>周日</h3>
      <div class="department-section">
        <div v-for="dept in Object.keys(sunNormal)" :key="dept" class="dept-group">
          <h4>{{ dept }}: {{ sunNormal[dept].join(', ') }}</h4>
        </div>
        <div v-for="dept in Object.keys(sunEvection)" :key="'evec-' + dept" class="dept-group">
          <h4>{{ dept }} evection: {{ sunEvection[dept].join(', ') }}</h4>
        </div>
      </div>
    </div>
  </div>
</template>

<script>
import { ref, onMounted } from 'vue'
import api from '../utils/api'

export default {
  name: 'Info',
  setup() {
    const today = ref(0)
    const satNormal = ref({})
    const satEvection = ref({})
    const sunNormal = ref({})
    const sunEvection = ref({})

    const fetchStatistics = async () => {
      try {
        const response = await api.get('/info/statistics')
        const data = response.data
        
        today.value = data.today
        satNormal.value = data.sat.normal
        satEvection.value = data.sat.evection
        sunNormal.value = data.sun.normal
        sunEvection.value = data.sun.evection
      } catch (error) {
        console.error('Failed to fetch statistics:', error)
      }
    }

    onMounted(() => {
      fetchStatistics()
    })

    return {
      today,
      satNormal,
      satEvection,
      sunNormal,
      sunEvection
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
