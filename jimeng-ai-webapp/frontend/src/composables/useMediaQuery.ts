import { ref, onMounted, onUnmounted } from 'vue'

/**
 * 响应式 media query 组合式函数
 * 监听 CSS media query 的匹配状态变化，返回一个响应式 ref
 *
 * @param query - CSS media query 字符串，如 "(max-width: 767px)"
 * @returns 返回一个 Ref<boolean>，表示当前是否匹配该 media query
 *
 * @example
 * const isMobile = useMediaQuery('(max-width: 767px)')
 * // 在模板或计算属性中使用 isMobile.value
 */
export function useMediaQuery(query: string) {
  // 当前是否匹配 media query
  const matches = ref(false)
  // 保存 MediaQueryList 实例，用于清理
  let mediaQueryList: MediaQueryList | null = null

  // 处理 media query 变化事件
  function handleChange(event: MediaQueryListEvent): void {
    matches.value = event.matches
  }

  // 组件挂载时注册监听
  onMounted(() => {
    // SSR 安全：无 window 对象时跳过
    if (typeof window === 'undefined') return
    // 创建 MediaQueryList 实例
    mediaQueryList = window.matchMedia(query)
    // 初始化匹配状态
    matches.value = mediaQueryList.matches
    // 注册变化监听
    mediaQueryList.addEventListener('change', handleChange)
  })

  // 组件卸载时移除监听
  onUnmounted(() => {
    if (mediaQueryList) {
      mediaQueryList.removeEventListener('change', handleChange)
      mediaQueryList = null
    }
  })

  return matches
}
