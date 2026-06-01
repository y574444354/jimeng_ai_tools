<template>
  <div class="image-uploader">
    <!-- 上传区域 -->
    <div
      v-if="!previewUrl"
      class="upload-area"
      @click="triggerUpload"
      @dragover.prevent
      @dragenter.prevent
      @drop.prevent="handleDrop"
      :class="{ dragging: isDragging }"
    >
      <div class="upload-icon-wrapper">
        <el-icon class="upload-icon" :size="32"><UploadFilled /></el-icon>
      </div>
      <div class="upload-text">点击或拖拽图片到此处上传</div>
      <div class="upload-hint">支持 JPG / PNG 格式，单文件不超过 20MB</div>
    </div>

    <!-- 预览区域 -->
    <div v-else class="upload-preview">
      <img :src="previewUrl" alt="预览图片" />
      <button class="remove-btn" @click="removeImage">
        <el-icon :size="14"><Close /></el-icon>
      </button>
    </div>

    <input
      ref="fileInput"
      type="file"
      accept="image/jpeg,image/png"
      style="display: none"
      @change="handleFileChange"
    />
  </div>
</template>

<script setup lang="ts">
import { ref } from 'vue'
import { UploadFilled, Close } from '@element-plus/icons-vue'

const emit = defineEmits<{
  uploaded: [filePath: string]
  removed: []
}>()

const fileInput = ref<HTMLInputElement | null>(null)
const previewUrl = ref<string | null>(null)
const currentFilePath = ref<string>('')
const isDragging = ref(false)

function triggerUpload() {
  fileInput.value?.click()
}

function handleDrop(event: DragEvent) {
  isDragging.value = false
  const files = event.dataTransfer?.files
  if (files && files.length > 0) {
    processFile(files[0])
  }
}

function handleFileChange(event: Event) {
  const target = event.target as HTMLInputElement
  if (target.files && target.files.length > 0) {
    processFile(target.files[0])
  }
}

async function processFile(file: File) {
  if (!['image/jpeg', 'image/png'].includes(file.type)) {
    alert('仅支持 JPG/PNG 格式的图片')
    return
  }

  if (file.size > 20 * 1024 * 1024) {
    alert('图片文件过大，最大允许 20MB')
    return
  }

  previewUrl.value = URL.createObjectURL(file)

  try {
    const { uploadImage } = await import('@/api/upload')
    const res = await uploadImage(file)
    currentFilePath.value = res.data.file_path
    emit('uploaded', res.data.file_path)
  } catch (e: any) {
    alert('上传失败: ' + (e.message || '未知错误'))
    removeImage()
  }
}

function removeImage() {
  previewUrl.value = null
  currentFilePath.value = ''
  if (fileInput.value) {
    fileInput.value.value = ''
  }
  emit('removed')
}
</script>

<style scoped>
.upload-area {
  border: 2px dashed var(--border-base);
  border-radius: var(--radius-lg);
  padding: 40px 24px;
  text-align: center;
  cursor: pointer;
  transition: all var(--transition-base);
  background: var(--bg-hover);
}

.upload-area:hover,
.upload-area.dragging {
  border-color: var(--primary);
  background: var(--primary-bg);
  box-shadow: 0 0 0 4px rgba(99, 102, 241, 0.06);
}

.upload-icon-wrapper {
  width: 56px;
  height: 56px;
  border-radius: var(--radius-md);
  background: var(--primary-bg);
  display: flex;
  align-items: center;
  justify-content: center;
  margin: 0 auto 12px;
  color: var(--primary);
}

.upload-text {
  color: var(--text-regular);
  font-size: 14px;
  font-weight: 500;
}

.upload-hint {
  color: var(--text-placeholder);
  font-size: 12px;
  margin-top: 6px;
}

.upload-preview {
  position: relative;
  display: inline-block;
  border-radius: var(--radius-md);
  overflow: hidden;
  box-shadow: var(--shadow-md);
}

.upload-preview img {
  max-width: 100%;
  max-height: 360px;
  display: block;
}

.remove-btn {
  position: absolute;
  top: 8px;
  right: 8px;
  background: rgba(0, 0, 0, 0.55);
  backdrop-filter: blur(4px);
  color: #fff;
  border: none;
  border-radius: var(--radius-full);
  width: 28px;
  height: 28px;
  cursor: pointer;
  display: flex;
  align-items: center;
  justify-content: center;
  transition: all var(--transition-fast);
}

.remove-btn:hover {
  background: var(--danger);
}
</style>
