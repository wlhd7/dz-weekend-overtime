<template>
  <div class="home">
    <!-- Header -->
    <div class="header">
      <h2>{{ currentDepartment?.name }}</h2>
      <el-button @click="$router.push('/select-department')">切换部门</el-button>
    </div>

    <!-- Day Selection -->
    <div class="day">
      <label>显示日期：</label>
      <el-select v-model="selectedDay" @change="onDayChange">
        <el-option label="周六" value="sat" />
        <el-option label="周日" value="sun" />
      </el-select>
    </div>

    <!-- Staff Management Form -->
    <el-form :inline="true" class="staff-form">
      <el-form-item label="姓名：">
        <el-input v-model="newStaffName" placeholder="请输入姓名" />
      </el-form-item>
      
      <el-form-item v-if="subDepartments.length > 0" label="班组：">
        <el-select v-model="selectedSubDepartment">
          <el-option 
            v-for="sd in subDepartments" 
            :key="sd.id"
            :label="sd.name"
            :value="sd.id"
          />
        </el-select>
      </el-form-item>
      
      <el-form-item>
        <el-button type="primary" @click="addStaff" :loading="loading">添加</el-button>
        <el-button type="danger" @click="removeStaff" :loading="loading">移除</el-button>
      </el-form-item>
    </el-form>

    <!-- Batch Operations -->
    <div class="function">
      <el-button @click="clearAll" :loading="loading">无人加班</el-button>
      <el-button @click="setAllInternal" :loading="loading">全部公司内加班</el-button>
      <el-button @click="setAllEvection" :loading="loading">全部出差</el-button>
    </div>

    <div class="note">
      注：公司内加班使用<span class="bg-2 inline-text">浅黄色</span>标记，出差使用<span class="bg-3 inline-text">浅蓝色</span>标记
    </div>

    <!-- Staff List -->
    <div v-if="groupedStaffs.length > 0">
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
              @click="toggleStaffStatus(staff)"
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
            @click="toggleStaffStatus(staff)"
          >
            {{ staff.name }}<span v-if="staff.sub_department_name"> — {{ staff.sub_department_name }}</span>
          </li>
        </ul>
      </div>
    </div>
  </div>
</template>

<script>
import { ref, computed, onMounted, watch } from 'vue'
import { ElMessage } from 'element-plus'
import { useDepartmentStore } from '../stores/department'
import { useStaffStore } from '../stores/staff'

export default {
  name: 'Home',
  setup() {
    const departmentStore = useDepartmentStore()
    const staffStore = useStaffStore()
    
    const newStaffName = ref('')
    const selectedSubDepartment = ref(null)

    const currentDepartment = computed(() => departmentStore.currentDepartment)
    const subDepartments = computed(() => departmentStore.subDepartments)
    const staffs = computed(() => staffStore.staffs)
    const loading = computed(() => staffStore.loading)
    const selectedDay = computed({
      get: () => staffStore.selectedDay,
      set: (value) => staffStore.selectedDay = value
    })

    const groupedStaffs = computed(() => {
      if (subDepartments.value.length === 0) return staffs.value
      
      return subDepartments.value.map(sd => ({
        subDept: sd,
        staffs: staffs.value.filter(s => s.sub_department_id === sd.id)
      }))
    })

    const getStaffsBySubDept = (subDeptId) => {
      return staffs.value.filter(s => s.sub_department_id === subDeptId)
    }

    const getStaffClass = (staff) => {
      return staffStore.getStaffClass(staff)
    }

    const onDayChange = () => {
      // Force re-render when day changes
    }

    const addStaff = async () => {
      if (!newStaffName.value.trim()) {
        ElMessage.warning('请输入姓名')
        return
      }

      const success = await staffStore.addStaff(
        newStaffName.value.trim(),
        selectedSubDepartment.value
      )
      
      if (success) {
        ElMessage.success('添加成功')
        newStaffName.value = ''
        selectedSubDepartment.value = null
      } else {
        ElMessage.error('添加失败')
      }
    }

    const removeStaff = async () => {
      if (!newStaffName.value.trim()) {
        ElMessage.warning('请输入要移除的姓名')
        return
      }

      const success = await staffStore.removeStaff(newStaffName.value.trim())
      
      if (success) {
        ElMessage.success('移除成功')
        newStaffName.value = ''
      } else {
        ElMessage.error('移除失败')
      }
    }

    const toggleStaffStatus = async (staff) => {
      const currentStatus = staffStore.getStaffCurrentStatus(staff)
      const success = await staffStore.toggleStaffStatus(staff.id, currentStatus)
      
      if (!success) {
        ElMessage.error('状态更新失败')
      }
    }

    const clearAll = async () => {
      const success = await staffStore.applyToAll('bg-1')
      if (success) {
        ElMessage.success('已清空所有加班状态')
      }
    }

    const setAllInternal = async () => {
      const success = await staffStore.applyToAll('bg-2')
      if (success) {
        ElMessage.success('已设置全部为公司内加班')
      }
    }

    const setAllEvection = async () => {
      const success = await staffStore.applyToAll('bg-3')
      if (success) {
        ElMessage.success('已设置全部为出差')
      }
    }

    onMounted(async () => {
      // Check if department is selected
      const hasDepartment = await departmentStore.checkCurrentDepartment()
      if (!hasDepartment) {
        return
      }

      // Fetch staffs for current department
      await staffStore.fetchStaffs(currentDepartment.value.id)
    })

    return {
      currentDepartment,
      subDepartments,
      staffs,
      loading,
      selectedDay,
      newStaffName,
      selectedSubDepartment,
      groupedStaffs,
      getStaffsBySubDept,
      getStaffClass,
      onDayChange,
      addStaff,
      removeStaff,
      toggleStaffStatus,
      clearAll,
      setAllInternal,
      setAllEvection
    }
  }
}
</script>

<style scoped>
.home {
  max-width: 1200px;
  margin: 0 auto;
  padding: 20px;
}

.staff-form {
  border: 2px solid green;
  padding: 10px;
  margin: 20px 0;
}

.sub-dept-block {
  margin-bottom: 20px;
}

.sub-dept-name {
  font-weight: bold;
  margin-bottom: 10px;
}

.inline-text {
  display: inline;
  padding: 2px 4px;
  border-radius: 3px;
}
</style>
