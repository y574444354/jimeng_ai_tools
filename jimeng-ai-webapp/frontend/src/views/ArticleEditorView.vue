<template>
  <div class="article-editor-view">
    <!-- 三栏布局 -->
    <div class="editor-layout">
      <!-- 左侧：搜索面板 -->
      <div class="editor-left">
        <SearchPanel
          :article-id="articleId"
          @use-title="onUseTitle"
        />
      </div>

      <!-- 中间：编辑器 -->
      <div class="editor-center">
        <div class="editor-toolbar">
          <el-button size="small" @click="insertBold">**B**</el-button>
          <el-button size="small" @click="insertItalic">*I*</el-button>
          <el-button size="small" @click="insertHeading">H1</el-button>
          <el-button size="small" @click="insertLink">链接</el-button>
          <el-button size="small" @click="insertImage">图片</el-button>
          <el-button size="small" @click="insertQuote">引用</el-button>
          <el-button size="small" @click="insertCode">代码</el-button>
        </div>
        <ArticleEditor
          ref="editorRef"
          v-model="content"
        />
      </div>

      <!-- 右侧：文章信息 -->
      <div class="editor-right">
        <div class="info-section">
          <div class="section-label">文章标题</div>
          <el-input v-model="title" placeholder="输入文章标题..." maxlength="200" show-word-limit />
        </div>

        <div class="info-section">
          <div class="section-label">摘要</div>
          <el-input
            v-model="summary"
            type="textarea"
            :rows="3"
            placeholder="文章摘要..."
            maxlength="500"
            show-word-limit
          />
        </div>

        <div class="info-section">
          <div class="section-label">分类</div>
          <el-select v-model="categoryId" placeholder="选择分类" clearable style="width: 100%">
            <el-option
              v-for="cat in articleStore.categories"
              :key="cat.id"
              :label="cat.name"
              :value="cat.id"
            />
          </el-select>
        </div>

        <div class="info-section">
          <div class="section-label">标签</div>
          <el-select
            v-model="selectedTagIds"
            multiple
            placeholder="选择标签"
            style="width: 100%"
          >
            <el-option
              v-for="tag in articleStore.tags"
              :key="tag.id"
              :label="tag.name"
              :value="tag.id"
            >
              <span :style="{ color: tag.color }">●</span>
              {{ tag.name }}
            </el-option>
          </el-select>
        </div>

        <div class="info-section">
          <div class="section-label">状态</div>
          <el-radio-group v-model="status">
            <el-radio value="draft">草稿</el-radio>
            <el-radio value="published">已发布</el-radio>
          </el-radio-group>
        </div>

        <div class="action-buttons">
          <el-button
            type="primary"
            :loading="saving"
            style="width: 100%"
            @click="saveArticle"
          >
            <el-icon><DocumentAdd /></el-icon>
            {{ articleId ? '更新文章' : '创建文章' }}
          </el-button>
          <el-button
            v-if="articleId"
            type="success"
            style="width: 100%"
            @click="showPublishDialog = true"
          >
            <el-icon><Promotion /></el-icon>
            发布到小红书
          </el-button>
        </div>

        <!-- 版本历史 -->
        <div v-if="articleId" class="info-section">
          <div class="section-label">版本历史</div>
          <div v-if="articleStore.currentVersions.length === 0" class="no-versions">
            暂无版本记录
          </div>
          <div v-else class="version-list">
            <div
              v-for="v in articleStore.currentVersions.slice(0, 5)"
              :key="v.id"
              class="version-item"
              @click="restoreVersion(v.id)"
            >
              <span class="v-num">v{{ v.version_number }}</span>
              <span class="v-time">{{ formatTime(v.created_at) }}</span>
            </div>
          </div>
        </div>
      </div>
    </div>

    <!-- 发布对话框 -->
    <PublishDialog
      v-model:visible="showPublishDialog"
      :article-id="articleId || ''"
      :article-title="title"
    />

    <LoadingOverlay
      :visible="articleStore.isGenerating"
      status="AI 生成中..."
    />
  </div>
</template>

<script setup lang="ts">
import { ref, watch, onMounted, onBeforeUnmount } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import { DocumentAdd, Promotion } from '@element-plus/icons-vue'
import { useArticleStore } from '@/stores/article'
import ArticleEditor from '@/components/ArticleEditor.vue'
import SearchPanel from '@/components/SearchPanel.vue'
import PublishDialog from '@/components/PublishDialog.vue'
import LoadingOverlay from '@/components/LoadingOverlay.vue'
import { ElMessage } from 'element-plus'

const route = useRoute()
const router = useRouter()
const articleStore = useArticleStore()

const articleId = ref<string>(route.params.id as string || '')
const title = ref('')
const content = ref('')
const summary = ref('')
const categoryId = ref<string>('')
const selectedTagIds = ref<string[]>([])
const status = ref('draft')
const saving = ref(false)
const showPublishDialog = ref(false)
const editorRef = ref()
let autoSaveTimer: any = null

