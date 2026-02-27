import { createRouter, createWebHistory } from 'vue-router'
import type { RouteRecordRaw } from 'vue-router'
import { useDepartmentStore } from '../stores/department'

const routes: RouteRecordRaw[] = [
  {
    path: '/',
    name: 'Home',
    component: () => import('../views/Home.vue')
  },
  {
    path: '/select-department',
    name: 'DepartmentSelect',
    component: () => import('../views/DepartmentSelect.vue')
  },
  {
    path: '/info',
    name: 'Info',
    component: () => import('../views/Info.vue')
  }
]

const router = createRouter({
  history: createWebHistory(),
  routes
})

router.beforeEach(async (to) => {
  const departmentStore = useDepartmentStore()

  // If already going to select-department, don't redirect again
  if (to.name === 'DepartmentSelect') {
    return true
  }

  // Check if department is already in store
  if (departmentStore.currentDepartment) {
    return true
  }

  // Check with server if we have a department selected
  const hasDepartment = await departmentStore.checkCurrentDepartment()
  if (!hasDepartment) {
    return { name: 'DepartmentSelect' }
  }

  return true
})

export default router
