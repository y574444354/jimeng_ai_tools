<template>
  <div class="img2img-view">
    <!-- 参考图片上传区 -->
    <div class="page-section">
      <div class="section-title">参考图片</div>
      <ImageUploader @uploaded="handleImageUploaded" @removed="handleImageRemoved" />
      <div v-if="!referenceImagePath && generationStore.isGenerating" class="upload-warning">
        请先上传参考图片
      </div>
    </div>

    <!-- 参数设置区 -->
    <div class="page-section">
      <div class="section-title">生成参数</div>

      <el-form label-position="top">
        <el-form-item label="正向提示词" required>
          <el-input
            v-model="form.prompt"
            type="textarea"
            :rows="4"
            placeholder="请输入图片描述..."
            maxlength="1000"
            show-word-limit
          />
        </el-form-item>

        <el-form-item label="负面提示词">
          <el-input
            v-model="form.negative_prompt"
            type="textarea"
            :rows="2"
            placeholder="描述不希望出现在图片中的内容..."
            maxlength="500"
            show-word-limit
          />
        </el-form-item>

        <el-form-item label="图片尺寸">
          <div class="size-chips">
            <el-radio-group v-model="form.image_size" class="size-group">
              <el-radio-button value="1024x1024" size="small">1:1 方图</el-radio-button>
              <el-radio-button value="1920x1080" size="small">16:9 横图</el-radio-button>
              <el-radio-button value="1080x1920" size="small">9:16 竖图</el-radio-button>
              <el-radio-button value="1280x960" size="small">4:3 横图</el-radio-button>
            </el-radio-group>
          </div>
        </el-form-item>

        <el-row :gutter="16">
          <el-col :span="8">
            <el-form-item label="生成数量">
              <el-select v-model="form.image_count" style="width: 100%">
                <el-option :value="1" label="1张" />
                <el-option :value="2" label="2张" />
                <el-option :value="3" label="3张" />
                <el-option :value="4" label="4张" />
              </el-select>
            </el-form-item>
          </el-col>
          <el-col :span="8">
            <el-form-item label="CFG Scale">
              <el-slider v-model="form.cfg_scale" :min="1" :max="20" :step="0.5" show-input />
            </el-form-item>
          </el-col>
          <el-col :span="8">
            <el-form-item label="随机种子">
              <el-input-number v-model="form.seed" :min="0" :max="999999999" style="width: 100%" />
            </el-form-item>
          </el-col>
        </el-row>

        <el-form-item label="图片风格">
          <el-select v-model="form.style" placeholder="默认风格" clearable style="width: 100%">
            <el-option value="写实摄影" label="写实摄影" />
            <el-option value="动漫" label="动漫" />
            <el-option value="水彩" label="水彩" />
            <el-option value="油画" label="油画" />
            <el-option value="3D渲染" label="3D渲染" />
          </el-select>
        </el-form-item>

        <el-form-item>
          <el-button
            type="primary"
            size="large"
            :loading="generationStore.isGenerating"
            :disabled="!form.prompt.trim() || !referenceImagePath"
            @click="generate"
            class="generate-btn"
          >
            {{ generationStore.isGenerating ? '生成中...' : '✨ 生成图片' }}
          </el-button>
        </el-form-item>
      </el-form>
    </div>

    <!-- 结果区 -->
    <div class="page-section" v-if="generationStore.result">
      <div class="section-title">生成结果</div>
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
import { useGenerationStore } from '@/stores/generation'
import ImageUploader from '@/components/ImageUploader.vue'
import GenerationResult from '@/components/GenerationResult.vue'
import LoadingOverlay from '@/components/LoadingOverlay.vue'

const generationStore = useGenerationStore()
const referenceImagePath = ref('')

const form = reactive({
  prompt: '',
  negative_prompt: '',
  image_size: '1024x1024',
  style: '',
  cfg_scale: 7,
  seed: 0,
  image_count: 1,
})

function handleImageUploaded(filePath: string) {
  referenceImagePath.value = filePath
}

function handleImageRemoved() {
  referenceImagePath.value = ''
}

async function generate() {
  if (!form.prompt.trim() || !referenceImagePath.value) return
  generationStore.reset()

  try {
    await generationStore.startImg2Img({
      prompt: form.prompt,
      negative_prompt: form.negative_prompt || undefined,
      image_size: form.image_size,
      style: form.style || undefined,
      cfg_scale: form.cfg_scale,
      seed: form.seed,
      image_count: form.image_count,
      reference_image_path: referenceImagePath.value,
    })
  } catch (e) {
    // Error handled in store
  }
}
</script>

<style scoped>
.upload-warning {
  color: #E6A23C;
  font-size: 13px;
  margin-top: 8px;
}

.generate-btn {
  width: 100%;
  height: 48px;
  font-size: 16px;
}
</style>