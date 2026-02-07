import { createRouter, createWebHistory } from 'vue-router'
import Home from '../views/Home.vue'
import DepartmentSelect from '../views/DepartmentSelect.vue'
import Info from '../views/Info.vue'

const routes = [
  {
    path: '/',
    name: 'Home',
    component: Home
  },
  {
    path: '/select-department',
    name: 'DepartmentSelect',
    component: DepartmentSelect
  },
  {
    path: '/info',
    name: 'Info',
    component: Info
  }
]

const router = createRouter({
  history: createWebHistory(),
  routes
})

export default router
