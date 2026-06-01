<template>
  <div class="app-container">
    <!-- 侧边栏 — 浅色毛玻璃风格 -->
    <aside class="sidebar" :class="{ collapsed: appStore.sidebarCollapsed }">
      <div class="sidebar-logo">
        <div class="logo-icon">
          <svg width="22" height="22" viewBox="0 0 24 24" fill="none">
            <path d="M12 2L2 7L12 12L22 7L12 2Z" stroke="white" stroke-width="2" stroke-linejoin="round"/>
            <path d="M2 17L12 22L22 17" stroke="white" stroke-width="2" stroke-linejoin="round"/>
            <path d="M2 12L12 17L22 12" stroke="white" stroke-width="2" stroke-linejoin="round"/>
          </svg>
        </div>
        <span class="logo-text gradient-text">雪桥AI</span>
      </div>

      <nav class="sidebar-menu">
        <router-link
          v-for="item in menuItems"
          :key="item.path"
          :to="item.path"
          class="menu-item"
          :class="{ active: currentRoute === item.path }"
          :title="item.label"
        >
          <el-icon class="menu-icon" :size="18">
            <component :is="item.icon" />
          </el-icon>
          <span class="menu-label">{{ item.label }}</span>
          <div v-if="currentRoute === item.path" class="active-indicator"></div>
        </router-link>
      </nav>

      <div class="sidebar-footer">
        <div class="sidebar-toggle" @click="appStore.toggleSidebar">
          <el-icon :size="16">
            <Fold v-if="!appStore.sidebarCollapsed" />
            <Expand v-else />
          </el-icon>
        </div>
      </div>
    </aside>

    <!-- 主内容区 -->
    <div class="main-content" :class="{ expanded: appStore.sidebarCollapsed }">
      <!-- 顶部栏 — 毛玻璃 -->
      <header class="header">
        <div class="header-left">
          <h1 class="header-title">{{ appStore.currentPageTitle }}</h1>
        </div>
        <div class="header-right">
          <StatusIndicator />
        </div>
      </header>

      <!-- 页面内容 -->
      <main class="page-content">
        <router-view v-slot="{ Component }">
          <transition name="page" mode="out-in">
            <component :is="Component" />
          </transition>
        </router-view>
      </main>
    </div>
  </div>
</template>

<script setup lang="ts">
import { computed, onMounted, watch } from 'vue'
import { useRoute } from 'vue-router'
import { useAppStore } from '@/stores/app'
import {
  Edit,
  Picture,
  Brush,
  Clock,
  Document,
  Fold,
  Expand,
  Search,
  Notebook,
  EditPen,
  Promotion,
} from '@element-plus/icons-vue'
import StatusIndicator from '@/components/StatusIndicator.vue'

const appStore = useAppStore()
const route = useRoute()

const currentRoute = computed(() => route.path)

const menuItems = [
  { path: '/text2img', label: '文生图', icon: Edit },
  { path: '/img2img', label: '图生图', icon: Picture },
  { path: '/inpaint', label: '局部重绘', icon: Brush },
  { path: '/history', label: '历史记录', icon: Clock },
  { path: '/ocr', label: '图片识文', icon: Document },
  { path: '/search', label: '智能搜索', icon: Search },
  { path: '/articles', label: '文章管理', icon: Notebook },
  { path: '/articles/new', label: '写文章', icon: EditPen },
  { path: '/publish', label: '发布中心', icon: Promotion },
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
  setInterval(() => {
    appStore.checkApiStatus()
  }, 30000)
})
</script>

<style scoped>
.app-container {
  display: flex;
  min-height: 100vh;
  background: var(--bg-page);
}

/* ======== 侧边栏 ======== */
.sidebar {
  width: var(--sidebar-width);
  background: var(--sidebar-bg);
  backdrop-filter: blur(24px) saturate(180%);
  -webkit-backdrop-filter: blur(24px) saturate(180%);
  border-right: 1px solid var(--sidebar-border);
  display: flex;
  flex-direction: column;
  position: fixed;
  top: 0;
  left: 0;
  height: 100vh;
  z-index: 100;
  transition: width var(--transition-slow), box-shadow var(--transition-slow);
  overflow: hidden;
}

.sidebar:not(.collapsed) {
  box-shadow: 2px 0 24px rgba(0, 0, 0, 0.04);
}

.sidebar.collapsed {
  width: var(--sidebar-collapsed);
}

