<template>
  <el-dialog
    :model-value="visible"
    @update:model-value="$emit('update:visible', $event)"
    width="420px"
    :close-on-click-modal="true"
    align-center
  >
    <template #header>
      <div class="dialog-header">
        <div class="dialog-icon danger">
          <el-icon :size="22"><WarningFilled /></el-icon>
        </div>
        <span class="dialog-title">确认删除</span>
      </div>
    </template>

    <div class="delete-confirm">
      <p class="confirm-text">确定要删除这条生成记录吗？</p>
      <p class="confirm-hint">删除后相关的图片文件也将被移除，此操作不可恢复。</p>
    </div>

    <template #footer>
      <div class="dialog-footer">
        <el-button @click="$emit('update:visible', false)" class="cancel-btn">取消</el-button>
        <el-button type="danger" @click="$emit('confirm')" class="confirm-btn">确认删除</el-button>
      </div>
    </template>
  </el-dialog>
</template>

<script setup lang="ts">
import { WarningFilled } from '@element-plus/icons-vue'

defineProps<{
  visible: boolean
}>()

defineEmits<{
  'update:visible': [value: boolean]
  'confirm': []
}>()
</script>

<style scoped>
.dialog-header {
  display: flex;
  align-items: center;
  gap: 10px;
}

.dialog-icon {
  width: 36px;
  height: 36px;
  border-radius: var(--radius-full);
  display: flex;
  align-items: center;
  justify-content: center;
}

.dialog-icon.danger {
  background: var(--danger-bg);
  color: var(--danger);
}

.dialog-title {
  font-size: 16px;
  font-weight: 700;
  color: var(--text-primary);
}

.delete-confirm {
  padding: 8px 0;
}

.confirm-text {
  font-size: 15px;
  color: var(--text-primary);
  margin-bottom: 8px;
}

.confirm-hint {
  font-size: 13px;
  color: var(--text-secondary);
  line-height: 1.5;
}

.dialog-footer {
  display: flex;
  justify-content: flex-end;
  gap: 12px;
}

.cancel-btn {
  font-weight: 500;
}

.confirm-btn {
  font-weight: 600;
}
</style>
