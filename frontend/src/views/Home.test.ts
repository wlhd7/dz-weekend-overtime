import { describe, it, expect, vi, beforeEach } from 'vitest'
import { mount } from '@vue/test-utils'
import { createPinia, setActivePinia } from 'pinia'
import Home from './Home.vue'
import { useDepartmentStore } from '../stores/department'
import { useStaffStore } from '../stores/staff'
import { createRouter, createWebHistory } from 'vue-router'
import ElementPlus from 'element-plus'

// Mock API
vi.mock('../utils/api')

const router = createRouter({
  history: createWebHistory(),
  routes: [{ path: '/', component: { template: 'div' } }]
})

describe('Home.vue', () => {
  beforeEach(() => {
    setActivePinia(createPinia())
    vi.clearAllMocks()
  })

  it('renders confirm button with correct style', async () => {
    const departmentStore = useDepartmentStore()
    const staffStore = useStaffStore()
    
    // Mock store data
    departmentStore.currentDepartment = { id: 1, name: '制造部' }
    staffStore.isConfirmed = false
    
    const wrapper = mount(Home, {
      global: {
        plugins: [ElementPlus, router]
      }
    })
    
    const confirmBtn = wrapper.find('.confirm-btn')
    expect(confirmBtn.exists()).toBe(true)
    expect(confirmBtn.text()).toContain('确认')
    expect(confirmBtn.classes()).not.toContain('is-disabled')
  })

  it('shows "已确认" when isConfirmed is true', async () => {
    const staffStore = useStaffStore()
    staffStore.isConfirmed = true
    
    const wrapper = mount(Home, {
      global: {
        plugins: [ElementPlus, router]
      }
    })
    
    const confirmBtn = wrapper.find('.confirm-btn')
    expect(confirmBtn.text()).toContain('已确认')
    expect(confirmBtn.classes()).toContain('is-confirmed')
    expect(confirmBtn.attributes('disabled')).toBeUndefined()
  })
})
