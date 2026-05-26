<template>
  <div class="inpaint-canvas">
    <div v-if="!imageLoaded" class="no-image">
      <ImageUploader @uploaded="handleImageUploaded" />
    </div>

    <div v-else class="canvas-wrapper">
      <!-- 工具栏 -->
      <div class="canvas-toolbar">
        <button
          class="tool-btn"
          :class="{ active: currentTool === 'brush' }"
          @click="currentTool = 'brush'"
        >
          🖊️ 画笔
        </button>
        <button
          class="tool-btn"
          :class="{ active: currentTool === 'eraser' }"
          @click="currentTool = 'eraser'"
        >
          🧹 橡皮擦
        </button>
        <div class="tool-separator"></div>
        <label class="tool-label">画笔大小:</label>
        <input
          type="range"
          v-model.number="brushSize"
          min="5"
          max="100"
          class="size-slider"
        />
        <span class="size-value">{{ brushSize }}px</span>
        <div class="tool-separator"></div>
        <button class="tool-btn" @click="clearMask">🗑️ 清除标记</button>
      </div>

      <!-- 画布区域 -->
      <div class="canvas-container" ref="canvasContainer">
        <canvas ref="mainCanvas"></canvas>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, nextTick, onUnmounted } from 'vue'
import ImageUploader from './ImageUploader.vue'

const emit = defineEmits<{
  maskReady: [maskPath: string]
}>()

const canvasContainer = ref<HTMLDivElement | null>(null)
const mainCanvas = ref<HTMLCanvasElement | null>(null)
const imageLoaded = ref(false)
const currentTool = ref<'brush' | 'eraser'>('brush')
const brushSize = ref(20)
const originalImagePath = ref('')

let isDrawing = false
let imageElement: HTMLImageElement | null = null

function handleImageUploaded(filePath: string) {
  originalImagePath.value = filePath
  imageLoaded.value = true
  nextTick(() => {
    loadImageToCanvas(filePath)
  })
}

async function loadImageToCanvas(filePath: string) {
  const canvas = mainCanvas.value
  if (!canvas || !canvasContainer.value) return

  const ctx = canvas.getContext('2d')
  if (!ctx) return

  imageElement = new Image()

  imageElement.onload = () => {
    // 设置canvas尺寸为图片尺寸（保持宽高比）
    const maxWidth = canvasContainer.value!.clientWidth || 600
    const scale = Math.min(maxWidth / imageElement!.width, 1)
    canvas.width = imageElement!.width * scale
    canvas.height = imageElement!.height * scale

    // 绘制原图作为背景
    ctx.drawImage(imageElement!, 0, 0, canvas.width, canvas.height)

    // 添加鼠标事件
    canvas.addEventListener('mousedown', startDrawing)
    canvas.addEventListener('mousemove', draw)
    canvas.addEventListener('mouseup', stopDrawing)
    canvas.addEventListener('mouseleave', stopDrawing)
  }

  // 从后端获取图片 - 通过上传文件接口获取
  const filename = filePath.replace(/^.*[\\/]/, '')
  const imageUrl = `/api/v1/upload/file/${encodeURIComponent(filename)}`
  imageElement.src = imageUrl
}

function startDrawing(e: MouseEvent) {
  isDrawing = true
  draw(e)
}

function stopDrawing() {
  isDrawing = false
  const canvas = mainCanvas.value
  if (!canvas) return
  const ctx = canvas.getContext('2d')
  if (ctx) {
    ctx.beginPath()
  }
}

function draw(e: MouseEvent) {
  if (!isDrawing) return
  const canvas = mainCanvas.value
  if (!canvas) return

  const ctx = canvas.getContext('2d')
  if (!ctx || !imageElement) return

  const rect = canvas.getBoundingClientRect()
  const x = e.clientX - rect.left
  const y = e.clientY - rect.top

  ctx.lineWidth = brushSize.value
  ctx.lineCap = 'round'
  ctx.lineJoin = 'round'

  if (currentTool.value === 'brush') {
    ctx.strokeStyle = 'rgba(255, 255, 255, 1)'
    ctx.globalCompositeOperation = 'source-over'
  } else {
    // 橡皮擦 - 露出原图
    ctx.globalCompositeOperation = 'destination-out'
  }

  ctx.lineTo(x, y)
  ctx.stroke()
  ctx.beginPath()
  ctx.moveTo(x, y)
}

