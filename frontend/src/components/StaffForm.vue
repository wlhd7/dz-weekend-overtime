<template>
  <el-form :inline="true" class="staff-form" @submit.prevent>
    <el-form-item label="姓名：">
      <el-input 
        v-model="staffName" 
        placeholder="请输入姓名"
        @keyup.enter="handleAdd"
        :maxlength="100"
        clearable
      />
    </el-form-item>
    
    <el-form-item v-if="subDepartments.length > 0" label="班组：">
      <el-select v-model="selectedSubDepartment" placeholder="选择班组">
        <el-option 
          v-for="sd in subDepartments" 
          :key="sd.id"
          :label="sd.name"
          :value="sd.id"
        />
      </el-select>
    </el-form-item>
    
    <el-form-item>
      <el-button 
        type="primary" 
        @click="handleAdd" 
        :loading="loading"
        :disabled="!staffName.trim()"
      >
        添加
      </el-button>
      <el-button 
        type="danger" 
        @click="handleRemove" 
        :loading="loading"
        :disabled="!staffName.trim()"
      >
        移除
      </el-button>
    </el-form-item>
  </el-form>
</template>

<script setup>
import { ref, watch } from 'vue'
import { ElMessage } from 'element-plus'

const props = defineProps({
  loading: {
    type: Boolean,
    default: false
  },
  subDepartments: {
    type: Array,
    default: () => []
  }
})

const emit = defineEmits(['add-staff', 'remove-staff'])

const staffName = ref('')
const selectedSubDepartment = ref(null)

// Reset form when sub-departments change
watch(() => props.subDepartments, () => {
  selectedSubDepartment.value = null
})

const handleAdd = () => {
  if (!staffName.value.trim()) {
    ElMessage.warning('请输入姓名')
    return
  }

  emit('add-staff', {
    name: staffName.value.trim(),
    subDepartmentId: selectedSubDepartment.value
  })
}

const handleRemove = () => {
  if (!staffName.value.trim()) {
    ElMessage.warning('请输入要移除的姓名')
    return
  }

  emit('remove-staff', staffName.value.trim())
}

// Expose methods for parent component
defineExpose({
  clearForm: () => {
    staffName.value = ''
    selectedSubDepartment.value = null
  },
  focus: () => {
    // Focus on the input field
    const input = document.querySelector('.staff-form input')
    if (input) {
      input.focus()
    }
  }
})
</script>

<style scoped>
.staff-form {
  border: 2px solid #67c23a;
  padding: 16px;
  margin: 20px 0;
  border-radius: 8px;
  background-color: #f9fff9;
}

.staff-form .el-form-item {
  margin-bottom: 0;
}

@media (max-width: 768px) {
  .staff-form {
    padding: 12px;
  }
  
  .staff-form .el-form-item {
    display: block;
    margin-bottom: 12px;
  }
  
  .staff-form .el-form-item__label {
    display: block;
    margin-bottom: 4px;
  }
}
</style>
