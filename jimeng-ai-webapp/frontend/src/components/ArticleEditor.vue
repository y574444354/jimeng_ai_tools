<template>
  <div class="article-editor">
    <textarea
      ref="editorRef"
      class="editor-textarea"
      :value="modelValue"
      @input="onInput"
      placeholder="开始写作...支持 Markdown 格式"
      spellcheck="false"
    />
    <div class="editor-footer">
      <span class="word-count">{{ wordCount }} 字</span>
      <span class="format-hint">支持 Markdown | **加粗** *斜体* # 标题</span>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, computed } from 'vue'

const props = defineProps<{
  modelValue: string
}>()

const emit = defineEmits<{
  (e: 'update:modelValue', value: string): void
  (e: 'save'): void
}>()

const editorRef = ref<HTMLTextAreaElement>()

const wordCount = computed(() => {
  if (!props.modelValue) return 0
  // 去除markdown标记后统计中文字符和英文单词
  const text = props.modelValue.replace(/[#*`~>\[\]()!\-_|]/g, '')
  return text.replace(/\s+/g, '').length
})

function onInput(e: Event) {
  const target = e.target as HTMLTextAreaElement
  emit('update:modelValue', target.value)
}

// 暴露插入文本方法
function insertText(text: string) {
  const el = editorRef.value
  if (!el) return
  const start = el.selectionStart
  const end = el.selectionEnd
  const before = props.modelValue.substring(0, start)
  const after = props.modelValue.substring(end)
  const newValue = before + text + after
  emit('update:modelValue', newValue)
  // 恢复光标位置
  setTimeout(() => {
    el.focus()
    el.setSelectionRange(start + text.length, start + text.length)
  }, 0)
}

defineExpose({ insertText })
</script>

<style scoped>
.article-editor {
  display: flex;
  flex-direction: column;
  height: 100%;
}

.editor-textarea {
  flex: 1;
  width: 100%;
  border: none;
  outline: none;
  resize: none;
  padding: 20px;
  font-family: 'PingFang SC', 'Microsoft YaHei', -apple-system, sans-serif;
  font-size: 15px;
  line-height: 1.8;
  color: var(--text-primary);
  background: transparent;
}

.editor-textarea::placeholder {
  color: var(--text-placeholder);
}

.editor-footer {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 8px 20px;
  border-top: 1px solid var(--border-light);
  font-size: 12px;
  color: var(--text-secondary);
}

.word-count {
  font-weight: 500;
  color: var(--text-regular);
}

.format-hint {
  color: var(--text-placeholder);
}
</style>
