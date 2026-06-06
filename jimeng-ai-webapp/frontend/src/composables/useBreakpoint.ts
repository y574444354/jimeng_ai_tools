import { computed } from 'vue'
import { MEDIA_QUERIES, type BreakpointName } from '@/utils/breakpoints'
import { useMediaQuery } from './useMediaQuery'

/**
 * 响应式断点组合式函数
 * 基于 MEDIA_QUERIES 常量监听当前视口断点，返回各项断点的匹配状态
 *
 * @returns 包含 isMobile、isTablet、isDesktop 响应式 ref 和 currentBreakpoint 计算属性
 *
 * @example
 * const { isMobile, isTablet, isDesktop, currentBreakpoint } = useBreakpoint()
 * // 在模板中直接使用 isMobile 会自动响应视口变化
 */
export function useBreakpoint() {
  // 监听各断点的 media query 匹配状态
  const isMobile = useMediaQuery(MEDIA_QUERIES.MOBILE)
  const isTablet = useMediaQuery(MEDIA_QUERIES.TABLET)
  const isDesktop = useMediaQuery(MEDIA_QUERIES.DESKTOP)

  // 根据匹配状态计算出当前所属断点名称
  const currentBreakpoint = computed<BreakpointName>(() => {
    if (isMobile.value) return 'mobile'
    if (isTablet.value) return 'tablet'
    return 'desktop'
  })

  return { isMobile, isTablet, isDesktop, currentBreakpoint }
}
