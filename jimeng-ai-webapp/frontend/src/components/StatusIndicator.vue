<template>
  <div class="status-indicator">
    <span class="status-dot" :class="{ offline: !connected }"></span>
    <span class="status-text">{{ connected ? '已连接' : '未连接' }}</span>
  </div>
</template>

<script setup lang="ts">
import { computed } from 'vue'
import { useAppStore } from '@/stores/app'

const appStore = useAppStore()
const connected = computed(() => appStore.apiConnected)
</script>

<style scoped>
.status-indicator {
  display: flex;
  align-items: center;
  gap: 8px;
  font-size: 13px;
  color: #909399;
}

.status-dot {
  width: 8px;
  height: 8px;
  border-radius: 50%;
  background: #67C23A;
  display: inline-block;
}

.status-dot.offline {
  background: #F56C6C;
}
</style>