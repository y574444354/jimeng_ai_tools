import { createRouter, createWebHistory, RouteRecordRaw } from 'vue-router'

const routes: RouteRecordRaw[] = [
  {
    path: '/',
    redirect: '/text2img',
  },
  {
    path: '/text2img',
    name: 'Text2Img',
    component: () => import('@/views/Text2ImgView.vue'),
    meta: { title: '文生图', icon: '✏️' },
  },
  {
    path: '/img2img',
    name: 'Img2Img',
    component: () => import('@/views/Img2ImgView.vue'),
    meta: { title: '图生图', icon: '🖼️' },
  },
  {
    path: '/inpaint',
    name: 'Inpaint',
    component: () => import('@/views/InpaintView.vue'),
    meta: { title: '局部重绘', icon: '🎨' },
  },
  {
    path: '/history',
    name: 'History',
    component: () => import('@/views/HistoryView.vue'),
    meta: { title: '历史记录', icon: '📋' },
  },
]

const router = createRouter({
  history: createWebHistory(),
  routes,
})

export default router