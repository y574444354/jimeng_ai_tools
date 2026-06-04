<template>
  <div class="history-view">
    <div class="page-section">
      <div class="section-title">
        <div class="title-row">
          <span class="title-left">
            <el-icon :size="18"><Clock /></el-icon>
            生成历史
          </span>
          <el-button size="small" @click="refreshList" class="refresh-btn">
            <el-icon :size="14"><Refresh /></el-icon>
            刷新
          </el-button>
        </div>
      </div>

      <!-- 空状态 -->
      <div v-if="!loading && items.length === 0" class="empty-state">
        <el-icon :size="48" class="empty-icon"><FolderOpened /></el-icon>
        <p class="empty-text">暂无生成记录</p>
        <p class="empty-hint">开始生成图片后，记录将显示在这里</p>
      </div>

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
              loading="lazy"
            />
            <div v-else class="thumb-placeholder">
              <el-icon :size="24"><Picture /></el-icon>
            </div>
          </div>
          <div class="history-info">
            <div class="hi-prompt">{{ item.prompt }}</div>
            <div class="hi-meta">
              <el-tag size="small" type="info" effect="plain">{{ getTaskTypeLabel(item.task_type) }}</el-tag>
              <span class="meta-sep">·</span>
              <span>{{ item.image_size }}</span>
              <span class="meta-sep">·</span>
              <span>{{ formatTime(item.created_at) }}</span>
              <span class="meta-sep">·</span>
              <span :class="'status-badge status-' + item.status">{{ getStatusLabel(item.status) }}</span>
            </div>
          </div>
          <div class="history-actions" @click.stop>
            <el-button
              type="danger"
              size="small"
              text
              @click="confirmDelete(item)"
              class="delete-btn"
            >
              <el-icon :size="16"><Delete /></el-icon>
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
          background
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
import { Clock, Refresh, FolderOpened, Picture, Delete } from '@element-plus/icons-vue'
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
.history-view {
  animation: fadeInUp 0.35s cubic-bezier(0.4, 0, 0.2, 1);
}

.title-row {
  display: flex;
  justify-content: space-between;
  align-items: center;
  width: 100%;
}

.title-left {
  display: flex;
  align-items: center;
  gap: 6px;
}

.refresh-btn {
  font-weight: 500;
}

.empty-state {
  text-align: center;
  padding: 48px 0;
}

.empty-icon {
  color: var(--text-placeholder);
  margin-bottom: 12px;
}

.empty-text {
  font-size: 15px;
  color: var(--text-secondary);
  font-weight: 500;
}

.empty-hint {
  font-size: 13px;
  color: var(--text-placeholder);
  margin-top: 4px;
}

.history-list {
  border: 1px solid var(--border-light);
  border-radius: var(--radius-lg);
  overflow: hidden;
}

.history-item {
  display: flex;
  align-items: center;
  gap: 16px;
  padding: 14px 18px;
  border-bottom: 1px solid var(--border-lighter);
  transition: background var(--transition-fast);
  cursor: pointer;
}

.history-item:last-child {
  border-bottom: none;
}

.history-item:hover {
  background: var(--bg-hover);
}

.history-thumb {
  width: 64px;
  height: 64px;
  border-radius: var(--radius-md);
  background: var(--bg-hover);
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
  color: var(--text-placeholder);
}

.history-info {
  flex: 1;
  min-width: 0;
}

.hi-prompt {
  font-size: 14px;
  color: var(--text-primary);
  overflow: hidden;
  text-overflow: ellipsis;
  white-space: nowrap;
  margin-bottom: 6px;
  font-weight: 500;
}

.hi-meta {
  display: flex;
  align-items: center;
  gap: 4px;
  font-size: 12px;
  color: var(--text-secondary);
}

.meta-sep {
  color: var(--border-base);
}

.status-badge {
  padding: 1px 8px;
  border-radius: var(--radius-full);
  font-size: 11px;
  font-weight: 600;
}

.status-completed {
  color: var(--success);
  background: var(--success-bg);
}

.status-failed {
  color: var(--danger);
  background: var(--danger-bg);
}

.status-processing,
.status-pending {
  color: var(--warning);
  background: var(--warning-bg);
}

.pagination-wrapper {
  display: flex;
  justify-content: center;
  margin-top: 20px;
}

.history-actions {
  flex-shrink: 0;
}

.delete-btn {
  opacity: 0.4;
  transition: opacity var(--transition-fast);
}

.history-item:hover .delete-btn {
  opacity: 1;
}

/* ======== 响应式 ======== */
/* 移动端：列表项垂直布局，mete信息精简 */
@media (max-width: 767px) {
  /* 减少动画开销 */
  .history-view {
    animation: none;
  }

  /* 区块padding收缩 */
  :deep(.page-section) {
    padding: 16px;
  }

  /* 列表项改为垂直布局：缩略图在上，信息在下 */
  .history-item {
    flex-direction: column;
    align-items: flex-start;
    gap: 10px;
    padding: 12px 14px;
    position: relative;
  }

  /* 缩略图变为全宽 */
  .history-thumb {
    width: 100%;
    height: 160px;
  }

  /* 信息区域全宽 */
  .history-info {
    width: 100%;
  }

  /* 提示词文本显示两行 */
  .hi-prompt {
    white-space: normal;
    display: -webkit-box;
    -webkit-line-clamp: 2;
    -webkit-box-orient: vertical;
    overflow: hidden;
    font-size: 13px;
  }

  /* meta信息隐藏中间多余项目，只保留tag和状态 */
  .hi-meta {
    flex-wrap: wrap;
    gap: 4px 8px;
    font-size: 11px;
  }

  /* 分隔符和部分信息项在移动端隐藏 */
  .hi-meta .meta-sep {
    display: none;
  }

  .hi-meta > span:nth-child(4) {
    display: none;
  }

  /* 删除按钮固定右上角，始终显示 */
  .history-actions {
    position: absolute;
    top: 12px;
    right: 14px;
  }

  .delete-btn {
    opacity: 0.7;
  }

  /* 空状态padding缩小 */
  .empty-state {
    padding: 32px 0;
  }

  /* 分页器居中 */
  .pagination-wrapper {
    justify-content: center;
    margin-top: 16px;
  }
}

/* 平板端：适度间距 */
@media (min-width: 768px) and (max-width: 1023px) {
  :deep(.page-section) {
    padding: 20px;
  }

  /* 缩略图略大一些 */
  .history-thumb {
    width: 80px;
    height: 80px;
  }

  /* meta信息适当缩小 */
  .hi-meta {
    font-size: 11px;
  }
}
</style>
