<template>
  <div class="article-list-view">
    <div class="page-section">
      <div class="section-title">
        <div class="title-row">
          <span class="title-left">
            <el-icon :size="18"><Notebook /></el-icon>
            文章管理
          </span>
          <div class="title-actions">
            <el-button type="primary" size="small" @click="$router.push('/articles/new')">
              <el-icon :size="14"><EditPen /></el-icon>
              写文章
            </el-button>
          </div>
        </div>
      </div>

      <!-- 筛选栏 -->
      <div class="filter-bar">
        <el-input
          v-model="keyword"
          placeholder="搜索文章标题或内容..."
          :prefix-icon="Search"
          clearable
          style="width: 260px"
          @keyup.enter="doSearch"
          @clear="doSearch"
        />
        <el-select v-model="filterStatus" placeholder="状态筛选" clearable style="width: 140px" @change="doSearch">
          <el-option label="全部状态" value="" />
          <el-option label="草稿" value="draft" />
          <el-option label="已发布" value="published" />
          <el-option label="已发布小红书" value="published_xhs" />
        </el-select>
        <el-select v-model="filterCategory" placeholder="分类筛选" clearable style="width: 160px" @change="doSearch">
          <el-option label="全部分类" value="" />
          <el-option v-for="cat in articleStore.categories" :key="cat.id" :label="cat.name" :value="cat.id" />
        </el-select>
        <el-button @click="doSearch">
          <el-icon :size="14"><Search /></el-icon>
          搜索
        </el-button>
      </div>

      <!-- 空状态 -->
      <div v-if="!articleStore.loading && articleStore.articles.length === 0" class="empty-state">
        <el-icon :size="48" class="empty-icon"><FolderOpened /></el-icon>
        <p class="empty-text">暂无文章</p>
        <p class="empty-hint">点击右上角"写文章"开始创作</p>
      </div>

      <!-- 文章列表 -->
      <div v-else class="article-table-wrapper">
        <el-table :data="articleStore.articles" style="width: 100%" @row-click="goEdit" v-loading="articleStore.loading">
          <el-table-column prop="title" label="标题" min-width="280">
            <template #default="{ row }">
              <div class="cell-title">
                <span class="cell-cover" v-if="row.cover_image_path">
                  <img :src="row.cover_image_path" alt="" />
                </span>
                <div class="cell-title-text">
                  <span class="title-main">{{ row.title }}</span>
                  <span class="title-summary" v-if="row.summary">{{ row.summary.substring(0, 60) }}{{ row.summary.length > 60 ? '...' : '' }}</span>
                </div>
              </div>
            </template>
          </el-table-column>
          <el-table-column prop="category_name" label="分类" width="120">
            <template #default="{ row }">
              <el-tag v-if="row.category_name" size="small" effect="plain" type="info">{{ row.category_name }}</el-tag>
              <span v-else class="text-muted">-</span>
            </template>
          </el-table-column>
          <el-table-column label="标签" width="180">
            <template #default="{ row }">
              <div class="tag-list" v-if="row.tags?.length">
                <span
                  v-for="tag in row.tags.slice(0, 3)"
                  :key="tag.id"
                  class="tag-dot"
                  :style="{ color: tag.color }"
                >● {{ tag.name }}</span>
              </div>
              <span v-else class="text-muted">-</span>
            </template>
          </el-table-column>
          <el-table-column prop="status" label="状态" width="120">
            <template #default="{ row }">
              <el-tag :type="statusTagType(row.status)" size="small">{{ statusLabel(row.status) }}</el-tag>
            </template>
          </el-table-column>
          <el-table-column label="字数" width="80" align="right">
            <template #default="{ row }">
              <span class="text-muted">{{ row.word_count }}</span>
            </template>
          </el-table-column>
          <el-table-column label="更新时间" width="170">
            <template #default="{ row }">
              <span class="text-muted">{{ formatTime(row.created_at) }}</span>
            </template>
          </el-table-column>
          <el-table-column label="操作" width="120" fixed="right">
            <template #default="{ row }">
              <el-button size="small" text type="primary" @click.stop="goEdit(row)">编辑</el-button>
              <el-button size="small" text type="danger" @click.stop="confirmDelete(row.id)">删除</el-button>
            </template>
          </el-table-column>
        </el-table>
      </div>

      <!-- 分页 -->
      <div class="pagination-wrapper" v-if="articleStore.total > articleStore.pageSize">
        <el-pagination
          v-model:current-page="articleStore.currentPage"
          :page-size="articleStore.pageSize"
          :total="articleStore.total"
          layout="prev, pager, next"
          background
          @current-change="handlePageChange"
        />
      </div>
    </div>

    <!-- 删除确认弹框 -->
    <DeleteConfirmModal
      v-model:visible="deleteVisible"
      @confirm="handleDelete"
    />
  </div>
</template>

