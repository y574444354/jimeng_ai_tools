<template>
  <div class="app-container">
    <!-- 侧边栏 -->
    <div class="sidebar" :class="{ collapsed: appStore.sidebarCollapsed }">
      <div class="sidebar-logo">
        <div class="logo-icon">✨</div>
        <span class="logo-text">即梦AI</span>
      </div>
      <div class="sidebar-menu">
        <router-link
          v-for="item in menuItems"
          :key="item.path"
          :to="item.path"
          class="menu-item"
          :class="{ active: currentRoute === item.path }"
        >
          <span class="menu-icon">{{ item.icon }}</span>
          <span class="menu-label">{{ item.label }}</span>
        </router-link>
      </div>
      <div class="sidebar-toggle" @click="appStore.toggleSidebar">
        <span>{{ appStore.sidebarCollapsed ? '☰' : '✕' }}</span>
      </div>
    </div>

    <!-- 主内容区 -->
    <div class="main-content">
      <!-- 顶部栏 -->
      <header class="header">
        <div class="header-title">{{ appStore.currentPageTitle }}</div>
        <div class="header-actions">
          <StatusIndicator />
        </div>
      </header>

      <!-- 页面内容 -->
      <div class="page-content">
        <router-view />
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { computed, onMounted, watch } from 'vue'
import { useRoute } from 'vue-router'
import { useAppStore } from '@/stores/app'
import StatusIndicator from '@/components/StatusIndicator.vue'

const appStore = useAppStore()
const route = useRoute()

const currentRoute = computed(() => route.path)

const menuItems = [
  { path: '/text2img', label: '文生图', icon: '✏️' },
  { path: '/img2img', label: '图生图', icon: '🖼️' },
  { path: '/inpaint', label: '局部重绘', icon: '🎨' },
  { path: '/history', label: '历史记录', icon: '📋' },
]

watch(
  () => route.meta.title,
  (title) => {
    if (title) {
      appStore.setCurrentPage(title as string)
    }
  },
  { immediate: true }
)

onMounted(() => {
  appStore.checkApiStatus()
  // 定期检查API状态
  setInterval(() => {
    appStore.checkApiStatus()
  }, 30000)
})
</script>

<style scoped>
.app-container {
  display: flex;
  min-height: 100vh;
}

/* 侧边栏 */
.sidebar {
  width: var(--sidebar-width, 220px);
  background: var(--bg-menu, #304156);
  display: flex;
  flex-direction: column;
  position: fixed;
  top: 0;
  left: 0;
  height: 100vh;
  z-index: 100;
  transition: width 0.3s;
  overflow: hidden;
}

.sidebar.collapsed {
  width: 64px;
}

.sidebar-logo {
  height: var(--header-height, 56px);
  display: flex;
  align-items: center;
  padding: 0 16px;
  gap: 8px;
  border-bottom: 1px solid rgba(255, 255, 255, 0.08);
  white-space: nowrap;
  overflow: hidden;
}

.logo-icon {
  width: 28px;
  height: 28px;
  background: linear-gradient(135deg, #409EFF, #66B1FF);
  border-radius: 4px;
  display: flex;
  align-items: center;
  justify-content: center;
  font-size: 16px;
  color: #fff;
  flex-shrink: 0;
}

.logo-text {
  color: #fff;
  font-size: 16px;
  font-weight: 600;
  transition: opacity 0.3s;
}

.sidebar.collapsed .logo-text {
  opacity: 0;
  width: 0;
  overflow: hidden;
}

.sidebar-menu {
  flex: 1;
  padding: 8px 0;
  overflow-y: auto;
}

.menu-item {
  display: flex;
  align-items: center;
  gap: 12px;
  padding: 12px 16px;
  color: #BFCDDB;
  cursor: pointer;
  transition: all 0.2s;
  white-space: nowrap;
  overflow: hidden;
  text-decoration: none;
  border-left: 3px solid transparent;
}

.menu-item:hover {
  background: #263445;
  color: #FFFFFF;
}

.menu-item.active {
  background: #263445;
  color: #FFFFFF;
  border-left-color: #409EFF;
}

.menu-icon {
  font-size: 18px;
  width: 20px;
  text-align: center;
  flex-shrink: 0;
}

.sidebar.collapsed .menu-item {
  justify-content: center;
  padding: 12px 0;
}

.sidebar.collapsed .menu-label {
  display: none;
}

.sidebar-toggle {
  padding: 12px 16px;
  border-top: 1px solid rgba(255, 255, 255, 0.08);
  color: #BFCDDB;
  cursor: pointer;
  text-align: center;
  font-size: 18px;
  transition: color 0.2s;
}

.sidebar-toggle:hover {
  color: #fff;
}

/* 主内容 */
.main-content {
  flex: 1;
  margin-left: var(--sidebar-width, 220px);
  transition: margin-left 0.3s;
  display: flex;
  flex-direction: column;
  min-height: 100vh;
}

.sidebar.collapsed + .main-content {
  margin-left: 64px;
}

/* 顶部栏 */
.header {
  height: var(--header-height, 56px);
  background: #fff;
  border-bottom: 1px solid #E4E7ED;
  display: flex;
  align-items: center;
  justify-content: space-between;
  padding: 0 24px;
  position: sticky;
  top: 0;
  z-index: 50;
  box-shadow: 0 2px 4px rgba(0, 0, 0, 0.04), 0 2px 8px rgba(0, 0, 0, 0.06);
}

.header-title {
  font-size: 16px;
  font-weight: 600;
  color: #303133;
}

.header-actions {
  display: flex;
  align-items: center;
  gap: 16px;
}

/* 页面内容 */
.page-content {
  padding: 24px;
  flex: 1;
}
</style>