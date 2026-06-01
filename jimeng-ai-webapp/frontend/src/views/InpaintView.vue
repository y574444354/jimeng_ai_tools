<template>
  <div class="inpaint-view">
    <!-- 画布上传区 -->
    <div class="page-section">
      <div class="section-title">
        <el-icon :size="18"><EditPen /></el-icon>
        上传图片并标记重绘区域
      </div>
      <InpaintCanvas ref="inpaintCanvasRef" @mask-ready="handleMaskReady" />
    </div>

    <!-- 参数设置区 -->
    <div class="page-section">
      <div class="section-title">
        <el-icon :size="18"><Setting /></el-icon>
        生成参数
      </div>

      <el-form label-position="top">
        <el-form-item label="描述提示词" required>
          <el-input
            v-model="form.prompt"
            type="textarea"
            :rows="4"
            placeholder="描述要重绘的区域内容..."
            maxlength="1000"
            show-word-limit
          />
        </el-form-item>

        <el-form-item label="负面提示词">
          <el-input
            v-model="form.negative_prompt"
            type="textarea"
            :rows="2"
            placeholder="描述不希望出现的内容..."
            maxlength="500"
            show-word-limit
          />
        </el-form-item>

        <el-row :gutter="16">
          <el-col :span="12">
            <el-form-item label="CFG Scale">
              <el-slider v-model="form.cfg_scale" :min="1" :max="20" :step="0.5" show-input />
            </el-form-item>
          </el-col>
          <el-col :span="12">
            <el-form-item label="随机种子">
              <el-input-number v-model="form.seed" :min="0" :max="999999999" style="width: 100%" />
            </el-form-item>
          </el-col>
        </el-row>

        <el-form-item>
          <el-button
            type="primary"
            size="large"
            :loading="generationStore.isGenerating"
            :disabled="!form.prompt.trim() || !imageReady"
            @click="generate"
            class="generate-btn"
          >
            <el-icon v-if="!generationStore.isGenerating" :size="18"><MagicStick /></el-icon>
            {{ generationStore.isGenerating ? 'AI 重绘中...' : '开始重绘' }}
          </el-button>
        </el-form-item>
      </el-form>
    </div>

    <!-- 结果区 -->
    <div class="page-section result-section" v-if="generationStore.result">
      <div class="section-title">
        <el-icon :size="18"><PictureFilled /></el-icon>
        生成结果
      </div>
      <GenerationResult :images="generationStore.result.images || []" />
    </div>

    <el-alert
      v-if="generationStore.error"
      :title="generationStore.error"
      type="error"
      show-icon
      closable
      @close="generationStore.reset()"
    />

    <LoadingOverlay
      :visible="generationStore.isGenerating"
      :status="generationStore.currentStatus"
    />
  </div>
</template>

<script setup lang="ts">
import { reactive, ref } from 'vue'
import { Setting, MagicStick, PictureFilled, EditPen } from '@element-plus/icons-vue'
import { useGenerationStore } from '@/stores/generation'
import InpaintCanvas from '@/components/InpaintCanvas.vue'
import GenerationResult from '@/components/GenerationResult.vue'
import LoadingOverlay from '@/components/LoadingOverlay.vue'

const generationStore = useGenerationStore()
const inpaintCanvasRef = ref<InstanceType<typeof InpaintCanvas> | null>(null)
const imageReady = ref(false)
const originalImagePath = ref('')
const maskImagePath = ref('')

const form = reactive({
  prompt: '',
  negative_prompt: '',
  cfg_scale: 7,
  seed: 0,
})

function handleMaskReady(path: string) {
  maskImagePath.value = path
  imageReady.value = true
  originalImagePath.value = inpaintCanvasRef.value?.getOriginalImagePath() || ''
}

async function generate() {
  if (!form.prompt.trim() || !imageReady.value) return
  generationStore.reset()

  try {
    const canvas = inpaintCanvasRef.value
    if (!canvas) return

    const maskDataUrl = canvas.getMaskDataUrl()
    const blob = await (await fetch(maskDataUrl)).blob()
    const file = new File([blob], 'mask.png', { type: 'image/png' })
    const { uploadImage } = await import('@/api/upload')
    const uploadRes = await uploadImage(file)
    const maskPath = uploadRes.data.file_path

    await generationStore.startInpainting({
      prompt: form.prompt,
      negative_prompt: form.negative_prompt || undefined,
      image_size: '1024x1024',
      cfg_scale: form.cfg_scale,
      seed: form.seed,
      image_count: 1,
      reference_image_path: originalImagePath.value,
      mask_image_path: maskPath,
    })
  } catch (e) {
    // Error handled in store
  }
}
</script>

<style scoped>
.inpaint-view {
  animation: fadeInUp 0.35s cubic-bezier(0.4, 0, 0.2, 1);
}

.generate-btn {
  width: 100%;
  height: 52px;
  font-size: 16px;
  font-weight: 700;
  letter-spacing: 0.04em;
  border-radius: var(--radius-md);
  background: var(--primary-gradient) !important;
  border: none !important;
  transition: all var(--transition-base);
}

.generate-btn:hover {
  box-shadow: 0 6px 20px rgba(99, 102, 241, 0.4);
  transform: translateY(-2px);
}

.result-section {
  animation: fadeInUp 0.4s cubic-bezier(0.4, 0, 0.2, 1);
}
</style>
