<template>
  <div class="search-view">
    <div class="page-section">
      <div class="section-title">
        <el-icon :size="18"><Search /></el-icon>
        智能搜索
      </div>

      <!-- 搜索输入 -->
      <div class="search-input-area">
        <el-input
          v-model="searchQuery"
          size="large"
          placeholder="输入关键词搜索全网信息，搜索结果可作为文章素材..."
          :prefix-icon="Search"
          clearable
          @keyup.enter="doSearch"
        >
          <template #append>
            <el-button :loading="searchStore.isSearching" @click="doSearch" style="width: 100px">
              {{ searchStore.isSearching ? '搜索中' : '搜索' }}
            </el-button>
          </template>
        </el-input>
      </div>

      <!-- 搜索结果区 -->
      <div v-if="searchStore.results.length > 0" class="results-area">
        <div class="results-toolbar">
          <span class="results-count">找到 {{ searchStore.results.length }} 条结果</span>
          <el-button
            v-if="searchStore.selectedSources.length > 0"
            type="primary"
            :loading="searchStore.isSummarizing"
            @click="doSummarize"
          >
            <el-icon :size="14"><MagicStick /></el-icon>
            AI总结选中素材 ({{ searchStore.selectedSources.length }})
          </el-button>
        </div>

        <SearchResultCard
          v-for="(result, idx) in searchStore.results"
          :key="idx"
          :result="result"
          :selected="searchStore.isSelected(result)"
          @toggle="searchStore.toggleSource(result)"
        />
      </div>

      <!-- AI总结结果 -->
      <div v-if="searchStore.summarizeResult" class="summarize-section">
        <div class="summarize-header">
          <el-icon :size="18"><MagicStick /></el-icon>
          <span>AI 智能总结</span>
        </div>

        <!-- 推荐标题 -->
        <div v-if="searchStore.summarizeResult.title_suggestions.length" class="suggested-titles">
          <div class="label">推荐标题</div>
          <div class="title-list">
            <el-tag
              v-for="(t, i) in searchStore.summarizeResult.title_suggestions"
              :key="i" size="default" class="title-tag"
            >{{ t }}</el-tag>
          </div>
        </div>

        <!-- 大纲 -->
        <div v-if="searchStore.summarizeResult.outline.length" class="outline-section">
          <div class="label">文章大纲</div>
          <div class="outline-list">
            <div v-for="(item, i) in searchStore.summarizeResult.outline" :key="i" class="outline-item">
              <div class="outline-heading">{{ item.heading }}</div>
              <ul v-if="item.key_points?.length">
                <li v-for="(kp, j) in item.key_points" :key="j">{{ kp }}</li>
              </ul>
            </div>
          </div>
        </div>

        <!-- 摘要 -->
        <div v-if="searchStore.summarizeResult.summary" class="summary-text">
          <div class="label">摘要</div>
          <p>{{ searchStore.summarizeResult.summary }}</p>
        </div>

        <!-- 操作按钮 -->
        <div class="action-area" v-if="searchStore.summarizeResult.full_content">
          <el-button type="primary" @click="createFromSearch">
            <el-icon :size="14"><DocumentAdd /></el-icon>
            基于此结果创建文章
          </el-button>
        </div>
      </div>

      <!-- 空状态 -->
      <div v-if="!searchStore.isSearching && searchStore.results.length === 0 && !searchStore.summarizeResult" class="empty-hint">
        <el-icon :size="48"><Search /></el-icon>
        <p>输入主题关键词搜索互联网信息</p>
        <p class="sub">AI会自动整理搜索结果，生成文章大纲和写作素材</p>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref } from 'vue'
import { useRouter } from 'vue-router'
import { Search, MagicStick, DocumentAdd } from '@element-plus/icons-vue'
import { useSearchStore } from '@/stores/search'
import { useArticleStore } from '@/stores/article'
import SearchResultCard from '@/components/SearchResultCard.vue'
import { ElMessage } from 'element-plus'

const router = useRouter()
const searchStore = useSearchStore()
const articleStore = useArticleStore()
const searchQuery = ref('')

async function doSearch() {
  if (!searchQuery.value.trim()) return
  searchStore.clearSearch()
  await searchStore.search(searchQuery.value.trim())
}

async function doSummarize() {
  await searchStore.summarize(searchStore.selectedSources)
}

