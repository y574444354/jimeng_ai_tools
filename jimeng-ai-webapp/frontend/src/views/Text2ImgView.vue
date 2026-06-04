<template>
  <div class="text2img-view">
    <!-- 参数设置区 -->
    <div class="page-section">
      <div class="section-title">
        <el-icon :size="18"><Setting /></el-icon>
        生成参数
      </div>

      <el-form label-position="top">
        <el-form-item label="正向提示词" required>
          <div class="prompt-input-wrapper">
            <el-input
              v-model="form.prompt"
              type="textarea"
              :rows="4"
              placeholder="请输入图片描述（支持中文和英文）..."
              maxlength="1000"
              show-word-limit
            />
            <div class="prompt-actions">
              <el-dropdown @command="handleOptimize" trigger="click">
                <el-button
                  type="primary"
                  plain
                  size="small"
                  :loading="optimizing"
                  :disabled="!form.prompt.trim()"
                >
                  <el-icon :size="14"><MagicStick /></el-icon>
                  AI 优化
                  <el-icon :size="12"><ArrowDown /></el-icon>
                </el-button>
                <template #dropdown>
                  <el-dropdown-menu>
                    <el-dropdown-item command="optimize">
                      <el-icon><MagicStick /></el-icon>
                      智能优化
                      <div class="dropdown-desc">补充细节，提升画质</div>
                    </el-dropdown-item>
                    <el-dropdown-item command="expand">
                      <el-icon><Document /></el-icon>
                      场景扩写
                      <div class="dropdown-desc">展开叙事，丰富场景</div>
                    </el-dropdown-item>
                    <el-dropdown-item command="translate">
                      <el-icon><Connection /></el-icon>
                      翻译英文
                      <div class="dropdown-desc">中译英，适配生图</div>
                    </el-dropdown-item>
                  </el-dropdown-menu>
                </template>
              </el-dropdown>
            </div>
          </div>
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
          <el-radio-group v-model="form.image_size" class="size-group">
            <el-radio-button value="1024x1024">1:1 方图</el-radio-button>
            <el-radio-button value="1920x1080">16:9 横图</el-radio-button>
            <el-radio-button value="1080x1920">9:16 竖图</el-radio-button>
            <el-radio-button value="1280x960">4:3 横图</el-radio-button>
          </el-radio-group>
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

        <el-form-item>
          <el-button
            type="primary"
            size="large"
            :loading="generationStore.isGenerating"
            :disabled="!form.prompt.trim()"
            @click="generate"
            class="generate-btn"
          >
            <el-icon v-if="!generationStore.isGenerating" :size="18"><MagicStick /></el-icon>
            {{ generationStore.isGenerating ? 'AI 生成中...' : '开始生成' }}
          </el-button>
        </el-form-item>
      </el-form>
    </div>

    <!-- 生成结果区 -->
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
import { reactive } from 'vue'
import { Setting, MagicStick, PictureFilled, ArrowDown, Document, Connection } from '@element-plus/icons-vue'
import { useGenerationStore } from '@/stores/generation'
import GenerationResult from '@/components/GenerationResult.vue'
import LoadingOverlay from '@/components/LoadingOverlay.vue'
import { usePromptOptimize } from '@/composables/usePromptOptimize'

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

const { optimizing, handleOptimize } = usePromptOptimize(
  () => form.prompt,
  (v) => { form.prompt = v },
  () => form.style || undefined,
)

async function generate() {
  console.log('[DEBUG] generate() 被调用, prompt=', form.prompt)
  if (!form.prompt.trim()) return
  generationStore.reset()
  console.log('[DEBUG] reset完成, 准备调用 startText2Img')

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
    console.log('[DEBUG] startText2Img 完成')
  } catch (e) {
    console.error('[DEBUG] startText2Img 失败:', e)
  }
}
</script>

<style scoped>
.text2img-view {
  animation: fadeInUp 0.35s cubic-bezier(0.4, 0, 0.2, 1);
}

.prompt-input-wrapper {
  width: 100%;
}

.prompt-actions {
  display: flex;
  justify-content: flex-end;
  margin-top: 8px;
  gap: 8px;
}

.dropdown-desc {
  font-size: 11px;
  color: var(--el-text-color-secondary);
  margin-top: 2px;
}

.size-group {
  display: flex;
  gap: 6px;
  flex-wrap: wrap;
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

.generate-btn:active {
  transform: translateY(0);
}

.result-section {
  animation: fadeInUp 0.4s cubic-bezier(0.4, 0, 0.2, 1);
}
</style>
