<template>
  <div class="department-select">
    <h2>选择部门</h2>
    <div class="department-buttons">
      <el-button 
        v-for="dept in departments" 
        :key="dept.id"
        type="primary"
        size="large"
        @click="selectDepartment(dept.id)"
        class="dept-button"
      >
        {{ dept.name }}
      </el-button>
    </div>
  </div>
</template>

<script lang="ts">
import { ref, onMounted } from 'vue'
import { useRouter } from 'vue-router'
import { useDepartmentStore } from '../stores/department'

type Department = {
  id: number
  name?: string
  [key: string]: unknown
}

export default {
  name: 'DepartmentSelect',
  setup() {
    const router = useRouter()
    const departmentStore = useDepartmentStore()
    const departments = ref<Department[]>([])
    const loading = ref(false)

    const selectDepartment = async (deptId: number): Promise<void> => {
      loading.value = true
      try {
        const success = await departmentStore.selectDepartment(deptId)
        if (success) {
          router.push('/')
        }
      } finally {
        loading.value = false
      }
    }

    onMounted(async () => {
      await departmentStore.fetchDepartments()
      departments.value = departmentStore.departments as Department[]
    })

    return {
      departments,
      loading,
      selectDepartment
    }
  }
}
</script>

<style scoped>
.department-select {
  max-width: 600px;
  margin: 0 auto;
  padding: 20px;
}

.department-buttons {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(120px, 1fr));
  gap: 15px;
  margin-top: 20px;
}

.dept-button {
  width: 100%;
  height: 60px;
  font-size: 18px;
}
</style>
