<template>
  <!-- 登录页面等免认证页面：全屏渲染，不带侧边栏和顶部栏 -->
  <router-view v-if="isFullscreenRoute" />
  <!-- 其他页面：带侧边栏和顶部栏的主布局 -->
  <MainLayout v-else />
</template>

<script setup lang="ts">
import { computed } from 'vue'
import { useRoute } from 'vue-router'
import MainLayout from '@/layouts/MainLayout.vue'

const route = useRoute()
// 复用路由 meta.requiresAuth 字段，免认证页面 = 全屏页面
const isFullscreenRoute = computed(() => route.meta.requiresAuth === false)
</script>
