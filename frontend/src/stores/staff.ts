import { defineStore } from 'pinia'
import { ref } from 'vue'
import api from '../utils/api'
import { getTomorrowToken, type DayKey } from '../utils/rollingDayOptions'

type StaffStatus = 'bg-1' | 'bg-2' | 'bg-3'

type Staff = {
  id: number
  department_id?: number
  [key: string]: unknown
} & Partial<Record<DayKey, StaffStatus>>

export const useStaffStore = defineStore('staff', () => {
  const staffs = ref<Staff[]>([])
  const loading = ref(false)
  const selectedDay = ref<DayKey>(getTomorrowToken())

  const fetchStaffs = async (departmentId?: number): Promise<void> => {
    loading.value = true
    try {
      const response = await api.get<Staff[]>('/staffs', {
        params: { department_id: departmentId }
      })
      staffs.value = response.data
    } catch (error) {
      console.error('Failed to fetch staffs:', error)
    } finally {
      loading.value = false
    }
  }

  const addStaff = async (
    name: string,
    subDepartmentId: number | null
  ): Promise<boolean> => {
    try {
      await api.post('/staffs/add', {
        name,
        sub_department_id: subDepartmentId
      })
      await fetchStaffs(staffs.value[0]?.department_id)
      return true
    } catch (error) {
      console.error('Failed to add staff:', error)
      return false
    }
  }

  const removeStaff = async (name: string): Promise<boolean> => {
    try {
      await api.post('/staffs/remove', { name })
      await fetchStaffs(staffs.value[0]?.department_id)
      return true
    } catch (error) {
      console.error('Failed to remove staff:', error)
      return false
    }
  }

  const toggleStaffStatus = async (
    staffId: number,
    currentStatus: StaffStatus
  ): Promise<boolean> => {
    let nextStatus: StaffStatus
    if (currentStatus === 'bg-1') nextStatus = 'bg-2'
    else if (currentStatus === 'bg-2') nextStatus = 'bg-3'
    else nextStatus = 'bg-1'

    try {
      const dayKey = selectedDay.value
      await api.post('/overtime/toggle', {
        staff_id: staffId,
        status: nextStatus,
        day: dayKey
      })

      const staff = staffs.value.find((item) => item.id === staffId)
      if (staff) {
        staff[dayKey] = nextStatus
      }

      return true
    } catch (error) {
      console.error('Failed to toggle staff status:', error)
      return false
    }
  }

  const applyToAll = async (targetStatus: StaffStatus): Promise<boolean> => {
    const dayKey = selectedDay.value
    const promises = staffs.value.map(async (staff) => {
      await api.post('/overtime/toggle', {
        staff_id: staff.id,
        status: targetStatus,
        day: dayKey
      })
      staff[dayKey] = targetStatus
    })

    try {
      await Promise.all(promises)
      await fetchStaffs(staffs.value[0]?.department_id)
      return true
    } catch (error) {
      console.error('Failed to apply to all:', error)
      return false
    }
  }

  const getStaffCurrentStatus = (staff: Staff): StaffStatus => {
    const status = staff[selectedDay.value]
    return status ?? 'bg-1'
  }

  const getStaffClass = (staff: Staff): StaffStatus => {
    return getStaffCurrentStatus(staff)
  }

  return {
    staffs,
    loading,
    selectedDay,
    fetchStaffs,
    addStaff,
    removeStaff,
    toggleStaffStatus,
    applyToAll,
    getStaffCurrentStatus,
    getStaffClass
  }
})
