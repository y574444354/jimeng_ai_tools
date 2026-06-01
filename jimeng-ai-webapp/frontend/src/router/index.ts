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
    meta: { title: '文生图' },
  },
  {
    path: '/img2img',
    name: 'Img2Img',
    component: () => import('@/views/Img2ImgView.vue'),
    meta: { title: '图生图' },
  },
  {
    path: '/inpaint',
    name: 'Inpaint',
    component: () => import('@/views/InpaintView.vue'),
    meta: { title: '局部重绘' },
  },
  {
    path: '/history',
    name: 'History',
    component: () => import('@/views/HistoryView.vue'),
    meta: { title: '历史记录' },
  },
  {
    path: '/ocr',
    name: 'Ocr',
    component: () => import('@/views/OcrView.vue'),
    meta: { title: '图片识文' },
  },
  // ===== 新增：内容创作平台路由 =====
  {
    path: '/search',
    name: 'Search',
    component: () => import('@/views/SearchView.vue'),
    meta: { title: '智能搜索' },
  },
  {
    path: '/articles',
    name: 'ArticleList',
    component: () => import('@/views/ArticleListView.vue'),
    meta: { title: '文章管理' },
  },
  {
    path: '/articles/new',
    name: 'ArticleCreate',
    component: () => import('@/views/ArticleEditorView.vue'),
    meta: { title: '写文章' },
  },
  {
    path: '/articles/:id/edit',
    name: 'ArticleEdit',
    component: () => import('@/views/ArticleEditorView.vue'),
    meta: { title: '编辑文章' },
  },
  {
    path: '/articles/:id',
    name: 'ArticleDetail',
    component: () => import('@/views/ArticleDetailView.vue'),
    meta: { title: '文章详情' },
  },
  {
    path: '/publish',
    name: 'PublishCenter',
    component: () => import('@/views/PublishCenterView.vue'),
    meta: { title: '发布中心' },
  },
]

const router = createRouter({
  history: createWebHistory(),
  routes,
})

export default router
