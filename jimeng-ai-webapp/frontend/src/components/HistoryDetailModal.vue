<template>
  <el-dialog
    :model-value="visible"
    @update:model-value="$emit('update:visible', $event)"
    title="生成详情"
    width="720px"
    :close-on-click-modal="true"
  >
    <div v-if="record" class="detail-content">
      <!-- 图片展示 -->
      <div class="detail-images" v-if="record.images && record.images.length > 0">
        <el-image
          v-for="img in record.images"
          :key="img.id"
          :src="getImageUrl(img.url || img.file_path)"
          :preview-src-list="getImageList(record.images)"
          fit="cover"
          class="detail-image"
        />
      </div>

      <!-- 参数信息 -->
      <div class="detail-info">
        <div class="info-grid">
          <div class="info-row">
            <span class="info-label">任务类型</span>
            <el-tag size="small" type="primary" effect="light">{{ getTaskTypeLabel(record.task_type) }}</el-tag>
          </div>
          <div class="info-row">
            <span class="info-label">图片尺寸</span>
            <span class="info-value">{{ record.image_size }}</span>
          </div>
          <div class="info-row" v-if="record.style">
            <span class="info-label">风格</span>
            <span class="info-value">{{ record.style }}</span>
          </div>
          <div class="info-row">
            <span class="info-label">CFG Scale</span>
            <span class="info-value">{{ record.cfg_scale }}</span>
          </div>
          <div class="info-row">
            <span class="info-label">Seed</span>
            <span class="info-value mono">{{ record.seed }}</span>
          </div>
          <div class="info-row">
            <span class="info-label">生成数量</span>
            <span class="info-value">{{ record.image_count }} 张</span>
          </div>
          <div class="info-row">
            <span class="info-label">创建时间</span>
            <span class="info-value">{{ formatTime(record.created_at) }}</span>
          </div>
          <div class="info-row">
            <span class="info-label">状态</span>
            <span class="info-value" :class="'status-' + record.status">{{ getStatusLabel(record.status) }}</span>
          </div>
        </div>

        <div class="info-prompt">
          <div class="prompt-label">正向提示词</div>
          <div class="prompt-content">{{ record.prompt }}</div>
        </div>
        <div class="info-prompt" v-if="record.negative_prompt">
          <div class="prompt-label negative">负面提示词</div>
          <div class="prompt-content">{{ record.negative_prompt }}</div>
        </div>
      </div>
    </div>
  </el-dialog>
</template>

<script setup lang="ts">
const props = defineProps<{
  visible: boolean
  record: any
}>()

const emit = defineEmits<{
  'update:visible': [value: boolean]
}>()

function getImageUrl(path: string): string {
  if (!path) return ''
  if (path.startsWith('http')) return path
  if (path.startsWith('/output')) return path
  return `/output/${path}`
}

function getImageList(images: any[]): string[] {
  return images.map((img: any) => getImageUrl(img.url || img.file_path))
}

function getTaskTypeLabel(type: string): string {
  const labels: Record<string, string> = {
    text2img: '文生图',
    img2img: '图生图',
    inpainting: '局部重绘',
  }
  return labels[type] || type
}

function getStatusLabel(status: string): string {
  const labels: Record<string, string> = {
    pending: '等待中',
    processing: '处理中',
    completed: '已完成',
    failed: '失败',
  }
  return labels[status] || status
}

function formatTime(timeStr: string): string {
  if (!timeStr) return ''
  const d = new Date(timeStr)
  return `${d.getFullYear()}-${String(d.getMonth() + 1).padStart(2, '0')}-${String(d.getDate()).padStart(2, '0')} ${String(d.getHours()).padStart(2, '0')}:${String(d.getMinutes()).padStart(2, '0')}`
}
</script>

<style scoped>
.detail-content {
  max-height: 70vh;
  overflow-y: auto;
}

.detail-images {
  display: grid;
  grid-template-columns: repeat(auto-fill, minmax(180px, 1fr));
  gap: 12px;
  margin-bottom: 24px;
}

.detail-image {
  width: 100%;
  aspect-ratio: 1;
  border-radius: var(--radius-md);
  overflow: hidden;
  border: 1px solid var(--border-light);
  transition: transform var(--transition-fast);
}

.detail-image:hover {
  transform: scale(1.02);
}

.detail-info {
  border-top: 1px solid var(--border-light);
  padding-top: 20px;
}

.info-grid {
  display: grid;
  grid-template-columns: repeat(2, 1fr);
  gap: 4px 24px;
  margin-bottom: 20px;
}

.info-row {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 8px 0;
  border-bottom: 1px solid var(--border-lighter);
}

.info-label {
  color: var(--text-secondary);
  font-size: 13px;
  flex-shrink: 0;
}

.info-value {
  color: var(--text-primary);
  font-size: 13px;
  font-weight: 500;
}

.info-value.mono {
  font-family: 'SF Mono', 'Fira Code', monospace;
  font-size: 12px;
}

.status-completed { color: var(--success); font-weight: 600; }
.status-failed { color: var(--danger); font-weight: 600; }
.status-processing { color: var(--warning); font-weight: 600; }

.info-prompt {
  margin-bottom: 16px;
}

.prompt-label {
  font-size: 13px;
  font-weight: 600;
  color: var(--text-secondary);
  margin-bottom: 6px;
}

.prompt-label.negative {
  color: var(--danger);
}

.prompt-content {
  font-size: 14px;
  color: var(--text-primary);
  line-height: 1.6;
  padding: 10px 14px;
  background: var(--bg-hover);
  border-radius: var(--radius-sm);
  word-break: break-all;
}

/* ======== 响应式 ======== */
@media (max-width: 767px) {
  :deep(.el-dialog) {
    width: 95% !important;
  }
  .detail-images {
    grid-template-columns: repeat(2, 1fr);
    gap: 8px;
  }
  .info-grid {
    grid-template-columns: 1fr;
    gap: 2px 0;
  }
  .info-row {
    padding: 6px 0;
  }
  .prompt-content {
    font-size: 13px;
    padding: 8px 10px;
  }
}
</style>