async function createFromSearch() {
  try {
    const article = await articleStore.create({
      title: searchStore.summarizeResult?.title_suggestions?.[0] || searchQuery.value,
      content: searchStore.summarizeResult?.full_content || '',
      summary: searchStore.summarizeResult?.summary || '',
      status: 'draft',
    })
    // 保存搜索素材
    if (searchStore.selectedSources.length > 0) {
      const sources = searchStore.selectedSources.map(s => ({
        title: s.title,
        url: s.url || '',
        snippet: s.snippet || '',
        content: s.content || '',
        source_type: 'web_search',
      }))
      await articleStore.saveSources(article.id, sources)
    }
    ElMessage.success('文章已创建')
    router.push(`/articles/${article.id}/edit`)
  } catch (e: any) {
    ElMessage.error(e.message || '创建失败')
  }
}
</script>

<style scoped>
.search-view {
  animation: fadeInUp 0.35s cubic-bezier(0.4, 0, 0.2, 1);
}

.search-input-area {
  margin-bottom: 24px;
}

.results-toolbar {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 16px;
  padding-bottom: 12px;
  border-bottom: 1px solid var(--border-light);
}

.results-count {
  font-size: 14px;
  color: var(--text-secondary);
  font-weight: 500;
}

.summarize-section {
  margin-top: 28px;
  padding: 24px;
  background: var(--primary-bg);
  border-radius: var(--radius-lg);
  border: 1px solid var(--primary-bg-hover);
}

.summarize-header {
  display: flex;
  align-items: center;
  gap: 8px;
  font-size: 16px;
  font-weight: 700;
  color: var(--primary);
  margin-bottom: 20px;
}

.label {
  font-size: 13px;
  font-weight: 600;
  color: var(--text-secondary);
  margin-bottom: 8px;
}

.suggested-titles { margin-bottom: 20px; }
.title-list { display: flex; flex-wrap: wrap; gap: 8px; }
.title-tag { cursor: pointer; }

.outline-section { margin-bottom: 20px; }
.outline-item { margin-bottom: 12px; }
.outline-heading { font-size: 15px; font-weight: 600; color: var(--text-primary); margin-bottom: 4px; }
.outline-item ul { margin: 0; padding-left: 20px; }
.outline-item li { font-size: 13px; color: var(--text-regular); line-height: 1.6; }

.summary-text p {
  font-size: 14px;
  color: var(--text-regular);
  line-height: 1.7;
}

.action-area {
  margin-top: 20px;
  padding-top: 16px;
  border-top: 1px solid var(--border-base);
}

.empty-hint {
  text-align: center;
  padding: 60px 0;
  color: var(--text-placeholder);
}
.empty-hint p { font-size: 15px; margin-top: 12px; }
.empty-hint .sub { font-size: 13px; color: var(--text-secondary); }

/* ======== 响应式 ======== */
/* 移动端：工具栏垂直排列，总结区padding缩小 */
@media (max-width: 767px) {
  /* 减少动画开销 */
  .search-view {
    animation: none;
  }

  /* 区块padding收缩 */
  :deep(.page-section) {
    padding: 16px;
  }

  /* 搜索输入区间距收窄 */
  .search-input-area {
    margin-bottom: 16px;
  }

  /* 搜索结果工具栏改为垂直排列 */
  .results-toolbar {
    flex-direction: column;
    align-items: flex-start;
    gap: 10px;
  }

  .results-toolbar .el-button {
    width: 100%;
  }

  /* 总结区padding缩小 */
  .summarize-section {
    padding: 16px;
    margin-top: 20px;
  }

  /* 总结区头部 */
  .summarize-header {
    font-size: 14px;
    margin-bottom: 14px;
  }

  /* 标题tag全宽 */
  .title-tag {
    width: 100%;
    justify-content: center;
  }

  /* 操作区按钮全宽 */
  .action-area .el-button {
    width: 100%;
  }

  /* 空状态padding缩小 */
  .empty-hint {
    padding: 36px 0;
  }
  .empty-hint p {
    font-size: 14px;
  }
}

/* 平板端：适度间距 */
@media (min-width: 768px) and (max-width: 1023px) {
  :deep(.page-section) {
    padding: 20px;
  }

  /* 总结区适度padding */
  .summarize-section {
    padding: 20px;
  }
}
</style>