/* Logo */
.sidebar-logo {
  height: var(--header-height);
  display: flex;
  align-items: center;
  padding: 0 18px;
  gap: 10px;
  white-space: nowrap;
  overflow: hidden;
  border-bottom: 1px solid var(--sidebar-border);
}

.logo-icon {
  width: 32px;
  height: 32px;
  background: var(--primary-gradient);
  border-radius: var(--radius-md);
  display: flex;
  align-items: center;
  justify-content: center;
  flex-shrink: 0;
  box-shadow: 0 2px 8px rgba(99, 102, 241, 0.3);
}

.logo-text {
  font-size: 17px;
  font-weight: 700;
  letter-spacing: 0.02em;
  transition: opacity var(--transition-base);
  white-space: nowrap;
}

.sidebar.collapsed .logo-text {
  opacity: 0;
  width: 0;
  overflow: hidden;
}

/* 菜单 */
.sidebar-menu {
  flex: 1;
  padding: 12px 10px;
  overflow-y: auto;
  display: flex;
  flex-direction: column;
  gap: 2px;
}

.menu-item {
  display: flex;
  align-items: center;
  gap: 12px;
  padding: 10px 14px;
  color: var(--sidebar-text);
  cursor: pointer;
  transition: all var(--transition-fast);
  white-space: nowrap;
  overflow: hidden;
  text-decoration: none;
  border-radius: var(--radius-md);
  position: relative;
  font-weight: 500;
  font-size: 14px;
}

.menu-item:hover {
  background: var(--primary-bg);
  color: var(--sidebar-active-text);
}

.menu-item.active {
  background: var(--sidebar-active-bg);
  color: var(--sidebar-active-text);
  font-weight: 600;
}

.active-indicator {
  position: absolute;
  left: 0;
  top: 50%;
  transform: translateY(-50%);
  width: 3px;
  height: 20px;
  background: var(--primary-gradient);
  border-radius: 0 3px 3px 0;
}

.menu-icon {
  flex-shrink: 0;
  display: flex;
  align-items: center;
  justify-content: center;
}

.menu-item.active .menu-icon {
  color: var(--primary);
}

/* 收起状态 */
.sidebar.collapsed .menu-item {
  justify-content: center;
  padding: 12px 0;
  border-radius: var(--radius-md);
}

.sidebar.collapsed .active-indicator {
  left: 0;
}

.sidebar.collapsed .menu-label {
  display: none;
}

/* 底部 */
.sidebar-footer {
  border-top: 1px solid var(--sidebar-border);
  padding: 8px;
}

.sidebar-toggle {
  display: flex;
  align-items: center;
  justify-content: center;
  height: 36px;
  border-radius: var(--radius-sm);
  color: var(--sidebar-text);
  cursor: pointer;
  transition: all var(--transition-fast);
}

.sidebar-toggle:hover {
  background: var(--primary-bg);
  color: var(--primary);
}

/* ======== 主内容区 ======== */
.main-content {
  flex: 1;
  margin-left: var(--sidebar-width);
  transition: margin-left var(--transition-slow);
  display: flex;
  flex-direction: column;
  min-height: 100vh;
}

.main-content.expanded {
  margin-left: var(--sidebar-collapsed);
}

/* ======== 顶部栏 ======== */
.header {
  height: var(--header-height);
  background: rgba(255, 255, 255, 0.8);
  backdrop-filter: blur(12px) saturate(150%);
  -webkit-backdrop-filter: blur(12px) saturate(150%);
  border-bottom: 1px solid var(--sidebar-border);
  display: flex;
  align-items: center;
  justify-content: space-between;
  padding: 0 28px;
  position: sticky;
  top: 0;
  z-index: 50;
}

.header-left {
  display: flex;
  align-items: center;
  gap: 12px;
}

.header-title {
  font-size: 18px;
  font-weight: 700;
  color: var(--text-primary);
  letter-spacing: 0.02em;
}

.header-right {
  display: flex;
  align-items: center;
  gap: 16px;
}

/* ======== 页面内容 ======== */
.page-content {
  padding: 28px;
  flex: 1;
}

/* 页面过渡动画 */
.page-enter-active {
  animation: fadeInUp 0.35s cubic-bezier(0.4, 0, 0.2, 1);
}
.page-leave-active {
  animation: fadeIn 0.2s cubic-bezier(0.4, 0, 0.2, 1) reverse;
}
</style>
