import { describe, it, expect, vi, beforeEach, afterEach } from 'vitest'
import { mount } from '@vue/test-utils'

// Mock vue-router，使用工厂函数避免 hoisting 问题
let mockMeta: Record<string, unknown> = { requiresAuth: true }
vi.mock('vue-router', () => ({
  useRoute: () => ({
    path: '/text2img',
    meta: mockMeta,
  }),
  useRouter: () => ({
    push: vi.fn(),
  }),
}))

// 在 vi.mock 工厂内联定义 Mock 组件，避免 hoisting 引用外部变量
vi.mock('@/layouts/MainLayout.vue', () => ({
  default: {
    name: 'MainLayout',
    template: '<div class="main-layout-mock">MainLayout</div>',
  },
}))

import App from '@/App.vue'

describe('App.vue — 全屏登录页布局切换', () => {
  beforeEach(() => {
    mockMeta = { requiresAuth: true }
  })

  afterEach(() => {
    vi.clearAllMocks()
  })

  // ===== 条件渲染测试 =====

  it('当 route.meta.requiresAuth === true 时，渲染 MainLayout', () => {
    mockMeta = { requiresAuth: true }

    const wrapper = mount(App, {
      global: {
        stubs: {
          'router-view': { template: '<div class="router-view-stub" />' },
        },
      },
    })

    expect(wrapper.find('.main-layout-mock').exists()).toBe(true)
    expect(wrapper.find('.router-view-stub').exists()).toBe(false)
  })

  it('当 route.meta.requiresAuth === false 时，渲染全屏 router-view', () => {
    mockMeta = { requiresAuth: false }

    const wrapper = mount(App, {
      global: {
        stubs: {
          'router-view': { template: '<div class="router-view-stub" />' },
        },
      },
    })

    expect(wrapper.find('.router-view-stub').exists()).toBe(true)
    expect(wrapper.find('.main-layout-mock').exists()).toBe(false)
  })

  it('当 meta 未设置 requiresAuth 时，默认走 MainLayout 分支', () => {
    mockMeta = {}

    const wrapper = mount(App, {
      global: {
        stubs: {
          'router-view': { template: '<div class="router-view-stub" />' },
        },
      },
    })

    expect(wrapper.find('.main-layout-mock').exists()).toBe(true)
    expect(wrapper.find('.router-view-stub').exists()).toBe(false)
  })
})
