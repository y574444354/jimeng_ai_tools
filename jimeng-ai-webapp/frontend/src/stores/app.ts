import { defineStore } from 'pinia'
import { ref, computed, onMounted, onUnmounted } from 'vue'
import request from '@/api/request'

export const useAppStore = defineStore('app', () => {
  // 窗口宽度跟踪
  const windowWidth = ref(window.innerWidth)

  // 是否为移动端 (< 768px)
  const isMobile = computed(() => windowWidth.value < 768)

  // 是否为平板端 (768px - 1023px)
  const isTablet = computed(() => windowWidth.value >= 768 && windowWidth.value < 1024)

  // 侧栏折叠状态（桌面端用户手动切换）
  const sidebarCollapsed = ref(false)

  // 移动端侧边栏 overlay 开关
  const mobileSidebarOpen = ref(false)

  // 侧边栏实际模式
  const sidebarMode = computed(() => {
    if (isMobile.value) return 'overlay'
    if (isTablet.value) return 'collapsed'
    return sidebarCollapsed.value ? 'collapsed' : 'expanded'
  })

  // 当前页面标题
  const currentPageTitle = ref('文生图')

  // API连接状态
  const apiConnected = ref(false)

  // 窗口大小变化处理
  function handleResize() {
    windowWidth.value = window.innerWidth
  }

  // 切换桌面端侧栏折叠
  function toggleSidebar() {
    if (isMobile.value) {
      mobileSidebarOpen.value = !mobileSidebarOpen.value
      // 移动端侧边栏打开时禁止body滚动
      document.body.style.overflow = mobileSidebarOpen.value ? 'hidden' : ''
    } else {
      sidebarCollapsed.value = !sidebarCollapsed.value
    }
  }

  // 关闭移动端侧边栏
  function closeMobileSidebar() {
    mobileSidebarOpen.value = false
    document.body.style.overflow = ''
  }

  // 设置当前页面
  function setCurrentPage(title: string) {
    currentPageTitle.value = title
  }

  // 检查API连接状态
  async function checkApiStatus() {
    try {
      const res: any = await request.get('/health')
      apiConnected.value = res.code === 0
    } catch {
      apiConnected.value = false
    }
  }

  // 注册 resize 监听
  let resizeTimer: ReturnType<typeof setTimeout> | null = null
  function onResize() {
    if (resizeTimer) clearTimeout(resizeTimer)
    resizeTimer = setTimeout(handleResize, 100)
  }

  // 在 store 外部调用初始化（从 main.ts 或 MainLayout onMounted）
  function initResizeListener() {
    window.addEventListener('resize', onResize)
  }

  function destroyResizeListener() {
    window.removeEventListener('resize', onResize)
    document.body.style.overflow = ''
  }

  return {
    windowWidth,
    isMobile,
    isTablet,
    sidebarCollapsed,
    mobileSidebarOpen,
    sidebarMode,
    currentPageTitle,
    apiConnected,
    toggleSidebar,
    closeMobileSidebar,
    setCurrentPage,
    checkApiStatus,
    initResizeListener,
    destroyResizeListener,
  }
})
