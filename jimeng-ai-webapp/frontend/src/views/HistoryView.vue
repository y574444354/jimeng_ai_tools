<template>
  <div class="history-view">
    <div class="page-section">
      <div class="section-title">
        <div class="title-row">
          <span>生成历史</span>
          <div class="title-actions">
            <el-button size="small" @click="refreshList">🔄 刷新</el-button>
          </div>
        </div>
      </div>

      <!-- 空状态 -->
      <el-empty v-if="!loading && items.length === 0" description="暂无生成记录" />

      <!-- 列表 -->
      <div v-else class="history-list">
        <div
          v-for="item in items"
          :key="item.id"
          class="history-item"
          @click="showDetail(item)"
        >
          <div class="history-thumb">
            <img
              v-if="item.thumbnail_path"
              :src="getImageUrl(item.thumbnail_path)"
              alt="缩略图"
            />
            <div v-else class="thumb-placeholder">🎨</div>
          </div>
          <div class="history-info">
            <div class="hi-prompt">{{ item.prompt }}</div>
            <div class="hi-meta">
              <span>{{ getTaskTypeLabel(item.task_type) }}</span>
              <span class="meta-sep">|</span>
              <span>{{ item.image_size }}</span>
              <span class="meta-sep">|</span>
              <span>{{ formatTime(item.created_at) }}</span>
              <span class="meta-sep">|</span>
              <span :class="'status-tag status-' + item.status">{{ getStatusLabel(item.status) }}</span>
            </div>
          </div>
          <div class="history-actions" @click.stop>
            <el-button
              type="danger"
              size="small"
              text
              @click="confirmDelete(item)"
            >
              🗑️ 删除
            </el-button>
          </div>
        </div>
      </div>

      <!-- 分页 -->
      <div class="pagination-wrapper" v-if="total > pageSize">
        <el-pagination
          v-model:current-page="currentPage"
          :page-size="pageSize"
          :total="total"
          layout="prev, pager, next"
          @current-change="handlePageChange"
        />
      </div>
    </div>

    <!-- 详情弹框 -->
    <HistoryDetailModal
      v-model:visible="detailVisible"
      :record="detailData"
    />

    <!-- 删除确认弹框 -->
    <DeleteConfirmModal
      v-model:visible="deleteVisible"
      @confirm="handleDelete"
    />
  </div>
</template>

<script setup lang="ts">
import { ref, onMounted } from 'vue'
import { getHistoryList, deleteHistory, HistoryItem } from '@/api/history'
import HistoryDetailModal from '@/components/HistoryDetailModal.vue'
import DeleteConfirmModal from '@/components/DeleteConfirmModal.vue'

const items = ref<HistoryItem[]>([])
const total = ref(0)
const currentPage = ref(1)
const pageSize = ref(20)
const loading = ref(false)
const detailVisible = ref(false)
const deleteVisible = ref(false)
const detailData = ref<any>(null)
const deleteTarget = ref<string>('')

function getImageUrl(path: string): string {
  return path
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

async function loadList() {
  loading.value = true
  try {
    const res = await getHistoryList(currentPage.value, pageSize.value)
    items.value = res.data.list || []
    total.value = res.data.total || 0
  } catch (e: any) {
    console.error('加载历史记录失败:', e.message)
  } finally {
    loading.value = false
  }
}

function refreshList() {
  currentPage.value = 1
  loadList()
}

function handlePageChange(page: number) {
  currentPage.value = page
  loadList()
}

async function showDetail(item: HistoryItem) {
  try {
    const { getHistoryDetail } = await import('@/api/history')
    const res = await getHistoryDetail(item.id)
    detailData.value = res.data
    detailVisible.value = true
  } catch (e: any) {
    console.error('加载详情失败:', e.message)
  }
}

function confirmDelete(item: HistoryItem) {
  deleteTarget.value = item.id
  deleteVisible.value = true
}

async function handleDelete() {
  if (!deleteTarget.value) return
  try {
    await deleteHistory(deleteTarget.value)
    deleteVisible.value = false
    loadList()
  } catch (e: any) {
    console.error('删除失败:', e.message)
  }
}

onMounted(() => {
  loadList()
})
</script>

<style scoped>
.title-row {
  display: flex;
  justify-content: space-between;
  align-items: center;
}

.history-list {
  border: 1px solid #EBEEF5;
  border-radius: 8px;
  overflow: hidden;
}

.history-item {
  display: flex;
  align-items: center;
  gap: 16px;
  padding: 12px 16px;
  border-bottom: 1px solid #EBEEF5;
  transition: background 0.2s;
  cursor: pointer;
}

.history-item:last-child {
  border-bottom: none;
}

.history-item:hover {
  background: #F5F7FA;
}

.history-thumb {
  width: 60px;
  height: 60px;
  border-radius: 4px;
  background: #F2F3F5;
  overflow: hidden;
  flex-shrink: 0;
  display: flex;
  align-items: center;
  justify-content: center;
}

.history-thumb img {
  width: 100%;
  height: 100%;
  object-fit: cover;
}

.thumb-placeholder {
  font-size: 24px;
}

.history-info {
  flex: 1;
  min-width: 0;
}

.hi-prompt {
  font-size: 14px;
  color: #303133;
  overflow: hidden;
  text-overflow: ellipsis;
  white-space: nowrap;
  margin-bottom: 4px;
}

.hi-meta {
  font-size: 12px;
  color: #909399;
}

.meta-sep {
  margin: 0 6px;
}

.status-tag {
  padding: 1px 6px;
  border-radius: 3px;
  font-size: 11px;
}

.status-completed {
  color: #67C23A;
  background: #F0F9EB;
}

.status-failed {
  color: #F56C6C;
  background: #FEF0F0;
}

.status-processing {
  color: #E6A23C;
  background: #FDF6EC;
}

.pagination-wrapper {
  display: flex;
  justify-content: center;
  margin-top: 16px;
}

.history-actions {
  flex-shrink: 0;
}
</style>