// 编辑已有文章时加载数据
onMounted(async () => {
  await articleStore.fetchCategories()
  await articleStore.fetchTags()

  if (articleId.value) {
    try {
      const article = await articleStore.fetchArticle(articleId.value)
      title.value = article.title
      content.value = article.content || ''
      summary.value = article.summary || ''
      categoryId.value = article.category_id || ''
      selectedTagIds.value = article.tags?.map(t => t.id) || []
      status.value = article.status
      articleStore.fetchVersions(articleId.value)
      articleStore.fetchSources(articleId.value)
    } catch (e: any) {
      ElMessage.error(e.message || '加载文章失败')
    }
  }
})

// 页面关闭前自动保存
onBeforeUnmount(() => {
  if (autoSaveTimer) clearInterval(autoSaveTimer)
})

function onUseTitle(t: string) {
  title.value = t
}

// 编辑器工具栏
function insertBold() { editorRef.value?.insertText('**加粗文字**') }
function insertItalic() { editorRef.value?.insertText('*斜体文字*') }
function insertHeading() { editorRef.value?.insertText('\n# 标题\n') }
function insertLink() { editorRef.value?.insertText('[链接文字](https://)') }
function insertImage() { editorRef.value?.insertText('![图片描述](/output/...)') }
function insertQuote() { editorRef.value?.insertText('\n> 引用文字\n') }
function insertCode() { editorRef.value?.insertText('\n```\n代码块\n```\n') }

async function saveArticle() {
  if (!title.value.trim()) {
    ElMessage.warning('请输入文章标题')
    return
  }
  saving.value = true
  try {
    const data = {
      title: title.value,
      content: content.value,
      summary: summary.value || undefined,
      category_id: categoryId.value || undefined,
      tag_ids: selectedTagIds.value.length > 0 ? selectedTagIds.value : undefined,
      status: status.value,
    }
    if (articleId.value) {
      await articleStore.update(articleId.value, data)
      ElMessage.success('文章更新成功')
    } else {
      const result = await articleStore.create(data)
      articleId.value = result.id
      router.replace(`/articles/${result.id}/edit`)
      ElMessage.success('文章创建成功')
    }
  } catch (e: any) {
    ElMessage.error(e.message || '保存失败')
  } finally {
    saving.value = false
  }
}

async function restoreVersion(versionId: string) {
  try {
    await articleStore.restoreVersion(articleId.value, versionId)
    content.value = articleStore.currentArticle?.content || ''
    title.value = articleStore.currentArticle?.title || ''
    ElMessage.success('版本恢复成功')
  } catch (e: any) {
    ElMessage.error(e.message || '恢复失败')
  }
}

function formatTime(timeStr?: string): string {
  if (!timeStr) return ''
  const d = new Date(timeStr)
  return `${d.getMonth() + 1}-${d.getDate()} ${d.getHours()}:${String(d.getMinutes()).padStart(2, '0')}`
}
</script>

<style scoped>
.article-editor-view {
  height: calc(100vh - var(--header-height) - 56px);
  animation: fadeInUp 0.35s cubic-bezier(0.4, 0, 0.2, 1);
}

.editor-layout {
  display: flex;
  height: 100%;
  gap: 0;
  background: var(--bg-content);
  border-radius: var(--radius-lg);
  box-shadow: var(--shadow-sm);
  overflow: hidden;
}

.editor-left {
  width: 300px;
  border-right: 1px solid var(--border-light);
  overflow-y: auto;
}

.editor-center {
  flex: 1;
  display: flex;
  flex-direction: column;
  border-right: 1px solid var(--border-light);
}

.editor-toolbar {
  display: flex;
  gap: 4px;
  padding: 8px 12px;
  border-bottom: 1px solid var(--border-light);
  background: var(--bg-hover);
}

.editor-right {
  width: 280px;
  padding: 16px;
  overflow-y: auto;
  display: flex;
  flex-direction: column;
  gap: 16px;
}

.info-section {
  display: flex;
  flex-direction: column;
  gap: 6px;
}

.section-label {
  font-size: 13px;
  font-weight: 600;
  color: var(--text-secondary);
}

.action-buttons {
  display: flex;
  flex-direction: column;
  gap: 8px;
  padding-top: 8px;
  border-top: 1px solid var(--border-light);
}

.no-versions {
  font-size: 12px;
  color: var(--text-placeholder);
  text-align: center;
  padding: 12px 0;
}

.version-list {
  display: flex;
  flex-direction: column;
  gap: 4px;
}

.version-item {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 6px 8px;
  border-radius: var(--radius-sm);
  cursor: pointer;
  font-size: 12px;
  transition: background var(--transition-fast);
}

.version-item:hover {
  background: var(--primary-bg);
}

.v-num {
  font-weight: 600;
  color: var(--primary);
}

.v-time {
  color: var(--text-placeholder);
}
</style>
