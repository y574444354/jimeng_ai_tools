<template>
  <div class="image-uploader">
    <!-- 上传区域 -->
    <div
      v-if="!previewUrl"
      class="upload-area"
      @click="triggerUpload"
      @dragover.prevent
      @drop.prevent="handleDrop"
    >
      <div class="upload-icon">📁</div>
      <div class="upload-text">点击或拖拽图片到此处上传</div>
      <div class="upload-hint">支持 JPG/PNG 格式，单文件不超过 20MB</div>
    </div>

    <!-- 预览区域 -->
    <div v-else class="upload-preview">
      <img :src="previewUrl" alt="预览图片" />
      <button class="remove-btn" @click="removeImage">✕</button>
    </div>

    <!-- 隐藏的文件输入 -->
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

const emit = defineEmits<{
  uploaded: [filePath: string]
  removed: []
}>()

const fileInput = ref<HTMLInputElement | null>(null)
const previewUrl = ref<string | null>(null)
const currentFilePath = ref<string>('')

function triggerUpload() {
  fileInput.value?.click()
}

function handleDrop(event: DragEvent) {
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
  // 校验格式
  if (!['image/jpeg', 'image/png'].includes(file.type)) {
    alert('仅支持 JPG/PNG 格式的图片')
    return
  }

  // 校验大小
  if (file.size > 20 * 1024 * 1024) {
    alert('图片文件过大，最大允许 20MB')
    return
  }

  // 显示预览
  previewUrl.value = URL.createObjectURL(file)

  // 上传到服务器
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
  border: 2px dashed #DCDFE6;
  border-radius: 8px;
  padding: 24px;
  text-align: center;
  cursor: pointer;
  transition: all 0.2s;
  background: #F2F3F5;
}

.upload-area:hover {
  border-color: #409EFF;
  background: #ECF5FF;
}

.upload-icon {
  font-size: 36px;
  color: #C0C4CC;
  margin-bottom: 8px;
}

.upload-text {
  color: #909399;
  font-size: 13px;
}

.upload-hint {
  color: #C0C4CC;
  font-size: 12px;
  margin-top: 4px;
}

.upload-preview {
  position: relative;
  display: inline-block;
  border-radius: 4px;
  overflow: hidden;
}

.upload-preview img {
  max-width: 100%;
  max-height: 300px;
  display: block;
}

.remove-btn {
  position: absolute;
  top: 4px;
  right: 4px;
  background: rgba(0, 0, 0, 0.5);
  color: #fff;
  border: none;
  border-radius: 50%;
  width: 24px;
  height: 24px;
  cursor: pointer;
  font-size: 14px;
  display: flex;
  align-items: center;
  justify-content: center;
}
</style>