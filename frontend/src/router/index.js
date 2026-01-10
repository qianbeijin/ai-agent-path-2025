import { createRouter, createWebHistory } from 'vue-router'
import MainLayout from '@/layout/MainLayout.vue'

const routes = [
  {
    path: '/',
    name: 'chat',
    component: MainLayout,
  },
  // 以后你增加“文档管理”页面，只需在这里加一条：
  // { path: '/docs', component: () => import('../views/DocManager.vue') }
]

const router = createRouter({
  history: createWebHistory(),
  routes,
})

export default router