onUnmounted(() => {
  const canvas = mainCanvas.value
  if (canvas) {
    canvas.removeEventListener('mousedown', startDrawing)
    canvas.removeEventListener('mousemove', draw)
    canvas.removeEventListener('mouseup', stopDrawing)
    canvas.removeEventListener('mouseleave', stopDrawing)
  }
})

function clearMask() {
  const canvas = mainCanvas.value
  if (!canvas || !imageElement) return

  const ctx = canvas.getContext('2d')
  if (!ctx) return

  // 重绘原图
  ctx.drawImage(imageElement, 0, 0, canvas.width, canvas.height)
}

function getMaskDataUrl(): string {
  const canvas = mainCanvas.value
  if (!canvas) return ''

  const ctx = canvas.getContext('2d')
  if (!ctx) return ''

  // 只获取绘制区域（白色笔触部分）
  const imageData = ctx.getImageData(0, 0, canvas.width, canvas.height)
  const data = imageData.data

  // 创建遮罩：白色像素保留，其他为透明
  for (let i = 0; i < data.length; i += 4) {
    const r = data[i]
    const g = data[i + 1]
    const b = data[i + 2]
    if (r > 200 && g > 200 && b > 200) {
      // 保持白色
      data[i] = 255
      data[i + 1] = 255
      data[i + 2] = 255
      data[i + 3] = 255
    } else {
      // 其他设为黑色
      data[i] = 0
      data[i + 1] = 0
      data[i + 2] = 0
      data[i + 3] = 255
    }
  }
  ctx.putImageData(imageData, 0, 0)
  return canvas.toDataURL('image/png')
}

// 暴露方法给父组件
defineExpose({
  getMaskDataUrl,
  getOriginalImagePath: () => originalImagePath.value,
})
</script>

<style scoped>
.canvas-wrapper {
  border: 1px solid #DCDFE6;
  border-radius: 4px;
  overflow: hidden;
}

.canvas-toolbar {
  display: flex;
  align-items: center;
  gap: 8px;
  padding: 8px 12px;
  background: #F2F3F5;
  border-bottom: 1px solid #E4E7ED;
  flex-wrap: wrap;
}

.tool-btn {
  display: inline-flex;
  align-items: center;
  gap: 4px;
  padding: 6px 12px;
  border: 1px solid #DCDFE6;
  border-radius: 4px;
  background: #fff;
  cursor: pointer;
  font-size: 13px;
  color: #606266;
  transition: all 0.2s;
}

.tool-btn:hover {
  border-color: #409EFF;
  color: #409EFF;
}

.tool-btn.active {
  background: #409EFF;
  border-color: #409EFF;
  color: #fff;
}

.tool-separator {
  width: 1px;
  height: 24px;
  background: #DCDFE6;
}

.tool-label {
  font-size: 13px;
  color: #606266;
}

.size-slider {
  width: 100px;
  height: 4px;
  -webkit-appearance: none;
  appearance: none;
  background: #EBEEF5;
  border-radius: 2px;
  outline: none;
}

.size-slider::-webkit-slider-thumb {
  -webkit-appearance: none;
  width: 14px;
  height: 14px;
  border-radius: 50%;
  background: #409EFF;
  cursor: pointer;
  border: 2px solid #fff;
  box-shadow: 0 2px 4px rgba(0, 0, 0, 0.1);
}

.size-value {
  font-size: 12px;
  color: #909399;
  min-width: 30px;
}

.canvas-container {
  display: flex;
  justify-content: center;
  background: #f0f0f0;
  padding: 16px;
  min-height: 200px;
}

.canvas-container canvas {
  max-width: 100%;
  cursor: crosshair;
}

.no-image {
  padding: 16px;
}
</style>