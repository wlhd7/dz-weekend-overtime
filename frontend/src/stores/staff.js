import { defineStore } from 'pinia'
import { ref } from 'vue'
import api from '../utils/api'

export const useStaffStore = defineStore('staff', () => {
  const staffs = ref([])
  const loading = ref(false)
  const selectedDay = ref('sat')

  const fetchStaffs = async (departmentId) => {
    loading.value = true
    try {
      const response = await api.get('/staffs', {
        params: { department_id: departmentId }
      })
      staffs.value = response.data
    } catch (error) {
      console.error('Failed to fetch staffs:', error)
    } finally {
      loading.value = false
    }
  }

  const addStaff = async (name, subDepartmentId) => {
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

  const removeStaff = async (name) => {
    try {
      await api.post('/staffs/remove', { name })
      await fetchStaffs(staffs.value[0]?.department_id)
      return true
    } catch (error) {
      console.error('Failed to remove staff:', error)
      return false
    }
  }

  const toggleStaffStatus = async (staffId, currentStatus) => {
    // Determine next status: bg-1 -> bg-2 -> bg-3 -> bg-1
    let nextStatus
    if (currentStatus === 'bg-1') nextStatus = 'bg-2'
    else if (currentStatus === 'bg-2') nextStatus = 'bg-3'
    else nextStatus = 'bg-1'

    try {
      await api.post('/overtime/toggle', {
        staff_id: staffId,
        status: nextStatus,
        day: selectedDay.value
      })
      
      // Update local state optimistically
      const staff = staffs.value.find(s => s.id === staffId)
      if (staff) {
        if (selectedDay.value === 'sat') {
          staff.sat_evection = nextStatus === 'bg-3' ? true : (nextStatus === 'bg-2' ? false : null)
        } else {
          staff.sun_evection = nextStatus === 'bg-3' ? true : (nextStatus === 'bg-2' ? false : null)
        }
      }
      
      return true
    } catch (error) {
      console.error('Failed to toggle staff status:', error)
      return false
    }
  }

  const applyToAll = async (targetStatus) => {
    const promises = staffs.value.map(staff => 
      toggleStaffStatus(staff.id, getStaffCurrentStatus(staff))
    )
    
    try {
      await Promise.all(promises)
      await fetchStaffs(staffs.value[0]?.department_id)
      return true
    } catch (error) {
      console.error('Failed to apply to all:', error)
      return false
    }
  }

  const getStaffCurrentStatus = (staff) => {
    const evection = selectedDay.value === 'sat' ? staff.sat_evection : staff.sun_evection
    if (evection === true) return 'bg-3'
    if (evection === false) return 'bg-2'
    return 'bg-1'
  }

  const getStaffClass = (staff) => {
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
