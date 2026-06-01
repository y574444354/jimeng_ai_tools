<template>
  <div class="result-grid">
    <div
      v-for="image in images"
      :key="image.id"
      class="result-card"
      @click="previewImage(image.url || image.file_path)"
    >
      <div class="card-image-wrapper">
        <img :src="getImageUrl(image.url || image.file_path)" :alt="'生成图片 ' + image.image_index" loading="lazy" />
        <div class="card-overlay">
          <el-icon :size="24"><ZoomIn /></el-icon>
        </div>
      </div>
      <div class="card-footer">
        <span class="tag tag-success">已完成</span>
        <span class="image-label">#{{ image.image_index }}</span>
      </div>
    </div>
  </div>

  <!-- 大图预览 -->
  <el-dialog
    v-model="previewVisible"
    :close-on-click-modal="true"
    width="auto"
    center
    class="preview-dialog"
  >
    <img :src="previewSrc" style="max-width: 80vw; max-height: 80vh; border-radius: 8px;" alt="预览" />
  </el-dialog>
</template>

<script setup lang="ts">
import { ref } from 'vue'
import { ZoomIn } from '@element-plus/icons-vue'

const props = defineProps<{
  images: Array<{
    id: string
    image_index: number
    file_path: string
    url?: string
  }>
}>()

const previewVisible = ref(false)
const previewSrc = ref('')

function getImageUrl(path: string): string {
  if (path.startsWith('http')) return path
  return `/output/${path}`
}

function previewImage(src: string) {
  previewSrc.value = getImageUrl(src)
  previewVisible.value = true
}
</script>

<style scoped>
.result-grid {
  display: grid;
  grid-template-columns: repeat(auto-fill, minmax(220px, 1fr));
  gap: 20px;
}

.result-card {
  border: 1px solid var(--border-light);
  border-radius: var(--radius-lg);
  overflow: hidden;
  transition: all var(--transition-base);
  cursor: pointer;
  background: var(--bg-card);
}

.result-card:hover {
  transform: translateY(-4px);
  box-shadow: var(--shadow-lg);
  border-color: var(--border-base);
}

.card-image-wrapper {
  position: relative;
  overflow: hidden;
  aspect-ratio: 1;
}

.card-image-wrapper img {
  width: 100%;
  height: 100%;
  object-fit: cover;
  display: block;
  transition: transform var(--transition-slow);
}

.result-card:hover .card-image-wrapper img {
  transform: scale(1.05);
}

.card-overlay {
  position: absolute;
  inset: 0;
  background: rgba(99, 102, 241, 0.15);
  display: flex;
  align-items: center;
  justify-content: center;
  opacity: 0;
  transition: opacity var(--transition-base);
  color: white;
}

.result-card:hover .card-overlay {
  opacity: 1;
}

.card-footer {
  padding: 10px 14px;
  font-size: 12px;
  color: var(--text-secondary);
  display: flex;
  justify-content: space-between;
  align-items: center;
  background: var(--bg-card);
}

.tag {
  display: inline-flex;
  align-items: center;
  padding: 2px 8px;
  border-radius: var(--radius-full);
  font-size: 11px;
  font-weight: 600;
}

.tag-success {
  background: var(--success-bg);
  color: var(--success);
}

.image-label {
  font-weight: 500;
  color: var(--text-secondary);
}

.preview-dialog :deep(.el-dialog__body) {
  padding: 0;
  display: flex;
  justify-content: center;
}
</style>
