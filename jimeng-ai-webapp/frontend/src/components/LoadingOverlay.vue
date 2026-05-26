<template>
  <div class="loading-overlay" v-if="visible">
    <div class="loading-content">
      <div class="loading-spinner"></div>
      <div class="loading-text">{{ text || '正在生成中...' }}</div>
      <div class="loading-status" v-if="status">{{ status }}</div>
    </div>
  </div>
</template>

<script setup lang="ts">
defineProps<{
  visible: boolean
  text?: string
  status?: string
}>()
</script>

<style scoped>
.loading-overlay {
  position: fixed;
  top: 0;
  left: 0;
  right: 0;
  bottom: 0;
  background: rgba(0, 0, 0, 0.5);
  display: flex;
  align-items: center;
  justify-content: center;
  z-index: 999;
}

.loading-content {
  background: #fff;
  border-radius: 12px;
  padding: 40px;
  text-align: center;
  min-width: 200px;
  box-shadow: 0 8px 24px rgba(0, 0, 0, 0.12);
}

.loading-spinner {
  width: 48px;
  height: 48px;
  border: 4px solid #ECF5FF;
  border-top: 4px solid #409EFF;
  border-radius: 50%;
  animation: spin 1s linear infinite;
  margin: 0 auto 16px;
}

@keyframes spin {
  to { transform: rotate(360deg); }
}

.loading-text {
  font-size: 16px;
  color: #303133;
  font-weight: 500;
}

.loading-status {
  font-size: 13px;
  color: #909399;
  margin-top: 8px;
}
</style>