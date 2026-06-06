import { createApp } from 'vue'
import { createPinia } from 'pinia'
import ElementPlus from 'element-plus'
import * as ElementPlusIconsVue from '@element-plus/icons-vue'
import 'element-plus/dist/index.css'
import App from './App.vue'
import router from './router'
import { useUserStore } from './stores/user'
import { useAppStore } from '@/stores/app'
import './styles/global.css'

const app = createApp(App)
const pinia = createPinia()

// 全局注册所有 Element Plus 图标
for (const [key, component] of Object.entries(ElementPlusIconsVue)) {
  app.component(key, component)
}

app.use(pinia)
app.use(router)
app.use(ElementPlus, { locale: undefined })

// 从 localStorage 恢复登录态
const userStore = useUserStore()
userStore.initFromStorage()

// 全局化 resize 监听器 — 在 mount 前注册，确保所有页面可获取窗口宽度
const appStore = useAppStore()
appStore.initResizeListener()

app.mount('#app')
