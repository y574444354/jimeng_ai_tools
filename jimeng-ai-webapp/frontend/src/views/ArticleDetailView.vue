<template>
  <div class="article-detail-view">
    <div v-if="article" class="page-section">
      <div class="section-title">
        <div class="title-row">
          <span class="title-left">
            <el-icon :size="18"><Document /></el-icon>
            {{ article.title }}
          </span>
          <div class="title-actions">
            <el-button size="small" @click="$router.push(`/articles/${article.id}/edit`)">
              <el-icon :size="14"><Edit /></el-icon>
              编辑
            </el-button>
            <el-button size="small" type="danger" @click="confirmDelete">
              <el-icon :size="14"><Delete /></el-icon>
              删除
            </el-button>
          </div>
        </div>
      </div>

      <div class="article-meta">
        <el-tag v-if="article.category_name" size="small" effect="plain" type="info">{{ article.category_name }}</el-tag>
        <span v-for="tag in article.tags" :key="tag.id" class="tag-dot" :style="{ color: tag.color }">● {{ tag.name }}</span>
        <span class="meta-text">{{ article.word_count }} 字 · {{ formatTime(article.created_at) }}</span>
        <el-tag :type="statusTagType(article.status)" size="small">{{ statusLabel(article.status) }}</el-tag>
      </div>

      <div class="article-content" v-html="renderedContent"></div>
    </div>

    <div v-else-if="loading" class="page-section" style="text-align: center; padding: 48px;">
      <p>加载中...</p>
    </div>

    <DeleteConfirmModal
      v-model:visible="deleteVisible"
      @confirm="handleDelete"
    />
  </div>
</template>

<script setup lang="ts">
import { ref, computed, onMounted } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import { Document, Edit, Delete } from '@element-plus/icons-vue'
import { useArticleStore } from '@/stores/article'
import DeleteConfirmModal from '@/components/DeleteConfirmModal.vue'
import { ElMessage } from 'element-plus'

const route = useRoute()
const router = useRouter()
const articleStore = useArticleStore()

const loading = ref(true)
const deleteVisible = ref(false)

const article = computed(() => articleStore.currentArticle)

// 简单的 Markdown 渲染
const renderedContent = computed(() => {
  const content = article.value?.content || ''
  if (!content) return '<p style="color: #9CA3AF">暂无正文</p>'
  return content
    .replace(/### (.+)/g, '<h3>$1</h3>')
    .replace(/## (.+)/g, '<h2>$1</h2>')
    .replace(/# (.+)/g, '<h1>$1</h1>')
    .replace(/\*\*(.+?)\*\*/g, '<strong>$1</strong>')
    .replace(/\*(.+?)\*/g, '<em>$1</em>')
    .replace(/\[(.+?)\]\((.+?)\)/g, '<a href="$2" target="_blank">$1</a>')
    .replace(/`(.+?)`/g, '<code>$1</code>')
    .replace(/\n\n/g, '</p><p>')
    .replace(/\n/g, '<br/>')
    .replace(/^/, '<p>')
    .replace(/$/, '</p>')
})

function statusTagType(status: string): 'info' | 'success' {
  const map: Record<string, 'info' | 'success'> = { draft: 'info', published: 'success', published_xhs: 'success' }
  return map[status] || 'info'
}

function statusLabel(status: string): string {
  const map: Record<string, string> = { draft: '草稿', published: '已发布', published_xhs: '已发布小红书' }
  return map[status] || status
}

function formatTime(timeStr?: string): string {
  if (!timeStr) return ''
  const d = new Date(timeStr)
  return `${d.getFullYear()}-${String(d.getMonth() + 1).padStart(2, '0')}-${String(d.getDate()).padStart(2, '0')} ${String(d.getHours()).padStart(2, '0')}:${String(d.getMinutes()).padStart(2, '0')}`
}

function confirmDelete() {
  deleteVisible.value = true
}

async function handleDelete() {
  if (!article.value) return
  try {
    await articleStore.remove(article.value.id)
    deleteVisible.value = false
    ElMessage.success('文章已删除')
    router.push('/articles')
  } catch (e: any) {
    ElMessage.error(e.message || '删除失败')
  }
}

onMounted(async () => {
  const articleId = route.params.id as string
  if (articleId) {
    try {
      await articleStore.fetchArticle(articleId)
    } catch (e: any) {
      ElMessage.error(e.message || '加载失败')
    }
  }
  loading.value = false
})
</script>

<style scoped>
.article-detail-view {
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
  flex: 1;
  min-width: 0;
}

.title-actions {
  display: flex;
  gap: 8px;
  flex-shrink: 0;
}

.article-meta {
  display: flex;
  align-items: center;
  gap: 10px;
  margin-bottom: 24px;
  padding-bottom: 16px;
  border-bottom: 1px solid var(--border-light);
  flex-wrap: wrap;
}

.tag-dot {
  font-size: 11px;
  white-space: nowrap;
}

.meta-text {
  font-size: 13px;
  color: var(--text-placeholder);
}

.article-content {
  font-size: 15px;
  line-height: 1.8;
  color: var(--text-regular);
  max-width: 800px;
}

.article-content :deep(h1) { font-size: 24px; margin: 24px 0 16px; color: var(--text-primary); }
.article-content :deep(h2) { font-size: 20px; margin: 20px 0 12px; color: var(--text-primary); }
.article-content :deep(h3) { font-size: 17px; margin: 16px 0 10px; color: var(--text-primary); }
.article-content :deep(p) { margin: 8px 0; }
.article-content :deep(a) { color: var(--primary); }
.article-content :deep(code) { background: var(--bg-hover); padding: 2px 6px; border-radius: 3px; font-size: 13px; }
.article-content :deep(strong) { font-weight: 600; }
</style>
