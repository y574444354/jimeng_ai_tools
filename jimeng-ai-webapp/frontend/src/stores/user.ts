import { defineStore } from 'pinia'
import { ref, computed } from 'vue'
import { login as loginApi, getCurrentUser as getCurrentUserApi, LoginParams, UserInfo } from '@/api/auth'

const TOKEN_KEY = 'xueqiao_token'

export const useUserStore = defineStore('user', () => {
  const token = ref<string>(localStorage.getItem(TOKEN_KEY) || '')
  const userInfo = ref<UserInfo | null>(null)

  const isLoggedIn = computed(() => !!token.value)

  // 从 localStorage 恢复登录态
  function initFromStorage() {
    const saved = localStorage.getItem(TOKEN_KEY)
    if (saved) {
      token.value = saved
    }
  }

  // 登录
  async function login(params: LoginParams) {
    const result = await loginApi(params)
    token.value = result.access_token
    userInfo.value = result.user
    localStorage.setItem(TOKEN_KEY, result.access_token)
  }

  // 登出
  function logout() {
    token.value = ''
    userInfo.value = null
    localStorage.removeItem(TOKEN_KEY)
  }

  // 获取当前用户信息
  async function fetchUserInfo() {
    if (!token.value) return
    try {
      userInfo.value = await getCurrentUserApi()
    } catch {
      // token 失效，清除登录态
      logout()
    }
  }

  return { token, userInfo, isLoggedIn, initFromStorage, login, logout, fetchUserInfo }
})
