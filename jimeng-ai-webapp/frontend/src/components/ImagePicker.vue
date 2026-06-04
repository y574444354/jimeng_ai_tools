<template>
  <div class="image-picker">
    <div class="picker-grid">
      <div
        v-for="img in recentImages"
        :key="img.path"
        class="picker-item"
        :class="{ selected: selected.includes(img.path) }"
        @click="toggle(img.path)"
      >
        <img :src="img.path" :alt="img.label" loading="lazy" />
        <div class="check-overlay" v-if="selected.includes(img.path)">
          <el-icon :size="20"><CircleCheckFilled /></el-icon>
        </div>
        <div class="img-label">{{ img.label }}</div>
      </div>
    </div>
    <div v-if="recentImages.length === 0" class="empty">
      <p>暂无可用图片</p>
      <p class="sub">生成图片后，可以在此选择作为文章配图</p>
    </div>
    <div class="picker-footer">
      <el-button size="small" @click="$emit('close')">完成（已选 {{ selected.length }} 张）</el-button>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, onMounted } from 'vue'
import { CircleCheckFilled } from '@element-plus/icons-vue'
import request from '@/api/request'

const props = defineProps<{
  modelValue: string[]
}>()

const emit = defineEmits<{
  (e: 'update:modelValue', value: string[]): void
  (e: 'close'): void
}>()

const recentImages = ref<{ path: string; label: string }[]>([])
const selected = ref<string[]>([...props.modelValue])

async function loadRecentImages() {
  try {
    const res: any = await request.get('/generations', { params: { page: 1, page_size: 20 } })
    const items = res.data?.list || []
    const images: { path: string; label: string }[] = []
    for (const item of items) {
      if (item.thumbnail_path) {
        images.push({
          path: item.thumbnail_path,
          label: item.prompt?.substring(0, 30) || '生成图片',
        })
      }
    }
    recentImages.value = images
  } catch {
    // 忽略加载错误
  }
}

function toggle(path: string) {
  const idx = selected.value.indexOf(path)
  if (idx >= 0) {
    selected.value.splice(idx, 1)
  } else {
    selected.value.push(path)
  }
  emit('update:modelValue', [...selected.value])
}

onMounted(() => {
  loadRecentImages()
})
</script>

<style scoped>
.image-picker {
  max-height: 400px;
  overflow-y: auto;
}

.picker-grid {
  display: grid;
  grid-template-columns: repeat(4, 1fr);
  gap: 10px;
}

.picker-item {
  position: relative;
  aspect-ratio: 1;
  border-radius: var(--radius-sm);
  overflow: hidden;
  cursor: pointer;
  border: 2px solid transparent;
  transition: all var(--transition-fast);
}

.picker-item:hover {
  border-color: var(--primary-light);
}

.picker-item.selected {
  border-color: var(--primary);
}

.picker-item img {
  width: 100%;
  height: 100%;
  object-fit: cover;
}

.check-overlay {
  position: absolute;
  top: 4px;
  right: 4px;
  color: var(--primary);
  background: white;
  border-radius: 50%;
}

.img-label {
  position: absolute;
  bottom: 0;
  left: 0;
  right: 0;
  padding: 4px 6px;
  background: rgba(0, 0, 0, 0.5);
  color: white;
  font-size: 10px;
  white-space: nowrap;
  overflow: hidden;
  text-overflow: ellipsis;
}

.empty {
  text-align: center;
  padding: 40px 0;
  color: var(--text-placeholder);
}
.empty p { font-size: 14px; margin: 4px 0; }
.empty .sub { font-size: 12px; }

.picker-footer {
  display: flex;
  justify-content: center;
  padding-top: 12px;
  border-top: 1px solid var(--border-light);
  margin-top: 12px;
}

/* ======== 响应式 ======== */
@media (max-width: 767px) {
  .picker-grid {
    grid-template-columns: repeat(3, 1fr);
    gap: 6px;
  }
  .image-picker {
    max-height: 300px;
  }
}
</style>
