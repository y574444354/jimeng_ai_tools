import { describe, it, expect, vi, beforeEach, afterEach } from 'vitest'
import { mount } from '@vue/test-utils'

// Mock stores used by MainLayout
vi.mock('@/stores/app', () => ({
  useAppStore: () => ({
    sidebarCollapsed: false,
    currentPageTitle: '测试页面',
    isMobile: false,
    isTablet: false,
    mobileSidebarOpen: false,
    sidebarMode: 'expanded',
    toggleSidebar: vi.fn(),
    closeMobileSidebar: vi.fn(),
    setCurrentPage: vi.fn(),
    checkApiStatus: vi.fn(),
    initResizeListener: vi.fn(),
    destroyResizeListener: vi.fn(),
  }),
}))

vi.mock('@/stores/user', () => ({
  useUserStore: () => ({
    isLoggedIn: false,
    userInfo: null,
    logout: vi.fn(),
    fetchUserInfo: vi.fn(),
  }),
}))

// Mock vue-router
vi.mock('vue-router', () => ({
  useRoute: () => ({
    path: '/text2img',
    meta: { title: '测试' },
  }),
  useRouter: () => ({
    push: vi.fn(),
  }),
}))

// Mock StatusIndicator component
vi.mock('@/components/StatusIndicator.vue', () => ({
  default: { template: '<div class="status-indicator" />' },
}))

import MainLayout from '@/layouts/MainLayout.vue'

describe('MainLayout.vue — setInterval 生命周期管理', () => {
  beforeEach(() => {
    vi.useFakeTimers()
    vi.spyOn(window, 'setInterval')
    vi.spyOn(window, 'clearInterval')
  })

  afterEach(() => {
    vi.useRealTimers()
    vi.clearAllMocks()
  })

  it('挂载时启动 setInterval 定时检查 API 状态', () => {
    const wrapper = mount(MainLayout, {
      global: {
        stubs: {
          'router-link': { template: '<a><slot /></a>' },
          'router-view': { template: '<div class="router-view" />' },
          'el-icon': { template: '<span class="el-icon" />' },
          'el-button': { template: '<button><slot /></button>' },
        },
      },
    })

    // setInterval 被调用一次，间隔 30000ms
    expect(window.setInterval).toHaveBeenCalledTimes(1)
    expect(window.setInterval).toHaveBeenCalledWith(expect.any(Function), 30000)

    wrapper.unmount()
  })

  it('卸载时清除 setInterval 定时器，防止内存泄漏', () => {
    const wrapper = mount(MainLayout, {
      global: {
        stubs: {
          'router-link': { template: '<a><slot /></a>' },
          'router-view': { template: '<div class="router-view" />' },
          'el-icon': { template: '<span class="el-icon" />' },
          'el-button': { template: '<button><slot /></button>' },
        },
      },
    })

    const timerId = (window.setInterval as ReturnType<typeof vi.fn>).mock
      .results[0].value

    wrapper.unmount()

    // clearInterval 被调用，参数与 setInterval 返回的 ID 一致
    expect(window.clearInterval).toHaveBeenCalledWith(timerId)
  })

  it('反复挂载和卸载不会累积未清理的定时器', () => {
    const wrapper1 = mount(MainLayout, {
      global: {
        stubs: {
          'router-link': { template: '<a><slot /></a>' },
          'router-view': { template: '<div class="router-view" />' },
          'el-icon': { template: '<span class="el-icon" />' },
          'el-button': { template: '<button><slot /></button>' },
        },
      },
    })
    wrapper1.unmount()

    const wrapper2 = mount(MainLayout, {
      global: {
        stubs: {
          'router-link': { template: '<a><slot /></a>' },
          'router-view': { template: '<div class="router-view" />' },
          'el-icon': { template: '<span class="el-icon" />' },
          'el-button': { template: '<button><slot /></button>' },
        },
      },
    })
    wrapper2.unmount()

    // setInterval 和 clearInterval 调用次数相等
    expect(window.setInterval).toHaveBeenCalledTimes(2)
    expect(window.clearInterval).toHaveBeenCalledTimes(2)
  })
})
