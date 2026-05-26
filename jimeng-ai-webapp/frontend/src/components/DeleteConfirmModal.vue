<template>
  <el-dialog
    :model-value="visible"
    @update:model-value="$emit('update:visible', $event)"
    title="确认删除"
    width="400px"
    :close-on-click-modal="true"
  >
    <div class="delete-confirm">
      <div class="confirm-icon">⚠️</div>
      <div class="confirm-text">
        确定要删除这条生成记录吗？<br />
        <span class="confirm-hint">删除后相关的图片文件也将被移除，此操作不可恢复。</span>
      </div>
    </div>

    <template #footer>
      <el-button @click="$emit('update:visible', false)">取消</el-button>
      <el-button type="danger" @click="$emit('confirm')">确认删除</el-button>
    </template>
  </el-dialog>
</template>

<script setup lang="ts">
defineProps<{
  visible: boolean
}>()

defineEmits<{
  'update:visible': [value: boolean]
  'confirm': []
}>()
</script>

<style scoped>
.delete-confirm {
  text-align: center;
  padding: 16px 0;
}

.confirm-icon {
  font-size: 48px;
  margin-bottom: 16px;
}

.confirm-text {
  font-size: 15px;
  color: #303133;
  line-height: 1.6;
}

.confirm-hint {
  font-size: 13px;
  color: #909399;
}
</style>