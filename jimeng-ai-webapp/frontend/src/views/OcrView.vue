<template>
  <div class="ocr-view">
    <!-- 图片上传区 -->
    <div class="page-section">
      <div class="section-title">
        <el-icon :size="18"><PictureFilled /></el-icon>
        上传图片
      </div>
      <ImageUploader @uploaded="handleImageUploaded" @removed="handleImageRemoved" />
    </div>

    <!-- 识别按钮 -->
    <el-button
      type="primary"
      size="large"
      :loading="ocrStore.isRecognizing"
      :disabled="!uploadedImagePath"
      @click="handleRecognize"
      class="recognize-btn"
    >
      <el-icon v-if="!ocrStore.isRecognizing" :size="18"><Document /></el-icon>
      {{ ocrStore.isRecognizing ? 'AI 识别中...' : '开始识别' }}
    </el-button>

    <!-- 识别结果区 -->
    <div class="page-section result-section" v-if="ocrStore.result">
      <!-- 结果概览 -->
      <div class="section-title">
        <el-icon :size="18"><Document /></el-icon>
        识别结果
      </div>
      <div class="result-summary">
        共识别 <span class="highlight">{{ ocrStore.result.total_lines }}</span> 行文字
      </div>

      <!-- 原始文本区 -->
      <div class="raw-text-section">
        <div class="raw-text-header">
          <span class="raw-text-label">原始文本</span>
          <el-button size="small" text @click="copyRawText" class="copy-btn">
            <el-icon :size="14"><CopyDocument /></el-icon>
            {{ copyBtnText }}
          </el-button>
        </div>
        <el-input
          type="textarea"
          :rows="6"
          :model-value="ocrStore.result.raw_text"
          readonly
          class="raw-text-input"
        />
      </div>

      <!-- 结构化展示区 -->
      <div class="structured-section">
        <div class="structured-label">结构化识别</div>
        <div v-for="(section, sIdx) in ocrStore.result.sections" :key="sIdx" class="ocr-section">
          <!-- 标题类型 section -->
          <template v-if="section.type === 'title'">
            <div class="section-title-line">
              <span class="title-bar"></span>
              <span class="title-text">{{ section.text }}</span>
            </div>
          </template>
          <!-- 正文类型 section -->
          <template v-else>
            <div class="section-body-line">
              <p class="body-text">{{ section.text }}</p>
            </div>
          </template>
          <!-- 每行置信度 -->
          <div class="line-detail" v-for="(line, lIdx) in section.lines" :key="lIdx">
            <span class="line-text">{{ line.text }}</span>
            <el-tag size="small" :type="line.confidence >= 0.8 ? 'success' : 'warning'">
              {{ (line.confidence * 100).toFixed(2) }}%
            </el-tag>
          </div>
        </div>
      </div>
    </div>

    <!-- 错误提示 -->
    <el-alert
      v-if="ocrStore.error"
      :title="ocrStore.error"
      type="error"
      show-icon
      closable
      @close="ocrStore.reset()"
    />

    <!-- 加载遮罩 -->
    <LoadingOverlay
      :visible="ocrStore.isRecognizing"
      text="AI 识别中..."
    />
  </div>
</template>

<script setup lang="ts">
import { ref } from 'vue'
import { Document, PictureFilled, CopyDocument } from '@element-plus/icons-vue'
import { useOcrStore } from '@/stores/ocr'
import ImageUploader from '@/components/ImageUploader.vue'
import LoadingOverlay from '@/components/LoadingOverlay.vue'

const ocrStore = useOcrStore()
const uploadedImagePath = ref('')
const copyBtnText = ref('复制')

function handleImageUploaded(filePath: string) {
  uploadedImagePath.value = filePath
}

function handleImageRemoved() {
  uploadedImagePath.value = ''
}

async function handleRecognize() {
  if (!uploadedImagePath.value) return
  ocrStore.reset()

  try {
    await ocrStore.startRecognize(uploadedImagePath.value)
  } catch (e) {
    // 错误已在 store 中处理
  }
}

async function copyRawText() {
  if (!ocrStore.result) return
  try {
    await navigator.clipboard.writeText(ocrStore.result.raw_text)
    copyBtnText.value = '已复制'
    setTimeout(() => {
      copyBtnText.value = '复制'
    }, 2000)
  } catch {
    copyBtnText.value = '复制失败'
    setTimeout(() => {
      copyBtnText.value = '复制'
    }, 2000)
  }
}
</script>

<style scoped>
.ocr-view {
  animation: fadeInUp 0.35s cubic-bezier(0.4, 0, 0.2, 1);
}

