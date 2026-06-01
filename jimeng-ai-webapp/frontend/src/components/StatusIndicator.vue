<template>
  <div class="status-indicator">
    <span class="status-dot" :class="{ offline: !connected }">
      <span class="pulse-ring" v-if="connected"></span>
    </span>
    <span class="status-text">{{ connected ? 'API 已连接' : 'API 未连接' }}</span>
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
  gap: 6px;
  font-size: 12px;
  color: var(--text-secondary);
  background: var(--bg-hover);
  padding: 5px 12px;
  border-radius: var(--radius-full);
}

.status-dot {
  position: relative;
  width: 7px;
  height: 7px;
  border-radius: 50%;
  background: var(--success);
  display: inline-block;
}

.status-dot.offline {
  background: var(--danger);
}

.pulse-ring {
  position: absolute;
  top: -3px;
  left: -3px;
  width: 13px;
  height: 13px;
  border-radius: 50%;
  background: rgba(16, 185, 129, 0.3);
  animation: pulse-glow 2s infinite;
}

.status-text {
  font-weight: 500;
}
</style>
