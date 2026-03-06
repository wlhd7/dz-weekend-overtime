<template>
  <div class="home">
    <!-- Header -->
    <div class="header">
      <div class="header-left">
        <h2>{{ currentDepartment?.name }}</h2>
        <div class="header-actions">
          <el-button @click="$router.push('/select-department')">切换部门</el-button>
          <el-button type="primary" plain @click="openExportDialog">制表</el-button>
        </div>
      </div>

      <div class="day-inline">
        <label class="day-label">显示日期：</label>
        <el-select class="day-select" v-model="selectedDay" @change="onDayChange">
          <el-option
            v-for="option in dayOptions"
            :key="option.value"
            :label="option.label"
            :value="option.value"
          />
        </el-select>
      </div>
    </div>

    <div class="ops-panel">
      <!-- Staff Management Form -->
      <el-form :inline="true" class="staff-form">
        <el-form-item label="姓名：">
          <el-input v-model="newStaffName" placeholder="请输入姓名" />
        </el-form-item>

        <el-form-item v-if="subDepartments.length > 0" label="班组：">
          <el-select class="sub-dept-select" v-model="selectedSubDepartment">
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
        <el-button 
          class="confirm-btn" 
          @click="toggleConfirmation" 
          :loading="loading" 
          :class="{ 'is-confirmed': isConfirmed }"
        >
          {{ isConfirmed ? '已确认' : '确认' }}
        </el-button>
      </div>
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

    <el-dialog
      v-model="exportDialogVisible"
      title="制表"
      width="420px"
      :close-on-click-modal="!exportLoading"
      :close-on-press-escape="!exportLoading"
    >
      <div class="export-dialog-content">
        <el-checkbox-group v-model="selectedExportDays" class="weekday-checkboxes">
          <el-checkbox
            v-for="option in exportWeekdayOptions"
            :key="option.value"
            :label="option.value"
            class="weekday-checkbox"
          >
            {{ option.label }}
          </el-checkbox>
        </el-checkbox-group>

        <p v-if="!hasSelectedExportDays" class="export-validation">
          请选择至少一个日期
        </p>

        <ul v-if="exportErrors.length > 0" class="export-errors">
          <li v-for="error in exportErrors" :key="error" class="export-error-item">
            {{ error }}
          </li>
        </ul>
      </div>

      <template #footer>
        <el-button @click="closeExportDialog" :disabled="exportLoading">取消</el-button>
        <el-button
          type="primary"
          @click="confirmExport"
          :loading="exportLoading"
          :disabled="!hasSelectedExportDays"
        >
          确认
        </el-button>
      </template>
    </el-dialog>
  </div>
</template>

<script lang="ts">
import { computed, onMounted, ref } from 'vue'
import { ElMessage } from 'element-plus'

import { useDepartmentStore } from '../stores/department'
import { useStaffStore } from '../stores/staff'
import api from '../utils/api'
import {
  buildRollingDayOptions,
  type DayKey,
  type DayOption
} from '../utils/rollingDayOptions'
import {
  DAY_LABELS,
  EXPORT_WEEKDAY_OPTIONS,
  getDefaultExportWeekdays,
  resolveWeekdaysToDates
} from '../utils/exportWeekdays'

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

type Staff = {
  id: number
  name?: string
  sub_department_id?: number
  sub_department_name?: string
  [key: string]: unknown
}

