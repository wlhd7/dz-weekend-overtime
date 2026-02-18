<template>
  <div class="batch-operations">
    <div class="function">
      <el-button 
        @click="handleClearAll" 
        :loading="loading"
        size="default"
        type="info"
      >
        无人加班
      </el-button>
      <el-button 
        @click="handleSetAllInternal" 
        :loading="loading"
        size="default"
        type="warning"
      >
        全部公司内加班
      </el-button>
      <el-button 
        @click="handleSetAllEvection" 
        :loading="loading"
        size="default"
        type="primary"
      >
        全部出差
      </el-button>
    </div>
    
    <div class="note">
      注：公司内加班使用<span class="bg-2 inline-text">浅黄色</span>标记，出差使用<span class="bg-3 inline-text">浅蓝色</span>标记
    </div>
  </div>
</template>

<script setup lang="ts">
import { ElMessage } from 'element-plus'

type StaffStatus = 'bg-1' | 'bg-2' | 'bg-3'

const props = withDefaults(defineProps<{
  loading?: boolean
  staffCount?: number
}>(), {
  loading: false,
  staffCount: 0
})

const emit = defineEmits<{
  (event: 'apply-to-all', status: StaffStatus): void
}>()

const handleClearAll = async () => {
  if (props.staffCount === 0) {
    ElMessage.info('当前部门没有员工')
    return
  }
  
  emit('apply-to-all', 'bg-1')
}

const handleSetAllInternal = async () => {
  if (props.staffCount === 0) {
    ElMessage.info('当前部门没有员工')
    return
  }
  
  emit('apply-to-all', 'bg-2')
}

const handleSetAllEvection = async () => {
  if (props.staffCount === 0) {
    ElMessage.info('当前部门没有员工')
    return
  }
  
  emit('apply-to-all', 'bg-3')
}
</script>

<style scoped>
.batch-operations {
  margin: 20px 0;
}

.function {
  display: flex;
  gap: 12px;
  flex-wrap: wrap;
  margin-bottom: 16px;
}

.note {
  font-size: 14px;
  color: #666;
  line-height: 1.5;
}

.inline-text {
  display: inline;
  padding: 2px 6px;
  border-radius: 3px;
  font-weight: 500;
}

.bg-2 {
  background-color: #fff3cd;
  border: 1px solid #ffeaa7;
}

.bg-3 {
  background-color: #cce5ff;
  border: 1px solid #99d6ff;
}

@media (max-width: 768px) {
  .function {
    flex-direction: column;
    gap: 8px;
  }
  
  .function .el-button {
    width: 100%;
  }
}
</style>
