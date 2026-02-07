import { defineStore } from 'pinia'
import { ref } from 'vue'
import api from '../utils/api'

export const useDepartmentStore = defineStore('department', () => {
  const departments = ref([])
  const currentDepartment = ref(null)
  const subDepartments = ref([])

  const fetchDepartments = async () => {
    try {
      const response = await api.get('/departments')
      departments.value = response.data
    } catch (error) {
      console.error('Failed to fetch departments:', error)
    }
  }

  const selectDepartment = async (departmentId) => {
    try {
      await api.post('/departments/select', { department_id: departmentId })
      currentDepartment.value = departments.value.find(d => d.id === departmentId)
      return true
    } catch (error) {
      console.error('Failed to select department:', error)
      return false
    }
  }

  const fetchSubDepartments = async (departmentId) => {
    try {
      const response = await api.get(`/staffs/sub-departments`, {
        params: { department_id: departmentId }
      })
      subDepartments.value = response.data
    } catch (error) {
      console.error('Failed to fetch sub-departments:', error)
    }
  }

  const checkCurrentDepartment = async () => {
    try {
      // Get department from cookie via API
      const response = await api.get('/departments/current')
      if (response.data) {
        currentDepartment.value = response.data
        await fetchSubDepartments(response.data.id)
        return true
      }
    } catch (error) {
      console.log('No department selected')
    }
    return false
  }

  return {
    departments,
    currentDepartment,
    subDepartments,
    fetchDepartments,
    selectDepartment,
    fetchSubDepartments,
    checkCurrentDepartment
  }
})
