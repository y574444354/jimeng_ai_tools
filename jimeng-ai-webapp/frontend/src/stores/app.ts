import { defineStore } from 'pinia'
import { ref, computed } from 'vue'
import request from '@/api/request'

export const useAppStore = defineStore('app', () => {
  // 侧栏折叠状态
  const sidebarCollapsed = ref(false)

  // 当前页面标题
  const currentPageTitle = ref('文生图')

  // API连接状态
  const apiConnected = ref(false)

  // 切换侧栏折叠
  function toggleSidebar() {
    sidebarCollapsed.value = !sidebarCollapsed.value
  }

  // 设置当前页面
  function setCurrentPage(title: string) {
    currentPageTitle.value = title
  }

  // 检查API连接状态
  // 检查API连接状态
  async function checkApiStatus() {
    try {
      const res: any = await request.get('/health')
      apiConnected.value = res.code === 0
    } catch {
      apiConnected.value = false
    }
  }
  return {
    sidebarCollapsed,
    currentPageTitle,
    apiConnected,
    toggleSidebar,
    setCurrentPage,
    checkApiStatus,
  }
})