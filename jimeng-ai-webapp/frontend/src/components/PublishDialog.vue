<template>
  <el-dialog
    :model-value="visible"
    title="发布到小红书"
    width="520px"
    @update:model-value="$emit('update:visible', $event)"
    @open="onOpen"
  >
    <el-form label-position="top">
      <el-form-item label="发布标题">
        <el-input
          v-model="publishTitle"
          placeholder="可自定义发布标题（默认使用文章标题）"
          maxlength="20"
          show-word-limit
        />
      </el-form-item>

      <el-form-item label="选择平台账号">
        <el-select v-model="selectedAccount" placeholder="选择已授权的小红书账号" style="width: 100%">
          <el-option
            v-for="acc in publishStore.accounts"
            :key="acc.id"
            :label="acc.account_name"
            :value="acc.id"
            :disabled="!acc.is_active"
          />
        </el-select>
        <div v-if="publishStore.accounts.length === 0" class="no-accounts">
          暂无账号，请在发布中心添加授权账号
        </div>
      </el-form-item>

      <el-form-item label="配图选择">
        <div class="image-pick-area">
          <div
            v-for="(img, idx) in selectedImages"
            :key="idx"
            class="picked-image"
            @click="removeImage(idx)"
          >
            <img :src="img" alt="" />
            <div class="remove-overlay">
              <el-icon :size="16"><Close /></el-icon>
            </div>
          </div>
          <div
            v-if="selectedImages.length < 9"
            class="add-image-btn"
            @click="showImagePicker = true"
          >
            <el-icon :size="24"><Plus /></el-icon>
            <span>添加</span>
          </div>
        </div>
      </el-form-item>

      <el-form-item label="发布标签">
        <el-input
          v-model="tagInput"
          placeholder="输入标签后按回车添加"
          @keyup.enter="addTag"
        />
        <div class="tag-list" v-if="publishTags.length > 0">
          <el-tag
            v-for="(t, i) in publishTags"
            :key="i"
            size="small"
            closable
            @close="publishTags.splice(i, 1)"
          >{{ t }}</el-tag>
        </div>
      </el-form-item>
    </el-form>

    <template #footer>
      <el-button @click="$emit('update:visible', false)">取消</el-button>
      <el-button
        type="primary"
        :loading="publishing"
        :disabled="!selectedAccount"
        @click="doPublish"
      >
        {{ publishing ? '发布中...' : '确认发布' }}
      </el-button>
    </template>

    <!-- 图片选择器 -->
    <el-dialog
      v-model="showImagePicker"
      title="选择配图"
      width="640px"
      append-to-body
    >
      <ImagePicker
        v-model="selectedImages"
        @close="showImagePicker = false"
      />
    </el-dialog>
  </el-dialog>
</template>

<script setup lang="ts">
import { ref } from 'vue'
import { Plus, Close } from '@element-plus/icons-vue'
import { usePublishStore } from '@/stores/publish'
import ImagePicker from '@/components/ImagePicker.vue'
import { ElMessage } from 'element-plus'

const props = defineProps<{
  visible: boolean
  articleId: string
  articleTitle: string
}>()

const emit = defineEmits<{
  (e: 'update:visible', value: boolean): void
}>()

const publishStore = usePublishStore()

const publishTitle = ref('')
const selectedAccount = ref('')
const selectedImages = ref<string[]>([])
const publishTags = ref<string[]>([])
const tagInput = ref('')
const publishing = ref(false)
const showImagePicker = ref(false)

function onOpen() {
  publishTitle.value = props.articleTitle
  selectedImages.value = []
  publishTags.value = []
  // 加载平台账号
  publishStore.fetchAccounts('xiaohongshu')
}

function addTag() {
  const tag = tagInput.value.trim()
  if (tag && !publishTags.value.includes(tag)) {
    publishTags.value.push(tag)
  }
  tagInput.value = ''
}

function removeImage(idx: number) {
  selectedImages.value.splice(idx, 1)
}

async function doPublish() {
  if (!props.articleId || !selectedAccount.value) return
  publishing.value = true
  try {
    await publishStore.publishToXHS({
      article_id: props.articleId,
      platform_account_id: selectedAccount.value,
      title: publishTitle.value || undefined,
      images: selectedImages.value,
      tags: publishTags.value,
    })
    ElMessage.success('发布已提交')
    emit('update:visible', false)
  } catch (e: any) {
    ElMessage.error(e.message || '发布失败')
  } finally {
    publishing.value = false
  }
}
</script>

<style scoped>
.image-pick-area {
  display: flex;
  flex-wrap: wrap;
  gap: 8px;
}

.picked-image {
  width: 72px;
  height: 72px;
  border-radius: var(--radius-sm);
  overflow: hidden;
  position: relative;
  cursor: pointer;
}

.picked-image img {
  width: 100%;
  height: 100%;
  object-fit: cover;
}

.remove-overlay {
  position: absolute;
  inset: 0;
  background: rgba(0, 0, 0, 0.4);
  display: flex;
  align-items: center;
  justify-content: center;
  color: white;
  opacity: 0;
  transition: opacity var(--transition-fast);
}

.picked-image:hover .remove-overlay {
  opacity: 1;
}

.add-image-btn {
  width: 72px;
  height: 72px;
  border: 2px dashed var(--border-base);
  border-radius: var(--radius-sm);
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  color: var(--text-placeholder);
  cursor: pointer;
  font-size: 11px;
  gap: 2px;
  transition: all var(--transition-fast);
}

.add-image-btn:hover {
  border-color: var(--primary);
  color: var(--primary);
}

.tag-list {
  display: flex;
  flex-wrap: wrap;
  gap: 6px;
  margin-top: 8px;
}

.no-accounts {
  font-size: 12px;
  color: var(--text-placeholder);
  padding: 8px 0;
}

/* ======== 响应式 ======== */
@media (max-width: 767px) {
  :deep(.el-dialog) {
    width: 95% !important;
  }
  .image-pick-area {
    gap: 6px;
  }
  .picked-image {
    width: 60px;
    height: 60px;
  }
  .add-image-btn {
    width: 60px;
    height: 60px;
  }
}
</style>
