import { describe, it, expect, vi, beforeAll, beforeEach } from 'vitest'
import { createApp, defineComponent, h, type App } from 'vue'
import { useBreakpoint } from '@/composables/useBreakpoint'
import { MEDIA_QUERIES } from '@/utils/breakpoints'

function setupMatchMediaForBreakpoint(
  mobile: boolean,
  tablet: boolean,
  desktop: boolean
) {
  const matchMediaMock = window.matchMedia as ReturnType<typeof vi.fn>
  matchMediaMock.mockImplementation((query: string) => {
    let matches = false
    if (query === MEDIA_QUERIES.MOBILE) matches = mobile
    else if (query === MEDIA_QUERIES.TABLET) matches = tablet
    else if (query === MEDIA_QUERIES.DESKTOP) matches = desktop

    return {
      matches,
      media: query,
      addEventListener: vi.fn(),
      removeEventListener: vi.fn(),
    } as unknown as MediaQueryList
  })
}

interface BreakpointResult {
  isMobile: { value: boolean }
  isTablet: { value: boolean }
  isDesktop: { value: boolean }
  currentBreakpoint: { value: string }
}

function testUseBreakpoint(): {
  app: App<Element>
  getIsMobile: () => boolean
  getIsTablet: () => boolean
  getIsDesktop: () => boolean
  getCurrent: () => string
} {
  let captured: BreakpointResult | null = null

  const TestComponent = defineComponent({
    setup() {
      captured = useBreakpoint() as unknown as BreakpointResult
      return () => h('div')
    },
  })

  const app = createApp(TestComponent)
  const root = document.createElement('div')
  app.mount(root)

  return {
    app,
    getIsMobile: () => captured!.isMobile.value,
    getIsTablet: () => captured!.isTablet.value,
    getIsDesktop: () => captured!.isDesktop.value,
    getCurrent: () => captured!.currentBreakpoint.value,
  }
}

describe('useBreakpoint.ts — 语义化断点组合式函数', () => {
  beforeAll(() => {
    window.matchMedia = vi.fn() as unknown as (query: string) => MediaQueryList
  })

  beforeEach(() => {
    const m = window.matchMedia as ReturnType<typeof vi.fn>
    m.mockClear()
  })

  // ===== 断点状态识别 =====

  it('桌面端：isDesktop=true，isMobile=false，isTablet=false', () => {
    setupMatchMediaForBreakpoint(false, false, true)
    const { app, getIsMobile, getIsTablet, getIsDesktop, getCurrent } =
      testUseBreakpoint()

    expect(getIsMobile()).toBe(false)
    expect(getIsTablet()).toBe(false)
    expect(getIsDesktop()).toBe(true)
    expect(getCurrent()).toBe('desktop')
    app.unmount()
  })

  it('移动端：isMobile=true，isTablet=false，isDesktop=false', () => {
    setupMatchMediaForBreakpoint(true, false, false)
    const { app, getIsMobile, getIsTablet, getIsDesktop, getCurrent } =
      testUseBreakpoint()

    expect(getIsMobile()).toBe(true)
    expect(getIsTablet()).toBe(false)
    expect(getIsDesktop()).toBe(false)
    expect(getCurrent()).toBe('mobile')
    app.unmount()
  })

  it('平板端：isTablet=true，isMobile=false，isDesktop=false', () => {
    setupMatchMediaForBreakpoint(false, true, false)
    const { app, getIsMobile, getIsTablet, getIsDesktop, getCurrent } =
      testUseBreakpoint()

    expect(getIsMobile()).toBe(false)
    expect(getIsTablet()).toBe(true)
    expect(getIsDesktop()).toBe(false)
    expect(getCurrent()).toBe('tablet')
    app.unmount()
  })

  // ===== currentBreakpoint 优先级 =====

  it('同时匹配多个时，优先级 mobile > tablet > desktop', () => {
    setupMatchMediaForBreakpoint(true, true, true)
    const { app, getCurrent } = testUseBreakpoint()

    expect(getCurrent()).toBe('mobile')
    app.unmount()
  })

  it('mobile + tablet 同时匹配，优先 mobile', () => {
    setupMatchMediaForBreakpoint(true, true, false)
    const { app, getIsMobile, getIsTablet, getCurrent } = testUseBreakpoint()

    expect(getIsMobile()).toBe(true)
    expect(getIsTablet()).toBe(true)
    expect(getCurrent()).toBe('mobile')
    app.unmount()
  })

  it('tablet + desktop 同时匹配，优先 tablet', () => {
    setupMatchMediaForBreakpoint(false, true, true)
    const { app, getCurrent } = testUseBreakpoint()

    expect(getCurrent()).toBe('tablet')
    app.unmount()
  })

  // ===== 边界 =====

  it('所有断点都不匹配时默认返回 desktop', () => {
    setupMatchMediaForBreakpoint(false, false, false)
    const { app, getCurrent } = testUseBreakpoint()

    expect(getCurrent()).toBe('desktop')
    app.unmount()
  })

  // ===== 类型安全 =====

  it('currentBreakpoint 在所有场景下只返回合法值', () => {
    const validNames = ['mobile', 'tablet', 'desktop']

    const scenarios: [boolean, boolean, boolean, string][] = [
      [true, false, false, 'mobile'],
      [false, true, false, 'tablet'],
      [false, false, true, 'desktop'],
      [false, false, false, 'desktop'],
      [true, true, true, 'mobile'],
    ]

    for (const [mobile, tablet, desktop, expected] of scenarios) {
      setupMatchMediaForBreakpoint(mobile, tablet, desktop)
      const { app, getCurrent } = testUseBreakpoint()

      expect(validNames).toContain(getCurrent())
      expect(getCurrent()).toBe(expected)
      app.unmount()
    }
  })

  // ===== 与 breakpoints.ts 常量集成 =====

  it('matchMedia 调用使用 MEDIA_QUERIES 常量', () => {
    setupMatchMediaForBreakpoint(true, false, false)
    const { app } = testUseBreakpoint()

    expect(window.matchMedia).toHaveBeenCalledWith(MEDIA_QUERIES.MOBILE)
    expect(window.matchMedia).toHaveBeenCalledWith(MEDIA_QUERIES.TABLET)
    expect(window.matchMedia).toHaveBeenCalledWith(MEDIA_QUERIES.DESKTOP)
    app.unmount()
  })
})
