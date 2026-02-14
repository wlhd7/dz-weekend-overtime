<template>
  <div class="staff-list-container">
    <!-- With Sub-departments -->
    <div v-if="subDepartments.length > 0">
      <div v-for="sd in subDepartments" :key="sd.id" class="sub-dept-block">
        <div class="sub-dept-name">{{ sd.name }}</div>
        <ul class="staff-list">
          <li 
            v-for="staff in getStaffsBySubDept(sd.id)" 
            :key="staff.id"
            :class="['staff', getStaffClass(staff)]"
            :data-staff-id="staff.id"
            @click="$emit('toggle-staff', staff)"
          >
            {{ staff.name }}
          </li>
        </ul>
      </div>
    </div>
    
    <!-- Without Sub-departments -->
    <div v-else>
      <ul class="staff-list">
        <li 
          v-for="staff in staffs" 
          :key="staff.id"
          :class="['staff', getStaffClass(staff)]"
          :data-staff-id="staff.id"
          @click="$emit('toggle-staff', staff)"
        >
          {{ staff.name }}<span v-if="staff.sub_department_name"> — {{ staff.sub_department_name }}</span>
        </li>
      </ul>
    </div>
  </div>
</template>

<script setup>
import { computed } from 'vue'

const props = defineProps({
  staffs: {
    type: Array,
    required: true
  },
  subDepartments: {
    type: Array,
    default: () => []
  },
  getStaffClass: {
    type: Function,
    required: true
  }
})

const emit = defineEmits(['toggle-staff'])

const getStaffsBySubDept = (subDeptId) => {
  return props.staffs.filter(s => s.sub_department_id === subDeptId)
}
</script>

<style scoped>
.staff-list-container {
  margin-top: 20px;
}

.sub-dept-block {
  margin-bottom: 20px;
}

.sub-dept-name {
  font-weight: bold;
  margin-bottom: 10px;
}

.staff-list {
  list-style: none;
  padding: 0;
  margin: 0;
  display: grid;
  grid-template-columns: repeat(auto-fill, minmax(120px, 1fr));
  gap: 8px;
}

.staff {
  padding: 8px 12px;
  border-radius: 4px;
  cursor: pointer;
  text-align: center;
  transition: background-color 0.2s;
  border: 1px solid #ddd;
}

.staff:hover {
  opacity: 0.8;
  transform: translateY(-1px);
}

/* Status colors */
.bg-1 {
  background-color: #f5f5f5;
}

.bg-2 {
  background-color: #fff3cd;
  border-color: #ffeaa7;
}

.bg-3 {
  background-color: #cce5ff;
  border-color: #99d6ff;
}

@media (max-width: 1200px) {
  .staff-list {
    grid-template-columns: repeat(auto-fill, minmax(100px, 1fr));
  }
}

@media (max-width: 768px) {
  .staff-list {
    grid-template-columns: repeat(auto-fill, minmax(80px, 1fr));
  }
}

@media (max-width: 480px) {
  .staff-list {
    grid-template-columns: repeat(auto-fill, minmax(60px, 1fr));
    gap: 4px;
  }
  
  .staff {
    padding: 6px 8px;
    font-size: 12px;
  }
}
</style>