.recognize-btn {
  width: 100%;
  height: 52px;
  font-size: 16px;
  font-weight: 700;
  letter-spacing: 0.04em;
  border-radius: var(--radius-md);
  background: var(--primary-gradient) !important;
  border: none !important;
  transition: all var(--transition-base);
  margin-bottom: 24px;
}

.recognize-btn:hover {
  box-shadow: 0 6px 20px rgba(99, 102, 241, 0.4);
  transform: translateY(-2px);
}

.recognize-btn:active {
  transform: translateY(0);
}

.result-section {
  animation: fadeInUp 0.4s cubic-bezier(0.4, 0, 0.2, 1);
}

.result-summary {
  margin-bottom: 20px;
  font-size: 15px;
  color: var(--text-regular);
}

.result-summary .highlight {
  font-weight: 700;
  color: var(--primary);
  font-size: 18px;
}

/* 原始文本区 */
.raw-text-section {
  margin-bottom: 24px;
  padding-bottom: 24px;
  border-bottom: 1px solid var(--border-light);
}

.raw-text-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 10px;
}

.raw-text-label {
  font-size: 15px;
  font-weight: 600;
  color: var(--text-primary);
}

.copy-btn {
  color: var(--primary);
  font-size: 13px;
}

/* 结构化展示区 */
.structured-section {
  margin-top: 4px;
}

.structured-label {
  font-size: 15px;
  font-weight: 600;
  color: var(--text-primary);
  margin-bottom: 16px;
}

.ocr-section {
  margin-bottom: 20px;
  padding-bottom: 20px;
  border-bottom: 1px solid var(--border-light);
}

.ocr-section:last-child {
  margin-bottom: 0;
  padding-bottom: 0;
  border-bottom: none;
}

/* 标题行样式 */
.section-title-line {
  display: flex;
  align-items: center;
  gap: 10px;
  margin-bottom: 10px;
}

.title-bar {
  width: 4px;
  height: 28px;
  background: var(--primary-gradient);
  border-radius: 2px;
  flex-shrink: 0;
}

.title-text {
  font-size: 20px;
  font-weight: 700;
  color: var(--text-primary);
  letter-spacing: 0.01em;
}

/* 正文行样式 */
.section-body-line {
  margin-bottom: 10px;
}

.body-text {
  font-size: 15px;
  color: var(--text-regular);
  line-height: 1.8;
  margin: 0;
}

/* 单行详情 */
.line-detail {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 6px 12px;
  margin-bottom: 4px;
  border-radius: var(--radius-sm);
  background: var(--bg-hover);
  transition: background var(--transition-fast);
}

.line-detail:hover {
  background: var(--primary-bg);
}

.line-detail:last-child {
  margin-bottom: 0;
}

.line-text {
  font-size: 14px;
  color: var(--text-regular);
  flex: 1;
  margin-right: 12px;
  word-break: break-all;
}

/* ======== 响应式 ======== */
/* 移动端：行详情垂直排列，标题字号缩小 */
@media (max-width: 767px) {
  /* 减少动画开销 */
  .ocr-view {
    animation: none;
  }
  .result-section {
    animation: none;
  }

  /* 区块padding收缩 */
  :deep(.page-section) {
    padding: 16px;
  }

  /* 识别按钮触摸区域 */
  .recognize-btn {
    height: 48px;
    font-size: 15px;
  }

  /* 标题字号缩小 */
  .title-text {
    font-size: 17px;
  }

  /* 正文字号缩小 */
  .body-text {
    font-size: 14px;
  }

  /* 行详情改为垂直排列 */
  .line-detail {
    flex-direction: column;
    align-items: flex-start;
    gap: 6px;
    padding: 8px 10px;
  }

  .line-text {
    margin-right: 0;
  }

  /* 原始文本区padding收紧 */
  .raw-text-section {
    margin-bottom: 16px;
    padding-bottom: 16px;
  }

  /* 结构化区域间距收紧 */
  .ocr-section {
    margin-bottom: 14px;
    padding-bottom: 14px;
  }

  /* 结构化标签间距 */
  .structured-label {
    margin-bottom: 10px;
  }

  /* 复制按钮文字隐藏 */
  .copy-btn {
    font-size: 0;
  }
  .copy-btn .el-icon {
    font-size: 16px !important;
  }
}

/* 平板端：适度间距 */
@media (min-width: 768px) and (max-width: 1023px) {
  :deep(.page-section) {
    padding: 20px;
  }

  /* 标题字号适度调小 */
  .title-text {
    font-size: 18px;
  }
}
</style>
