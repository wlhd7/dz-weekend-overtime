import { defineStore } from 'pinia'
import { ref } from 'vue'
import api from '../utils/api'

type Department = {
  id: number
  name?: string
  [key: string]: unknown
}

type SubDepartment = {
  id: number
  name?: string
  [key: string]: unknown
}

export const useDepartmentStore = defineStore('department', () => {
  const departments = ref<Department[]>([])
  const currentDepartment = ref<Department | null>(null)
  const subDepartments = ref<SubDepartment[]>([])

  const fetchDepartments = async (): Promise<void> => {
    try {
      const response = await api.get<Department[]>('/departments')
      departments.value = response.data
    } catch (error) {
      console.error('Failed to fetch departments:', error)
    }
  }

  const selectDepartment = async (departmentId: number): Promise<boolean> => {
    try {
      await api.post('/departments/select', { department_id: departmentId })
      currentDepartment.value = departments.value.find(
        (department) => department.id === departmentId
      ) || null
      return true
    } catch (error) {
      console.error('Failed to select department:', error)
      return false
    }
  }

  const fetchSubDepartments = async (departmentId: number): Promise<void> => {
    try {
      const response = await api.get<SubDepartment[]>('/staffs/sub-departments', {
        params: { department_id: departmentId }
      })
      subDepartments.value = response.data
    } catch (error) {
      console.error('Failed to fetch sub-departments:', error)
    }
  }

  const checkCurrentDepartment = async (): Promise<boolean> => {
    try {
      const response = await api.get<Department | null>('/departments/current')
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
