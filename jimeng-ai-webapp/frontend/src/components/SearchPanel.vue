<template>
  <div class="search-panel">
    <!-- 搜索输入 -->
    <div class="search-input-area">
      <el-input
        v-model="searchQuery"
        placeholder="输入关键词搜索全网信息..."
        :prefix-icon="Search"
        clearable
        @keyup.enter="doSearch"
      >
        <template #append>
          <el-button :loading="searchStore.isSearching" @click="doSearch">
            搜索
          </el-button>
        </template>
      </el-input>
    </div>

    <!-- 搜索结果 -->
    <div class="search-results" v-if="searchStore.results.length > 0">
      <div class="results-header">
        <span class="results-count">{{ searchStore.results.length }} 条结果</span>
        <el-button
          v-if="searchStore.selectedSources.length > 0"
          type="primary"
          size="small"
          :loading="searchStore.isSummarizing"
          @click="doSummarize"
        >
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

      <el-button
        v-if="articleId && searchStore.selectedSources.length > 0"
        type="default"
        size="small"
        style="margin-top: 12px; width: 100%"
        @click="saveToArticle"
      >
        保存选中素材到文章
      </el-button>
    </div>

    <!-- AI总结结果 -->
    <div class="summarize-result" v-if="searchStore.summarizeResult">
      <div class="section-title">AI 总结</div>
      <div v-if="searchStore.summarizeResult.summary" class="summary-text">
        {{ searchStore.summarizeResult.summary }}
      </div>
      <div v-if="searchStore.summarizeResult.title_suggestions.length" class="title-suggestions">
        <div class="label">推荐标题:</div>
        <el-tag
          v-for="(t, i) in searchStore.summarizeResult.title_suggestions"
          :key="i"
          size="small"
          class="title-tag"
          @click="$emit('useTitle', t)"
        >
          {{ t }}
        </el-tag>
      </div>
    </div>

    <!-- 空状态 -->
    <div v-if="!searchStore.isSearching && searchStore.results.length === 0 && !searchStore.summarizeResult" class="empty-hint">
      <el-icon :size="32"><Search /></el-icon>
      <p>输入关键词搜索互联网信息</p>
      <p class="sub">搜索结果可作为文章素材，AI会自动整理生成大纲</p>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref } from 'vue'
import { Search } from '@element-plus/icons-vue'
import { useSearchStore } from '@/stores/search'
import { useArticleStore } from '@/stores/article'
import SearchResultCard from '@/components/SearchResultCard.vue'

defineEmits<{
  (e: 'useTitle', title: string): void
}>()

const props = defineProps<{
  articleId?: string
}>()

const searchStore = useSearchStore()
const articleStore = useArticleStore()
const searchQuery = ref('')

async function doSearch() {
  if (!searchQuery.value.trim()) return
  await searchStore.search(searchQuery.value.trim())
}

async function doSummarize() {
  await searchStore.summarize(searchStore.selectedSources)
}

async function saveToArticle() {
  if (!props.articleId) return
  const sources = searchStore.selectedSources.map(s => ({
    title: s.title,
    url: s.url || '',
    snippet: s.snippet || '',
    content: s.content || '',
    source_type: 'web_search',
  }))
  await articleStore.saveSources(props.articleId, sources)
  ElMessage.success(`已保存${sources.length}条素材`)
}
</script>

<script lang="ts">
import { ElMessage } from 'element-plus'
export default {}
</script>

<style scoped>
.search-panel {
  display: flex;
  flex-direction: column;
  height: 100%;
  padding: 16px;
}

.search-input-area {
  margin-bottom: 16px;
}

.results-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 12px;
}

.results-count {
  font-size: 13px;
  color: var(--text-secondary);
  font-weight: 500;
}

.summarize-result {
  margin-top: 20px;
  padding: 16px;
  background: var(--primary-bg);
  border-radius: var(--radius-md);
}

.summary-text {
  font-size: 14px;
  color: var(--text-regular);
  line-height: 1.6;
  margin-bottom: 12px;
}

.title-suggestions {
  display: flex;
  flex-wrap: wrap;
  gap: 8px;
  align-items: center;
}

.title-suggestions .label {
  font-size: 12px;
  color: var(--text-secondary);
}

.title-tag {
  cursor: pointer;
}

.title-tag:hover {
  background: var(--primary);
  color: white;
}

.empty-hint {
  flex: 1;
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  color: var(--text-placeholder);
  gap: 8px;
}

.empty-hint p {
  font-size: 13px;
}

.empty-hint .sub {
  font-size: 12px;
}
</style>
