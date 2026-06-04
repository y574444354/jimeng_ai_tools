import { createRouter, createWebHistory, RouteRecordRaw } from 'vue-router'

const TOKEN_KEY = 'xueqiao_token'

const routes: RouteRecordRaw[] = [
  // 登录页面 — 不需要认证
  {
    path: '/login',
    name: 'Login',
    component: () => import('@/views/LoginView.vue'),
    meta: { title: '登录', requiresAuth: false },
  },
  {
    path: '/',
    redirect: '/text2img',
  },
  {
    path: '/text2img',
    name: 'Text2Img',
    component: () => import('@/views/Text2ImgView.vue'),
    meta: { title: '文生图', requiresAuth: true },
  },
  {
    path: '/img2img',
    name: 'Img2Img',
    component: () => import('@/views/Img2ImgView.vue'),
    meta: { title: '图生图', requiresAuth: true },
  },
  {
    path: '/inpaint',
    name: 'Inpaint',
    component: () => import('@/views/InpaintView.vue'),
    meta: { title: '局部重绘', requiresAuth: true },
  },
  {
    path: '/history',
    name: 'History',
    component: () => import('@/views/HistoryView.vue'),
    meta: { title: '历史记录', requiresAuth: true },
  },
  {
    path: '/ocr',
    name: 'Ocr',
    component: () => import('@/views/OcrView.vue'),
    meta: { title: '图片识文', requiresAuth: true },
  },
  {
    path: '/search',
    name: 'Search',
    component: () => import('@/views/SearchView.vue'),
    meta: { title: '智能搜索', requiresAuth: true },
  },
  {
    path: '/articles',
    name: 'ArticleList',
    component: () => import('@/views/ArticleListView.vue'),
    meta: { title: '文章管理', requiresAuth: true },
  },
  {
    path: '/articles/new',
    name: 'ArticleCreate',
    component: () => import('@/views/ArticleEditorView.vue'),
    meta: { title: '写文章', requiresAuth: true },
  },
  {
    path: '/articles/:id/edit',
    name: 'ArticleEdit',
    component: () => import('@/views/ArticleEditorView.vue'),
    meta: { title: '编辑文章', requiresAuth: true },
  },
  {
    path: '/articles/:id',
    name: 'ArticleDetail',
    component: () => import('@/views/ArticleDetailView.vue'),
    meta: { title: '文章详情', requiresAuth: true },
  },
  {
    path: '/publish',
    name: 'PublishCenter',
    component: () => import('@/views/PublishCenterView.vue'),
    meta: { title: '发布中心', requiresAuth: true },
  },
  {
    path: '/settings',
    name: 'Settings',
    component: () => import('@/views/SettingsView.vue'),
    meta: { title: '系统设置', requiresAuth: true },
  },
]

const router = createRouter({
  history: createWebHistory(),
  routes,
})

// 全局前置路由守卫 — 登录验证
router.beforeEach((to, _from, next) => {
  const token = localStorage.getItem(TOKEN_KEY)

  // 访问登录页但已登录 → 跳转到首页
  if (to.path === '/login' && token) {
    next('/text2img')
    return
  }

  // 需要认证但未登录 → 跳转到登录页
  if (to.meta.requiresAuth !== false && !token) {
    next('/login')
    return
  }

  next()
})

export default router
