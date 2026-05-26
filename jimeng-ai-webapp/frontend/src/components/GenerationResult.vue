<template>
  <div class="result-grid">
    <div
      v-for="image in images"
      :key="image.id"
      class="result-card"
      @click="previewImage(image.url || image.file_path)"
    >
      <img :src="getImageUrl(image.url || image.file_path)" :alt="'生成图片 ' + image.image_index" />
      <div class="card-footer">
        <span class="tag tag-success">已完成</span>
        <span class="image-label">#{{ image.image_index }}</span>
      </div>
    </div>
  </div>

  <!-- 大图预览对话框 -->
  <el-dialog
    v-model="previewVisible"
    :close-on-click-modal="true"
    width="auto"
    center
    class="preview-dialog"
  >
    <img :src="previewSrc" style="max-width: 80vw; max-height: 80vh;" alt="预览" />
  </el-dialog>
</template>

<script setup lang="ts">
import { ref } from 'vue'

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
  grid-template-columns: repeat(auto-fill, minmax(200px, 1fr));
  gap: 16px;
}

.result-card {
  border: 1px solid #EBEEF5;
  border-radius: 8px;
  overflow: hidden;
  transition: all 0.2s;
  cursor: pointer;
}

.result-card:hover {
  box-shadow: 0 4px 12px rgba(0, 0, 0, 0.08);
  transform: translateY(-2px);
}

.result-card img {
  width: 100%;
  height: 200px;
  object-fit: cover;
  display: block;
}

.card-footer {
  padding: 8px 12px;
  font-size: 12px;
  color: #909399;
  display: flex;
  justify-content: space-between;
  align-items: center;
  background: #fff;
}

.tag {
  display: inline-flex;
  align-items: center;
  padding: 2px 8px;
  border-radius: 4px;
  font-size: 12px;
}

.tag-success {
  background: #F0F9EB;
  color: #67C23A;
}

.preview-dialog :deep(.el-dialog__body) {
  padding: 0;
  display: flex;
  justify-content: center;
}
</style>