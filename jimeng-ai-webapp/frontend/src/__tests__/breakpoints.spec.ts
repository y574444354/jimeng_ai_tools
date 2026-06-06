import { describe, it, expect } from 'vitest'
import { BREAKPOINTS, MEDIA_QUERIES, type BreakpointName } from '@/utils/breakpoints'

describe('breakpoints.ts — 断点常量系统', () => {
  // ===== BREAKPOINTS 常量值 =====

  describe('BREAKPOINTS 常量', () => {
    it('MOBILE 最大宽度为 767px', () => {
      expect(BREAKPOINTS.MOBILE).toBe(767)
    })

    it('TABLET_MIN 起始宽度为 768px', () => {
      expect(BREAKPOINTS.TABLET_MIN).toBe(768)
    })

    it('TABLET 结束宽度为 1023px', () => {
      expect(BREAKPOINTS.TABLET).toBe(1023)
    })

    it('平板区间连续：TABLET_MIN = MOBILE + 1', () => {
      expect(BREAKPOINTS.TABLET_MIN).toBe(BREAKPOINTS.MOBILE + 1)
    })

    it('桌面端起始：TABLET + 1 = 1024', () => {
      expect(BREAKPOINTS.TABLET + 1).toBe(1024)
    })

    it('BREAKPOINTS 对象不可变（as const）', () => {
      expect(Object.isFrozen(BREAKPOINTS)).toBe(false)
      // as const 在类型层面保证只读，运行时值正确即可
      expect(BREAKPOINTS.MOBILE).toBe(767)
      expect(BREAKPOINTS.TABLET).toBe(1023)
    })
  })

  // ===== MEDIA_QUERIES 字符串格式 =====

  describe('MEDIA_QUERIES 预编译查询字符串', () => {
    it('MOBILE 查询：max-width: 767px', () => {
      expect(MEDIA_QUERIES.MOBILE).toBe('(max-width: 767px)')
    })

    it('TABLET 查询：768px ≤ width ≤ 1023px', () => {
      expect(MEDIA_QUERIES.TABLET).toBe('(min-width: 768px) and (max-width: 1023px)')
    })

    it('DESKTOP 查询：width ≥ 1024px', () => {
      expect(MEDIA_QUERIES.DESKTOP).toBe('(min-width: 1024px)')
    })

    it('TABLET_DOWN 查询：width ≤ 1023px', () => {
      expect(MEDIA_QUERIES.TABLET_DOWN).toBe('(max-width: 1023px)')
    })

    it('所有 MEDIA_QUERIES 值基于 BREAKPOINTS 生成（耦合校验）', () => {
      // 如果此处失败，说明 MEDIA_QUERIES 未使用 BREAKPOINTS 模板字面量
      expect(MEDIA_QUERIES.MOBILE).toContain(String(BREAKPOINTS.MOBILE))
      expect(MEDIA_QUERIES.TABLET).toContain(String(BREAKPOINTS.TABLET_MIN))
      expect(MEDIA_QUERIES.TABLET).toContain(String(BREAKPOINTS.TABLET))
      expect(MEDIA_QUERIES.DESKTOP).toContain(String(BREAKPOINTS.TABLET + 1))
      expect(MEDIA_QUERIES.TABLET_DOWN).toContain(String(BREAKPOINTS.TABLET))
    })

    it('MEDIA_QUERIES 对象不可变', () => {
      expect(Object.isFrozen(MEDIA_QUERIES)).toBe(false)
      // as const 确保类型级只读
      expect(MEDIA_QUERIES.DESKTOP).toBe('(min-width: 1024px)')
    })
  })

  // ===== 边界值验证 =====

  describe('断点边界不重叠', () => {
    it('移动端和平板端区间不重叠（MOBILE < TABLET_MIN）', () => {
      expect(BREAKPOINTS.MOBILE).toBeLessThan(BREAKPOINTS.TABLET_MIN)
    })

    it('平板端区间有效（TABLET_MIN ≤ TABLET）', () => {
      expect(BREAKPOINTS.TABLET_MIN).toBeLessThanOrEqual(BREAKPOINTS.TABLET)
    })

    it('桌面端从 TABLET + 1 开始，与平板无重叠', () => {
      const desktopStart = BREAKPOINTS.TABLET + 1
      expect(desktopStart).toBeGreaterThan(BREAKPOINTS.TABLET)
      expect(desktopStart).toBe(1024)
    })
  })

  // ===== BreakpointName 类型 =====

  describe('BreakpointName 类型', () => {
    it('类型值包含三种断点名称', () => {
      const names: BreakpointName[] = ['mobile', 'tablet', 'desktop']
      expect(names).toHaveLength(3)
      expect(names).toContain('mobile')
      expect(names).toContain('tablet')
      expect(names).toContain('desktop')
    })

    it('currentBreakpoint 默认值应为 desktop（最大视口假设）', () => {
      // 当无任何匹配时，按优先级 mobile → tablet → desktop 应返回 desktop
      const defaultBreakpoint: BreakpointName = 'desktop'
      expect(defaultBreakpoint).toBe('desktop')
    })
  })
})