<script setup lang="ts">
import { ref, onMounted } from 'vue'
import { useRouter } from 'vue-router'
import { Notebook, EditPen, Search, FolderOpened } from '@element-plus/icons-vue'
import { useArticleStore } from '@/stores/article'
import DeleteConfirmModal from '@/components/DeleteConfirmModal.vue'
import { ElMessage } from 'element-plus'

const router = useRouter()
const articleStore = useArticleStore()

const keyword = ref('')
const filterStatus = ref('')
const filterCategory = ref('')
const deleteVisible = ref(false)
const deleteTarget = ref('')

function statusTagType(status: string): 'info' | 'success' | 'warning' {
  const map: Record<string, 'info' | 'success' | 'warning'> = {
    draft: 'info',
    published: 'success',
    published_xhs: 'success',
  }
  return map[status] || 'info'
}

function statusLabel(status: string): string {
  const map: Record<string, string> = {
    draft: '草稿',
    published: '已发布',
    published_xhs: '已发布小红书',
  }
  return map[status] || status
}

function formatTime(timeStr?: string): string {
  if (!timeStr) return ''
  const d = new Date(timeStr)
  return `${d.getFullYear()}-${String(d.getMonth() + 1).padStart(2, '0')}-${String(d.getDate()).padStart(2, '0')} ${String(d.getHours()).padStart(2, '0')}:${String(d.getMinutes()).padStart(2, '0')}`
}

function goEdit(row: any) {
  router.push(`/articles/${row.id}/edit`)
}

function confirmDelete(id: string) {
  deleteTarget.value = id
  deleteVisible.value = true
}

async function handleDelete() {
  if (!deleteTarget.value) return
  try {
    await articleStore.remove(deleteTarget.value)
    deleteVisible.value = false
    ElMessage.success('文章已删除')
    doSearch()
  } catch (e: any) {
    ElMessage.error(e.message || '删除失败')
  }
}

async function doSearch() {
  await articleStore.fetchArticles({
    page: 1,
    keyword: keyword.value || undefined,
    status: filterStatus.value || undefined,
    category_id: filterCategory.value || undefined,
  })
}

function handlePageChange(page: number) {
  articleStore.fetchArticles({
    page,
    keyword: keyword.value || undefined,
    status: filterStatus.value || undefined,
    category_id: filterCategory.value || undefined,
  })
}

onMounted(async () => {
  await articleStore.fetchCategories()
  await doSearch()
})
</script>

<style scoped>
.article-list-view {
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

.title-actions {
  display: flex;
  gap: 8px;
}

.filter-bar {
  display: flex;
  gap: 12px;
  margin-bottom: 20px;
  flex-wrap: wrap;
}

.cell-title {
  display: flex;
  align-items: center;
  gap: 10px;
}

.cell-cover {
  width: 40px;
  height: 40px;
  border-radius: var(--radius-sm);
  overflow: hidden;
  flex-shrink: 0;
  background: var(--bg-hover);
}

.cell-cover img {
  width: 100%;
  height: 100%;
  object-fit: cover;
}

.cell-title-text {
  display: flex;
  flex-direction: column;
  gap: 2px;
  min-width: 0;
}

.title-main {
  font-weight: 600;
  color: var(--text-primary);
  overflow: hidden;
  text-overflow: ellipsis;
  white-space: nowrap;
}

.title-summary {
  font-size: 12px;
  color: var(--text-placeholder);
  overflow: hidden;
  text-overflow: ellipsis;
  white-space: nowrap;
}

.tag-list {
  display: flex;
  gap: 6px;
  flex-wrap: wrap;
}

.tag-dot {
  font-size: 11px;
}

.text-muted {
  color: var(--text-placeholder);
  font-size: 13px;
}

.article-table-wrapper {
  border-radius: var(--radius-md);
  overflow: hidden;
}

.empty-state {
  text-align: center;
  padding: 48px 0;
}

.empty-icon { color: var(--text-placeholder); margin-bottom: 12px; }
.empty-text { font-size: 15px; color: var(--text-secondary); font-weight: 500; }
.empty-hint { font-size: 13px; color: var(--text-placeholder); margin-top: 4px; }

.pagination-wrapper {
  display: flex;
  justify-content: center;
  margin-top: 20px;
}

/* ======== 响应式 ======== */
@media (max-width: 767px) {
  .filter-bar {
    flex-direction: column;
    gap: 8px;
  }
  .filter-bar > * {
    width: 100% !important;
  }
  .title-row {
    flex-direction: column;
    align-items: flex-start;
    gap: 10px;
  }
  .title-actions {
    width: 100%;
    flex-wrap: wrap;
  }
  .article-table-wrapper {
    overflow-x: auto;
    -webkit-overflow-scrolling: touch;
  }
  .article-table-wrapper :deep(.el-table) {
    min-width: 700px;
  }
  .cell-title {
    flex-direction: column;
    align-items: flex-start;
    gap: 6px;
  }
  .pagination-wrapper {
    justify-content: flex-start;
  }
}
</style>
