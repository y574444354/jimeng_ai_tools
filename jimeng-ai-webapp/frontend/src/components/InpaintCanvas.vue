<template>
  <div class="inpaint-canvas">
    <div v-if="!imageLoaded" class="no-image">
      <ImageUploader @uploaded="handleImageUploaded" />
    </div>

    <div v-else class="canvas-wrapper">
      <!-- 工具栏 -->
      <div class="canvas-toolbar">
        <div class="tool-group">
          <button
            class="tool-btn"
            :class="{ active: currentTool === 'brush' }"
            @click="currentTool = 'brush'"
          >
            <el-icon :size="16"><Brush /></el-icon>
            <span>画笔</span>
          </button>
          <button
            class="tool-btn"
            :class="{ active: currentTool === 'eraser' }"
            @click="currentTool = 'eraser'"
          >
            <el-icon :size="16"><RemoveFilled /></el-icon>
            <span>橡皮擦</span>
          </button>
        </div>

        <div class="tool-separator"></div>

        <div class="tool-group">
          <label class="tool-label">大小</label>
          <input
            type="range"
            v-model.number="brushSize"
            min="5"
            max="100"
            class="size-slider"
          />
          <span class="size-badge">{{ brushSize }}px</span>
        </div>

        <div class="tool-separator"></div>

        <button class="tool-btn danger" @click="clearMask">
          <el-icon :size="16"><Delete /></el-icon>
          <span>清除标记</span>
        </button>
      </div>

      <!-- 画布 -->
      <div class="canvas-container" ref="canvasContainer">
        <canvas ref="mainCanvas"></canvas>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, nextTick, onUnmounted } from 'vue'
import { Brush, RemoveFilled, Delete } from '@element-plus/icons-vue'
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
    const maxWidth = canvasContainer.value!.clientWidth || 600
    const scale = Math.min(maxWidth / imageElement!.width, 1)
    canvas.width = imageElement!.width * scale
    canvas.height = imageElement!.height * scale

    ctx.drawImage(imageElement!, 0, 0, canvas.width, canvas.height)

    canvas.addEventListener('mousedown', startDrawing)
    canvas.addEventListener('mousemove', draw)
    canvas.addEventListener('mouseup', stopDrawing)
    canvas.addEventListener('mouseleave', stopDrawing)
  }

  const filename = filePath.replace(/^.*[\/]/, '')
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

  ctx.drawImage(imageElement, 0, 0, canvas.width, canvas.height)
}

function getMaskDataUrl(): string {
  const canvas = mainCanvas.value
  if (!canvas) return ''

  const ctx = canvas.getContext('2d')
  if (!ctx) return ''

  const imageData = ctx.getImageData(0, 0, canvas.width, canvas.height)
  const data = imageData.data

  for (let i = 0; i < data.length; i += 4) {
    const r = data[i]
    const g = data[i + 1]
    const b = data[i + 2]
    if (r > 200 && g > 200 && b > 200) {
      data[i] = 255
      data[i + 1] = 255
      data[i + 2] = 255
      data[i + 3] = 255
    } else {
      data[i] = 0
      data[i + 1] = 0
      data[i + 2] = 0
      data[i + 3] = 255
    }
  }
  ctx.putImageData(imageData, 0, 0)
  return canvas.toDataURL('image/png')
}

defineExpose({
  getMaskDataUrl,
  getOriginalImagePath: () => originalImagePath.value,
})
</script>

<style scoped>
.canvas-wrapper {
  border: 1px solid var(--border-base);
  border-radius: var(--radius-lg);
  overflow: hidden;
}

.canvas-toolbar {
  display: flex;
  align-items: center;
  gap: 8px;
  padding: 10px 16px;
  background: var(--bg-hover);
  border-bottom: 1px solid var(--border-light);
  flex-wrap: wrap;
}

.tool-group {
  display: flex;
  align-items: center;
  gap: 4px;
}

.tool-btn {
  display: inline-flex;
  align-items: center;
  gap: 5px;
  padding: 6px 12px;
  border: 1px solid var(--border-base);
  border-radius: var(--radius-sm);
  background: var(--bg-card);
  cursor: pointer;
  font-size: 13px;
  color: var(--text-regular);
  transition: all var(--transition-fast);
  font-weight: 500;
}

.tool-btn:hover {
  border-color: var(--primary);
  color: var(--primary);
  background: var(--primary-bg);
}

.tool-btn.active {
  background: var(--primary-gradient);
  border-color: transparent;
  color: #fff;
}

.tool-btn.danger:hover {
  border-color: var(--danger);
  color: var(--danger);
  background: var(--danger-bg);
}

.tool-separator {
  width: 1px;
  height: 24px;
  background: var(--border-base);
  margin: 0 4px;
}

.tool-label {
  font-size: 12px;
  color: var(--text-secondary);
  font-weight: 500;
}

.size-slider {
  width: 100px;
  height: 4px;
  -webkit-appearance: none;
  appearance: none;
  background: var(--border-light);
  border-radius: 2px;
  outline: none;
  cursor: pointer;
}

.size-slider::-webkit-slider-thumb {
  -webkit-appearance: none;
  width: 16px;
  height: 16px;
  border-radius: 50%;
  background: var(--primary);
  cursor: pointer;
  border: 2px solid #fff;
  box-shadow: var(--shadow-sm);
}

.size-badge {
  font-size: 12px;
  font-weight: 600;
  color: var(--primary);
  min-width: 32px;
  text-align: center;
}

.canvas-container {
  display: flex;
  justify-content: center;
  background: repeating-conic-gradient(#F3F4F6 0% 25%, transparent 0% 50%) 50% / 20px 20px;
  padding: 20px;
  min-height: 200px;
}

.canvas-container canvas {
  max-width: 100%;
  cursor: crosshair;
  box-shadow: var(--shadow-md);
}

.no-image {
  padding: 16px;
}

/* ======== 响应式 ======== */
@media (max-width: 767px) {
  .canvas-toolbar {
    padding: 8px 10px;
    gap: 4px;
  }
  .tool-btn {
    padding: 4px 8px;
    font-size: 12px;
    gap: 3px;
  }
  .tool-btn span {
    display: none;
  }
  .size-slider {
    width: 56px;
  }
  .canvas-container {
    padding: 10px;
    min-height: 150px;
  }
  .tool-separator {
    margin: 0 2px;
  }
  .tool-label {
    font-size: 11px;
  }
  .size-badge {
    font-size: 11px;
    min-width: 28px;
  }
}
</style>
