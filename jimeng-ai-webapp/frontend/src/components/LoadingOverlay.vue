<template>
  <div class="loading-overlay" v-if="visible">
    <div class="loading-content">
      <div class="loading-spinner">
        <div class="spinner-ring"></div>
        <div class="spinner-icon">
          <svg width="28" height="28" viewBox="0 0 24 24" fill="none">
            <path d="M12 2L2 7L12 12L22 7L12 2Z" stroke="url(#spinnerGradient)" stroke-width="1.5" stroke-linejoin="round"/>
          </svg>
        </div>
      </div>
      <div class="loading-text gradient-text">{{ text || 'AI 正在生成中...' }}</div>
      <div class="loading-status" v-if="status">{{ status }}</div>
      <div class="loading-dots">
        <span class="dot"></span>
        <span class="dot"></span>
        <span class="dot"></span>
      </div>
    </div>
    <svg width="0" height="0">
      <defs>
        <linearGradient id="spinnerGradient" x1="0%" y1="0%" x2="100%" y2="100%">
          <stop offset="0%" stop-color="#6366F1" />
          <stop offset="100%" stop-color="#8B5CF6" />
        </linearGradient>
      </defs>
    </svg>
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
  background: rgba(15, 23, 42, 0.5);
  backdrop-filter: blur(8px);
  -webkit-backdrop-filter: blur(8px);
  display: flex;
  align-items: center;
  justify-content: center;
  z-index: 999;
  animation: fadeIn 0.2s ease;
}

.loading-content {
  background: var(--bg-content);
  border-radius: var(--radius-xl);
  padding: 44px 56px;
  text-align: center;
  min-width: 240px;
  box-shadow: var(--shadow-xl), 0 0 60px rgba(99, 102, 241, 0.1);
  animation: scaleIn 0.3s cubic-bezier(0.4, 0, 0.2, 1);
}

.loading-spinner {
  position: relative;
  width: 64px;
  height: 64px;
  margin: 0 auto 20px;
}

.spinner-ring {
  position: absolute;
  inset: 0;
  border: 3px solid var(--border-light);
  border-top: 3px solid var(--primary);
  border-radius: 50%;
  animation: spin 1s linear infinite;
}

.spinner-icon {
  position: absolute;
  inset: 0;
  display: flex;
  align-items: center;
  justify-content: center;
}

.loading-text {
  font-size: 17px;
  font-weight: 700;
  margin-bottom: 4px;
}

.loading-status {
  font-size: 13px;
  color: var(--text-secondary);
  margin-bottom: 16px;
}

.loading-dots {
  display: flex;
  justify-content: center;
  gap: 6px;
}

.dot {
  width: 6px;
  height: 6px;
  border-radius: 50%;
  background: var(--primary-light);
  animation: dotBounce 1.4s ease-in-out infinite;
}

.dot:nth-child(2) { animation-delay: 0.2s; }
.dot:nth-child(3) { animation-delay: 0.4s; }

@keyframes dotBounce {
  0%, 80%, 100% { transform: scale(0.6); opacity: 0.4; }
  40% { transform: scale(1); opacity: 1; }
}
</style>
