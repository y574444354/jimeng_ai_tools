import { describe, it, expect, vi, beforeEach, afterEach } from 'vitest'
import { createPinia, setActivePinia } from 'pinia'

// 在 store 导入前 mock request
vi.mock('@/api/request', () => ({
  default: {
    get: vi.fn(),
    post: vi.fn(),
    put: vi.fn(),
    delete: vi.fn(),
  },
}))

import { useAppStore } from '@/stores/app'
import { BREAKPOINTS } from '@/utils/breakpoints'

// 通过闭包变量控制 window.innerWidth
let _innerWidth = 1440

function setInnerWidth(width: number) {
  _innerWidth = width
  // 触发 resize 事件使 store 的防抖监听器感知变化
  window.dispatchEvent(new Event('resize'))
}

describe('app.ts store — 断点逻辑与响应式状态', () => {
  beforeEach(() => {
    _innerWidth = 1440
    // 通过 getter 劫持 window.innerWidth（jsdom 中该属性默认不可写）
    Object.defineProperty(window, 'innerWidth', {
      get: () => _innerWidth,
      configurable: true,
    })
    setActivePinia(createPinia())
  })

  afterEach(() => {
    vi.restoreAllMocks()
  })

  // ===== 初始化 =====

  it('windowWidth 初始化为当前 window.innerWidth', () => {
    _innerWidth = 1440
    const store = useAppStore()
    expect(store.windowWidth).toBe(1440)
  })

  it('windowWidth 反映 innerWidth 的实际值', () => {
    _innerWidth = 375
    const store = useAppStore()
    expect(store.windowWidth).toBe(375)
  })

  // ===== isMobile 计算属性 =====

  it('窗口宽度 767 时，isMobile 为 true', () => {
    _innerWidth = 767
    const store = useAppStore()
    expect(store.isMobile).toBe(true)
  })

  it('窗口宽度 320 时，isMobile 为 true', () => {
    _innerWidth = 320
    const store = useAppStore()
    expect(store.isMobile).toBe(true)
  })

  it('窗口宽度 768 时，isMobile 为 false', () => {
    _innerWidth = 768
    const store = useAppStore()
    expect(store.isMobile).toBe(false)
  })

  it('窗口宽度 1440 时，isMobile 为 false', () => {
    _innerWidth = 1440
    const store = useAppStore()
    expect(store.isMobile).toBe(false)
  })

  // ===== isTablet 计算属性 =====

  it('窗口宽度 768 时，isTablet 为 true（下边界）', () => {
    _innerWidth = 768
    const store = useAppStore()
    expect(store.isTablet).toBe(true)
  })

  it('窗口宽度 1023 时，isTablet 为 true（上边界）', () => {
    _innerWidth = 1023
    const store = useAppStore()
    expect(store.isTablet).toBe(true)
  })

  it('窗口宽度 900 时，isTablet 为 true', () => {
    _innerWidth = 900
    const store = useAppStore()
    expect(store.isTablet).toBe(true)
  })

  it('窗口宽度 767 时，isTablet 为 false', () => {
    _innerWidth = 767
    const store = useAppStore()
    expect(store.isTablet).toBe(false)
  })

  it('窗口宽度 1024 时，isTablet 为 false', () => {
    _innerWidth = 1024
    const store = useAppStore()
    expect(store.isTablet).toBe(false)
  })

  // ===== isMobile / isTablet 互斥性 =====

  it('任意宽度下 isMobile 和 isTablet 不会同时为 true', () => {
    const widths = [320, 375, 414, 767, 768, 900, 1023, 1024, 1280, 1440, 1920]

    for (const w of widths) {
      _innerWidth = w
      const store = useAppStore()
      expect(store.isMobile && store.isTablet).toBe(false)
    }
  })

  // ===== sidebarMode 计算属性 =====

  it('移动端（375px）sidebarMode 为 overlay', () => {
    _innerWidth = 375
    const store = useAppStore()
    expect(store.sidebarMode).toBe('overlay')
  })

  it('移动端 sidebarMode 不受 sidebarCollapsed 影响', () => {
    _innerWidth = 375
    const store = useAppStore()

    store.toggleSidebar() // 移动端切换的是 mobileSidebarOpen
    expect(store.sidebarMode).toBe('overlay')
  })

  it('平板端（900px）sidebarMode 始终为 collapsed', () => {
    _innerWidth = 900
    const store = useAppStore()
    expect(store.sidebarMode).toBe('collapsed')
  })

  it('桌面端（1440px）默认 sidebarMode 为 expanded', () => {
    _innerWidth = 1440
    const store = useAppStore()
    expect(store.sidebarMode).toBe('expanded')
  })

  it('桌面端 toggleSidebar 后 sidebarMode 变为 collapsed', () => {
    _innerWidth = 1440
    const store = useAppStore()

    store.toggleSidebar()
    expect(store.sidebarCollapsed).toBe(true)
    expect(store.sidebarMode).toBe('collapsed')

    store.toggleSidebar()
    expect(store.sidebarCollapsed).toBe(false)
    expect(store.sidebarMode).toBe('expanded')
  })

  // ===== toggleSidebar 方法 =====

  it('移动端 toggleSidebar 切换 mobileSidebarOpen 并控制 body 滚动', () => {
    _innerWidth = 375
    const store = useAppStore()

    store.toggleSidebar()
    expect(store.mobileSidebarOpen).toBe(true)
    expect(document.body.style.overflow).toBe('hidden')

    store.toggleSidebar()
    expect(store.mobileSidebarOpen).toBe(false)
    expect(document.body.style.overflow).toBe('')
  })

  it('桌面端 toggleSidebar 切换 sidebarCollapsed，不影响 body overflow', () => {
    _innerWidth = 1440
    const store = useAppStore()

    store.toggleSidebar()
    expect(store.sidebarCollapsed).toBe(true)
    expect(store.mobileSidebarOpen).toBe(false)

    store.toggleSidebar()
    expect(store.sidebarCollapsed).toBe(false)
  })

  it('平板端 toggleSidebar 切换 sidebarCollapsed', () => {
    _innerWidth = 900
    const store = useAppStore()

    store.toggleSidebar()
    expect(store.sidebarCollapsed).toBe(true)

    store.toggleSidebar()
    expect(store.sidebarCollapsed).toBe(false)
  })

  // ===== closeMobileSidebar 方法 =====

  it('closeMobileSidebar 关闭移动端侧边栏并恢复 body 滚动', () => {
    _innerWidth = 375
    const store = useAppStore()

    store.toggleSidebar() // 打开
    store.closeMobileSidebar()

    expect(store.mobileSidebarOpen).toBe(false)
    expect(document.body.style.overflow).toBe('')
  })

  it('连续调用 closeMobileSidebar 不会报错', () => {
    _innerWidth = 375
    const store = useAppStore()

    expect(() => {
      store.closeMobileSidebar()
      store.closeMobileSidebar()
    }).not.toThrow()
  })

  // ===== setCurrentPage 方法 =====

  it('setCurrentPage 更新 currentPageTitle', () => {
    const store = useAppStore()

    store.setCurrentPage('文章管理')
    expect(store.currentPageTitle).toBe('文章管理')

    store.setCurrentPage('OCR识别')
    expect(store.currentPageTitle).toBe('OCR识别')
  })

  // ===== checkApiStatus 方法 =====

  it('checkApiStatus: 返回 code=0 时 apiConnected 为 true', async () => {
    const request = (await import('@/api/request')).default
    ;(request.get as ReturnType<typeof vi.fn>).mockResolvedValue({ code: 0 })

    const store = useAppStore()
    await store.checkApiStatus()

    expect(store.apiConnected).toBe(true)
    expect(request.get).toHaveBeenCalledWith('/health')
  })

  it('checkApiStatus: 返回非 0 code 时 apiConnected 为 false', async () => {
    const request = (await import('@/api/request')).default
    ;(request.get as ReturnType<typeof vi.fn>).mockResolvedValue({ code: 1 })

    const store = useAppStore()
    await store.checkApiStatus()

    expect(store.apiConnected).toBe(false)
  })

  it('checkApiStatus: 请求失败时 apiConnected 为 false', async () => {
    const request = (await import('@/api/request')).default
    ;(request.get as ReturnType<typeof vi.fn>).mockRejectedValue(
      new Error('Network Error')
    )

    const store = useAppStore()
    await store.checkApiStatus()

    expect(store.apiConnected).toBe(false)
  })

  // ===== resize 监听生命周期 =====

  it('initResizeListener 注册 window resize 事件', () => {
    const addSpy = vi.spyOn(window, 'addEventListener')
    const store = useAppStore()

    store.initResizeListener()
    expect(addSpy).toHaveBeenCalledWith('resize', expect.any(Function))
  })

  it('destroyResizeListener 移除 resize 事件并清理 body overflow', () => {
    const removeSpy = vi.spyOn(window, 'removeEventListener')
    const store = useAppStore()

    store.initResizeListener()
    store.destroyResizeListener()

    expect(removeSpy).toHaveBeenCalledWith('resize', expect.any(Function))
    expect(document.body.style.overflow).toBe('')
  })

  // ===== resize 防抖处理 =====

  it('resize 事件延迟 100ms 后更新 windowWidth', () => {
    vi.useFakeTimers()
    const store = useAppStore()
    store.initResizeListener()

    _innerWidth = 375
    setInnerWidth(375)

    // 100ms 内不应更新
    expect(store.windowWidth).toBe(1440)

    vi.advanceTimersByTime(100)
    expect(store.windowWidth).toBe(375)

    vi.useRealTimers()
  })

  it('快速多次 resize 仅最后一次生效', () => {
    vi.useFakeTimers()
    const store = useAppStore()
    store.initResizeListener()

    _innerWidth = 1024
    setInnerWidth(1024)

    _innerWidth = 768
    setInnerWidth(768)

    _innerWidth = 375
    setInnerWidth(375)

    vi.advanceTimersByTime(100)
    expect(store.windowWidth).toBe(375)

    vi.useRealTimers()
  })

  // ===== BREAKPOINTS 常量集成校验 =====

  it('isMobile 判定基于 BREAKPOINTS.MOBILE（边界 <= 767）', () => {
    _innerWidth = BREAKPOINTS.MOBILE // 767
    const store = useAppStore()
    expect(store.isMobile).toBe(true)
    expect(BREAKPOINTS.MOBILE).toBe(767)
  })

  it('isMobile 判定 BREAKPOINTS.MOBILE + 1 为 false', () => {
    _innerWidth = BREAKPOINTS.MOBILE + 1 // 768
    const store = useAppStore()
    expect(store.isMobile).toBe(false)
  })

  it('isTablet 下边界 TABLET_MIN 为 true', () => {
    _innerWidth = BREAKPOINTS.TABLET_MIN // 768
    const store = useAppStore()
    expect(store.isTablet).toBe(true)
    expect(BREAKPOINTS.TABLET_MIN).toBe(768)
  })

  it('isTablet 上边界 TABLET 为 true', () => {
    _innerWidth = BREAKPOINTS.TABLET // 1023
    const store = useAppStore()
    expect(store.isTablet).toBe(true)
    expect(BREAKPOINTS.TABLET).toBe(1023)
  })

  it('isTablet 判定 TABLET + 1 为 false（桌面端）', () => {
    _innerWidth = BREAKPOINTS.TABLET + 1 // 1024
    const store = useAppStore()
    expect(store.isTablet).toBe(false)
  })
})
