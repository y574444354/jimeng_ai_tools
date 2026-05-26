<template>
  <div class="text2img-view">
    <!-- 参数设置区 -->
    <div class="page-section">
      <div class="section-title">生成参数</div>

      <el-form label-position="top">
        <!-- 正向提示词 -->
        <el-form-item label="正向提示词" required>
          <el-input
            v-model="form.prompt"
            type="textarea"
            :rows="4"
            placeholder="请输入图片描述（支持中文和英文）..."
            maxlength="1000"
            show-word-limit
          />
        </el-form-item>

        <!-- 负面提示词 -->
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

        <!-- 图片尺寸 -->
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

        <!-- 参数行 -->
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
            <el-form-item label="CFG Scale (提示词相关性)">
              <el-slider
                v-model="form.cfg_scale"
                :min="1"
                :max="20"
                :step="0.5"
                show-input
              />
            </el-form-item>
          </el-col>
          <el-col :span="8">
            <el-form-item label="随机种子 (0=随机)">
              <el-input-number
                v-model="form.seed"
                :min="0"
                :max="999999999"
                style="width: 100%"
              />
            </el-form-item>
          </el-col>
        </el-row>

        <!-- 风格选择 -->
        <el-form-item label="图片风格">
          <el-select v-model="form.style" placeholder="不选择（默认风格）" clearable style="width: 100%">
            <el-option value="写实摄影" label="写实摄影" />
            <el-option value="动漫" label="动漫" />
            <el-option value="水彩" label="水彩" />
            <el-option value="油画" label="油画" />
            <el-option value="3D渲染" label="3D渲染" />
            <el-option value="水墨画" label="水墨画" />
            <el-option value="素描" label="素描" />
            <el-option value="赛博朋克" label="赛博朋克" />
          </el-select>
        </el-form-item>

        <!-- 生成按钮 -->
        <el-form-item>
          <el-button
            type="primary"
            size="large"
            :loading="generationStore.isGenerating"
            :disabled="!form.prompt.trim()"
            @click="generate"
            class="generate-btn"
          >
            {{ generationStore.isGenerating ? '生成中...' : '✨ 生成图片' }}
          </el-button>
        </el-form-item>
      </el-form>
    </div>

    <!-- 生成结果区 -->
    <div class="page-section" v-if="generationStore.result">
      <div class="section-title">生成结果</div>
      <GenerationResult :images="generationStore.result.images || []" />
    </div>

    <!-- 错误提示 -->
    <el-alert
      v-if="generationStore.error"
      :title="generationStore.error"
      type="error"
      show-icon
      closable
      @close="generationStore.reset()"
    />

    <!-- 加载遮罩 -->
    <LoadingOverlay
      :visible="generationStore.isGenerating"
      :status="generationStore.currentStatus"
    />
  </div>
</template>

<script setup lang="ts">
import { reactive, onMounted } from 'vue'
import { useGenerationStore } from '@/stores/generation'
import GenerationResult from '@/components/GenerationResult.vue'
import LoadingOverlay from '@/components/LoadingOverlay.vue'

const generationStore = useGenerationStore()

const form = reactive({
  prompt: '',
  negative_prompt: '',
  image_size: '1024x1024',
  style: '',
  cfg_scale: 7,
  seed: 0,
  image_count: 1,
})

async function generate() {
  if (!form.prompt.trim()) return
  generationStore.reset()

  try {
    await generationStore.startText2Img({
      prompt: form.prompt,
      negative_prompt: form.negative_prompt || undefined,
      image_size: form.image_size,
      style: form.style || undefined,
      cfg_scale: form.cfg_scale,
      seed: form.seed,
      image_count: form.image_count,
    })
  } catch (e) {
    // 错误已自动处理
  }
}
</script>

<style scoped>
.size-chips {
  width: 100%;
}

.size-group {
  display: flex;
  gap: 8px;
}

.generate-btn {
  width: 100%;
  height: 48px;
  font-size: 16px;
}
</style>