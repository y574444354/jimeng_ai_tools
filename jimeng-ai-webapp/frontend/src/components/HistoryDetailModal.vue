<template>
  <el-dialog
    :model-value="visible"
    @update:model-value="$emit('update:visible', $event)"
    title="生成详情"
    width="700px"
    :close-on-click-modal="true"
  >
    <div v-if="record" class="detail-content">
      <!-- 大图展示 -->
      <div class="detail-images" v-if="record.images && record.images.length > 0">
        <el-image
          v-for="img in record.images"
          :key="img.id"
          :src="getImageUrl(img.url || img.file_path)"
          :preview-src-list="getImageList(record.images)"
          fit="contain"
          class="detail-image"
        />
      </div>

      <!-- 参数信息 -->
      <div class="detail-info">
        <div class="info-row">
          <span class="info-label">任务类型</span>
          <span class="info-value">{{ getTaskTypeLabel(record.task_type) }}</span>
        </div>
        <div class="info-row">
          <span class="info-label">正向提示词</span>
          <span class="info-value">{{ record.prompt }}</span>
        </div>
        <div class="info-row" v-if="record.negative_prompt">
          <span class="info-label">负面提示词</span>
          <span class="info-value">{{ record.negative_prompt }}</span>
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
          <span class="info-value">{{ record.seed }}</span>
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
  grid-template-columns: repeat(auto-fill, minmax(200px, 1fr));
  gap: 12px;
  margin-bottom: 20px;
}

.detail-image {
  width: 100%;
  height: 200px;
  border-radius: 8px;
  overflow: hidden;
  border: 1px solid #EBEEF5;
}

.detail-info {
  border-top: 1px solid #EBEEF5;
  padding-top: 16px;
}

.info-row {
  display: flex;
  padding: 8px 0;
  border-bottom: 1px solid #F5F7FA;
}

.info-label {
  width: 120px;
  flex-shrink: 0;
  color: #909399;
  font-size: 13px;
}

.info-value {
  flex: 1;
  color: #303133;
  font-size: 13px;
  word-break: break-all;
}

.status-completed { color: #67C23A; }
.status-failed { color: #F56C6C; }
.status-processing { color: #E6A23C; }
</style>