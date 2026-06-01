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
    </div>
  </div>
</template>

<script setup lang="ts">
import { CircleCheck, CircleCheckFilled } from '@element-plus/icons-vue'
import type { SearchResult } from '@/api/search'

defineProps<{
  result: SearchResult
  selected: boolean
}>()

defineEmits<{
  (e: 'toggle'): void
}>()
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
</style>
