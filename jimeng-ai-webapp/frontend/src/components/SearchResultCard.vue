<template>
  <div class="search-result-card" :class="{ selected }" @click="$emit('toggle')">
    <div class="card-check">
      <el-icon :size="18" :color="selected ? '#6366F1' : '#D1D5DB'">
        <CircleCheckFilled v-if="selected" />
        <CircleCheck v-else />
      </el-icon>
    </div>
    <div class="card-body">
      <h4 class="card-title">{{ result.title }}</h4>
      <p class="card-snippet" v-if="result.snippet">{{ result.snippet }}</p>
      <a class="card-url" v-if="result.url" :href="result.url" target="_blank" @click.stop>
        {{ result.url }}
      </a>
      <div class="card-actions" v-if="result.url" @click.stop>
        <el-button text size="small" type="primary" :icon="Download" :loading="fetching" @click="handleFetch">
          {{ fetching ? '抓取中...' : '抓取全文' }}
        </el-button>
        <span v-if="fetchedContent" class="fetched-badge">
          <el-icon :size="12"><CircleCheckFilled /></el-icon>
          已抓取 {{ fetchedLength }} 字
        </span>
      </div>
      <div class="card-content-preview" v-if="showPreview">
        <p>{{ fetchedPreview }}</p>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, computed } from 'vue'
import { CircleCheck, CircleCheckFilled, Download } from '@element-plus/icons-vue'
import { ElMessage } from 'element-plus'
import { fetchWebContent, type SearchResult } from '@/api/search'

const props = defineProps<{
  result: SearchResult
  selected: boolean
}>()

defineEmits<{
  (e: 'toggle'): void
}>()

const fetching = ref(false)
const fetchedContent = ref('')

const fetchedLength = computed(() => fetchedContent.value.length)
const showPreview = computed(() => fetchedContent.value.length > 0)
const fetchedPreview = computed(() => {
  const text = fetchedContent.value
  return text.length > 300 ? text.slice(0, 300) + '...' : text
})

async function handleFetch() {
  if (!props.result.url) return
  fetching.value = true
  try {
    const result = await fetchWebContent(props.result.url)
    fetchedContent.value = result.content || ''
    if (fetchedContent.value) {
      ElMessage.success(`已抓取 ${fetchedContent.value.length} 字`)
    } else {
      ElMessage.warning('未抓取到有效内容，可尝试浏览器模式')
    }
  } catch (e: any) {
    ElMessage.error(e?.message || '抓取失败')
  } finally {
    fetching.value = false
  }
}
</script>

<style scoped>
.search-result-card {
  display: flex;
  gap: 10px;
  padding: 12px;
  border-radius: var(--radius-sm);
  cursor: pointer;
  transition: all var(--transition-fast);
  border: 1px solid var(--border-lighter);
  margin-bottom: 8px;
}

.search-result-card:hover {
  background: var(--bg-hover);
  border-color: var(--border-base);
}

.search-result-card.selected {
  background: var(--primary-bg);
  border-color: var(--primary-light);
}

.card-check {
  flex-shrink: 0;
  display: flex;
  align-items: flex-start;
  padding-top: 2px;
}

.card-body {
  flex: 1;
  min-width: 0;
}

.card-title {
  font-size: 14px;
  font-weight: 600;
  color: var(--text-primary);
  margin-bottom: 4px;
  line-height: 1.4;
  display: -webkit-box;
  -webkit-line-clamp: 2;
  -webkit-box-orient: vertical;
  overflow: hidden;
}

.card-snippet {
  font-size: 12px;
  color: var(--text-secondary);
  line-height: 1.5;
  margin-bottom: 4px;
  display: -webkit-box;
  -webkit-line-clamp: 3;
  -webkit-box-orient: vertical;
  overflow: hidden;
}

.card-url {
  font-size: 11px;
  color: var(--text-placeholder);
  text-decoration: none;
  overflow: hidden;
  text-overflow: ellipsis;
  white-space: nowrap;
  display: block;
}

.card-url:hover {
  color: var(--primary);
}

.card-actions {
  display: flex;
  align-items: center;
  gap: 8px;
  margin-top: 6px;
}

.fetched-badge {
  font-size: 11px;
  color: var(--primary);
  display: flex;
  align-items: center;
  gap: 3px;
}

.card-content-preview {
  margin-top: 8px;
  padding: 8px;
  background: var(--bg-page);
  border-radius: var(--radius-sm);
  font-size: 12px;
  color: var(--text-secondary);
  line-height: 1.6;
  max-height: 120px;
  overflow-y: auto;
}

.card-content-preview p {
  margin: 0;
}

/* ======== 响应式 ======== */
@media (max-width: 767px) {
  .search-result-card {
    padding: 10px;
    gap: 8px;
  }
  .card-title {
    font-size: 13px;
  }
  .card-snippet {
    font-size: 11px;
  }
  .card-actions {
    flex-wrap: wrap;
    gap: 4px;
  }
  .card-content-preview {
    max-height: 80px;
    padding: 6px;
  }
  .card-url {
    font-size: 10px;
  }
}
</style>