export default {
  name: 'Home',
  setup() {
    const departmentStore = useDepartmentStore()
    const staffStore = useStaffStore()

    const newStaffName = ref('')
    const selectedSubDepartment = ref<number | null>(null)
    const dayOptions = ref<DayOption[]>(buildRollingDayOptions())

    const exportDialogVisible = ref(false)
    const selectedExportDays = ref<DayKey[]>([])
    const exportLoading = ref(false)
    const exportErrors = ref<string[]>([])
    const exportWeekdayOptions = EXPORT_WEEKDAY_OPTIONS

    const currentDepartment = computed(() =>
      departmentStore.currentDepartment as Department | null
    )
    const subDepartments = computed(() =>
      departmentStore.subDepartments as SubDepartment[]
    )
    const staffs = computed(() => staffStore.staffs as Staff[])
    const loading = computed(() => staffStore.loading)
    const isConfirmed = computed(() => staffStore.isConfirmed)
    const selectedDay = computed<DayKey>({
      get: () => staffStore.selectedDay as DayKey,
      set: (value) => {
        staffStore.selectedDay = value
      }
    })
    const hasSelectedExportDays = computed(
      () => selectedExportDays.value.length > 0
    )

    const ensureSelectedDay = (): void => {
      if (!dayOptions.value.some((option) => option.value === selectedDay.value)) {
        selectedDay.value = dayOptions.value[0]?.value ?? 'mon'
      }
    }

    const groupedStaffs = computed(() => {
      if (subDepartments.value.length === 0) return staffs.value

      return subDepartments.value.map((sd) => ({
        subDept: sd,
        staffs: staffs.value.filter((staff) =>
          staff.sub_department_id === sd.id
        )
      }))
    })

    const getStaffsBySubDept = (subDeptId: number): Staff[] => {
      return staffs.value.filter((staff) => staff.sub_department_id === subDeptId)
    }

    const getStaffClass = (staff: Staff): string => {
      return staffStore.getStaffClass(staff)
    }

    const onDayChange = (): void => {
      // Force re-render when day changes
    }

    const addStaff = async (): Promise<void> => {
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

    const removeStaff = async (): Promise<void> => {
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

    const toggleStaffStatus = async (staff: Staff): Promise<void> => {
      const currentStatus = staffStore.getStaffCurrentStatus(staff)
      const success = await staffStore.toggleStaffStatus(staff.id, currentStatus)

      if (!success) {
        ElMessage.error('状态更新失败')
      }
    }

    const clearAll = async (): Promise<void> => {
      const success = await staffStore.applyToAll('bg-1')
      if (success) {
        ElMessage.success('已清空所有加班状态')
      }
    }

    const setAllInternal = async (): Promise<void> => {
      const success = await staffStore.applyToAll('bg-2')
      if (success) {
        ElMessage.success('已设置全部为公司内加班')
      }
    }

    const setAllEvection = async (): Promise<void> => {
      const success = await staffStore.applyToAll('bg-3')
      if (success) {
        ElMessage.success('已设置全部为出差')
      }
    }

    const confirmData = async (): Promise<void> => {
      const success = await staffStore.confirmData()
      if (success) {
        ElMessage.success('确认成功')
      } else {
        ElMessage.error('确认失败')
      }
    }

    const unconfirmData = async (): Promise<void> => {
      const success = await staffStore.unconfirmData()
      if (success) {
        ElMessage.success('已取消确认')
      } else {
        ElMessage.error('取消失败')
      }
    }

    const toggleConfirmation = async (): Promise<void> => {
      if (isConfirmed.value) {
        await unconfirmData()
      } else {
        await confirmData()
      }
    }

    const parseDownloadFilename = (
      contentDisposition?: string,
      fallbackDate?: string
    ): string => {
      if (contentDisposition) {
        const utf8Match = contentDisposition.match(/filename\*=UTF-8''([^;]+)/i)
        if (utf8Match?.[1]) {
          try {
            return decodeURIComponent(utf8Match[1])
          } catch {
            // ignore decoding errors and continue with other patterns
          }
        }

        const plainMatch = contentDisposition.match(/filename="?([^";]+)"?/i)
        if (plainMatch?.[1]) {
          return plainMatch[1]
        }
      }

      if (fallbackDate) {
        return `${fallbackDate}_上班人员统计表.pdf`
      }
      return 'overtime-table.pdf'
    }

    const triggerDownload = (blob: Blob, filename: string): void => {
      const url = window.URL.createObjectURL(blob)
      const link = document.createElement('a')
      link.href = url
      link.download = filename
      document.body.appendChild(link)
      link.click()
      document.body.removeChild(link)
      window.URL.revokeObjectURL(url)
    }

    const openExportDialog = (): void => {
      selectedExportDays.value = getDefaultExportWeekdays(new Date())
      exportErrors.value = []
      exportDialogVisible.value = true
    }

    const closeExportDialog = (): void => {
      if (exportLoading.value) {
        return
      }
      exportDialogVisible.value = false
    }

    const confirmExport = async (): Promise<void> => {
      if (!hasSelectedExportDays.value) {
        ElMessage.warning('请选择至少一个日期')
        return
      }

      exportLoading.value = true
      exportErrors.value = []

      const resolvedDates = resolveWeekdaysToDates(
        selectedExportDays.value,
        new Date()
      )

      let successCount = 0
      for (const resolved of resolvedDates) {
        try {
          const response = await api.get('/exports/overtime-table', {
            params: { date: resolved.date },
            responseType: 'blob'
          })
          const filename = parseDownloadFilename(
            response.headers['content-disposition'],
            resolved.date
          )
          triggerDownload(response.data as Blob, filename)
          successCount += 1
        } catch (error) {
          exportErrors.value.push(
            `${DAY_LABELS[resolved.day]} (${resolved.date}) 导出失败`
          )
        }
      }

      exportLoading.value = false

      if (successCount > 0 && exportErrors.value.length === 0) {
        ElMessage.success(`已下载 ${successCount} 份表格`)
        exportDialogVisible.value = false
        return
      }

      if (successCount > 0 && exportErrors.value.length > 0) {
        ElMessage.warning(
          `已下载 ${successCount} 份，${exportErrors.value.length} 份失败`
        )
        return
      }

      ElMessage.error('导出失败，请稍后重试')
    }

    onMounted(async () => {
      ensureSelectedDay()
      const hasDepartment = await departmentStore.checkCurrentDepartment()
      if (!hasDepartment) {
        return
      }

      if (!currentDepartment.value) {
        return
      }

      await Promise.all([
        staffStore.fetchStaffs(currentDepartment.value.id),
        staffStore.fetchConfirmStatus()
      ])
    })

    return {
      currentDepartment,
      subDepartments,
      staffs,
      loading,
      isConfirmed,
      selectedDay,
      newStaffName,
      selectedSubDepartment,
      dayOptions,
      groupedStaffs,
      getStaffsBySubDept,
      getStaffClass,
      onDayChange,
      addStaff,
      removeStaff,
      toggleStaffStatus,
      clearAll,
      setAllInternal,
      setAllEvection,
      toggleConfirmation,
      exportDialogVisible,
      selectedExportDays,
      exportLoading,
      exportErrors,
      exportWeekdayOptions,
      hasSelectedExportDays,
      openExportDialog,
      closeExportDialog,
      confirmExport
    }
  }
}
</script>

<style scoped>
.home {
  max-width: 1000px;
  margin: 0 auto;
  padding: 20px;
}

.header {
  display: flex;
  align-items: center;
  justify-content: space-between;
  gap: 12px;
  flex-wrap: wrap;
}

.header-left {
  display: flex;
  align-items: center;
  gap: 12px;
  flex-wrap: wrap;
}

.header-left h2 {
  margin: 0;
}

.header-actions {
  display: flex;
  align-items: center;
  flex-wrap: wrap;
  gap: 8px;
}

.day-inline {
  display: flex;
  align-items: center;
  gap: 8px;
}

.day-label {
  white-space: nowrap;
}

.day-select {
  width: 11em;
}

.ops-panel {
  border: 2px solid green;
  padding: 10px;
  margin: 20px 0;
  display: flex;
  flex-direction: column;
  gap: 12px;
  justify-content: center;
}

.staff-form {
  margin: 0;
}

.staff-form :deep(.el-form-item) {
  align-items: center;
}

.sub-dept-select {
  min-width: 10em;
}

.function {
  margin: 0;
  display: flex;
  align-items: center;
  flex-wrap: wrap;
  gap: 12px;
}

.function :deep(button) {
  margin-right: 0;
}

.confirm-btn {
  border: 2px solid #409eff !important;
  background-color: #fff !important;
  color: #409eff !important;
  font-weight: bold !important;
  transition: all 0.3s ease;
}

.confirm-btn.is-confirmed {
  background-color: #409eff !important;
  color: #fff !important;
}

.confirm-btn.is-confirmed:hover {
  background-color: #f56c6c !important;
  border-color: #f56c6c !important;
  color: #fff !important;
}

.note {
  margin: 12px 0;
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

.export-dialog-content {
  display: flex;
  flex-direction: column;
  gap: 10px;
}

.weekday-checkboxes {
  display: grid;
  grid-template-columns: repeat(4, minmax(0, 1fr));
  gap: 8px;
}

.weekday-checkbox {
  margin-right: 0;
}

.export-validation {
  margin: 0;
  color: #c45656;
  font-size: 13px;
}

.export-errors {
  margin: 0;
  padding-left: 18px;
  color: #c45656;
  font-size: 13px;
}

.export-error-item {
  line-height: 1.4;
}

@media (max-width: 700px) {
  .weekday-checkboxes {
    grid-template-columns: repeat(3, minmax(0, 1fr));
  }
}
</style>
