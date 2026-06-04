<template>
  <div class="settings-page">
    <div class="page-header">
      <h2 class="page-title">系统设置</h2>
      <p class="page-desc">管理 AI 模型连接配置，支持 OpenAI 兼容 API</p>
    </div>

    <div class="section">
      <div class="section-header">
        <h3>AI 模型配置</h3>
        <el-button type="primary" :icon="Plus" @click="openCreateDialog">添加配置</el-button>
      </div>

      <el-table :data="store.configs" v-loading="store.loading" stripe class="config-table">
        <el-table-column prop="name" label="名称" min-width="120" />
        <el-table-column prop="api_base_url" label="API 地址" min-width="200" show-overflow-tooltip />
        <el-table-column prop="model_name" label="模型" min-width="120" />
        <el-table-column prop="api_key" label="密钥" width="120">
          <template #default="{ row }">{{ row.api_key || '****' }}</template>
        </el-table-column>
        <el-table-column label="状态" width="80" align="center">
          <template #default="{ row }">
            <el-tag :type="row.is_active ? 'success' : 'info'" size="small">
              {{ row.is_active ? '激活' : '未激活' }}
            </el-tag>
          </template>
        </el-table-column>
        <el-table-column label="参数" width="140">
          <template #default="{ row }">
            <span class="param-text">T={{ row.temperature }} / {{ row.max_tokens }}t</span>
          </template>
        </el-table-column>
        <el-table-column label="操作" width="280" fixed="right">
          <template #default="{ row }">
            <el-button text type="primary" size="small" @click="openEditDialog(row)">编辑</el-button>
            <el-button text type="success" size="small" @click="handleActivate(row)" :disabled="row.is_active">
              激活
            </el-button>
            <el-button text type="warning" size="small" @click="handleTest(row)">测试</el-button>
            <el-popconfirm title="确定删除此配置？" @confirm="handleDelete(row.id)">
              <template #reference>
                <el-button text type="danger" size="small">删除</el-button>
              </template>
            </el-popconfirm>
          </template>
        </el-table-column>
      </el-table>
    </div>

    <!-- 添加/编辑弹窗 -->
    <el-dialog
      v-model="dialogVisible"
      :title="isEditing ? '编辑配置' : '添加配置'"
      width="560px"
      destroy-on-close
    >
      <el-form ref="formRef" :model="form" :rules="formRules" label-width="100px" label-position="left">
        <el-form-item label="配置名称" prop="name">
          <el-input v-model="form.name" placeholder="如：DeepSeek、OpenAI" maxlength="100" />
        </el-form-item>
        <el-form-item label="API 地址" prop="api_base_url">
          <el-input v-model="form.api_base_url" placeholder="https://api.openai.com/v1" maxlength="500" />
        </el-form-item>
        <el-form-item label="模型名称" prop="model_name">
          <el-input v-model="form.model_name" placeholder="gpt-4o / deepseek-chat" maxlength="100" />
        </el-form-item>
        <el-form-item label="API 密钥" prop="api_key">
          <el-input
            v-model="form.api_key"
            type="password"
            show-password
            :placeholder="isEditing ? '留空则不修改密钥' : 'sk-...'"
            maxlength="500"
          />
        </el-form-item>
        <el-form-item label="温度参数">
          <el-slider v-model="form.temperature" :min="0" :max="2" :step="0.1" show-input />
        </el-form-item>
        <el-form-item label="最大 Token">
          <el-input-number v-model="form.max_tokens" :min="1" :max="128000" :step="1024" />
        </el-form-item>
      </el-form>
      <template #footer>
        <el-button @click="dialogVisible = false">取消</el-button>
        <el-button type="primary" :loading="submitting" @click="handleSubmit">
          {{ isEditing ? '保存' : '创建' }}
        </el-button>
      </template>
    </el-dialog>

    <!-- 测试连接弹窗 -->
    <el-dialog v-model="testDialogVisible" title="测试连接" width="480px" destroy-on-close @closed="onTestDialogClosed">
      <el-form label-width="80px" label-position="left">
        <el-form-item label="API 地址">
          <el-input :model-value="testTarget.api_base_url" disabled />
        </el-form-item>
        <el-form-item label="模型名称">
          <el-input :model-value="testTarget.model_name" disabled />
        </el-form-item>
        <el-form-item label="API 密钥" required>
          <el-input
            v-model="testApiKey"
            type="password"
            show-password
            placeholder="请输入完整密钥进行测试"
            maxlength="500"
            @keyup.enter="handleDoTest"
          />
        </el-form-item>
      </el-form>
      <div class="test-result" v-if="store.testResult">
        <el-alert
          :type="store.testResult.ok ? 'success' : 'error'"
          :title="store.testResult.ok ? '连接成功' : '连接失败'"
          :closable="false"
          show-icon
        >
          <template v-if="store.testResult.ok">
            <p>模型：{{ store.testResult.model }}</p>
            <p>延迟：{{ store.testResult.latency_ms }}ms</p>
            <p v-if="store.testResult.reply_preview">响应预览：{{ store.testResult.reply_preview }}</p>
          </template>
          <template v-else>
            <p>{{ store.testResult.error }}</p>
          </template>
        </el-alert>
      </div>
      <p v-else-if="store.testLoading" style="text-align:center;color:var(--text-secondary);">
        正在测试...
      </p>
      <template #footer>
        <el-button @click="testDialogVisible = false">关闭</el-button>
        <el-button type="primary" :loading="store.testLoading" :disabled="!testApiKey" @click="handleDoTest">
          开始测试
        </el-button>
      </template>
    </el-dialog>
  </div>
</template>

<script setup lang="ts">
import { ref, reactive, computed, onMounted } from 'vue'
import { Plus } from '@element-plus/icons-vue'
import { ElMessage } from 'element-plus'
import { useSettingsStore } from '@/stores/settings'
import type { AIConfigItem, AIConfigForm } from '@/api/settings'
import type { FormInstance, FormRules } from 'element-plus'

const store = useSettingsStore()

// 表单
const dialogVisible = ref(false)
const isEditing = ref(false)
const editingId = ref('')
const submitting = ref(false)
const formRef = ref<FormInstance>()

const defaultForm: AIConfigForm = {
  name: '',
  api_base_url: '',
  model_name: '',
  api_key: '',
  temperature: 0.7,
  max_tokens: 4096,
}

const form = reactive<AIConfigForm>({ ...defaultForm })

const formRules = computed<FormRules>(() => ({
  name: [{ required: true, message: '请输入配置名称', trigger: 'blur' }],
  api_base_url: [{ required: true, message: '请输入 API 地址', trigger: 'blur' }],
  model_name: [{ required: true, message: '请输入模型名称', trigger: 'blur' }],
  api_key: isEditing.value
    ? []
    : [{ required: true, message: '请输入 API 密钥', trigger: 'blur' }],
}))

// 测试连接
const testDialogVisible = ref(false)
const testApiKey = ref('')
const testTarget = reactive({ api_base_url: '', model_name: '' })

function handleTest(row: AIConfigItem) {
  store.testResult = null
  testApiKey.value = ''
  testTarget.api_base_url = row.api_base_url
  testTarget.model_name = row.model_name
  testDialogVisible.value = true
}

function onTestDialogClosed() {
  store.testResult = null
  testApiKey.value = ''
}

async function handleDoTest() {
  if (!testApiKey.value) return
  await store.testConnection({
    api_base_url: testTarget.api_base_url,
    model_name: testTarget.model_name,
    api_key: testApiKey.value,
  })
}

// 生命周期
onMounted(() => {
  store.fetchConfigs()
})

// 新建/编辑弹窗
function openCreateDialog() {
  isEditing.value = false
  editingId.value = ''
  Object.assign(form, defaultForm)
  dialogVisible.value = true
}

function openEditDialog(row: AIConfigItem) {
  isEditing.value = true
  editingId.value = row.id
  form.name = row.name
  form.api_base_url = row.api_base_url
  form.model_name = row.model_name
  form.api_key = '' // 编辑时不回填密钥，留空表示不修改
  form.temperature = row.temperature
  form.max_tokens = row.max_tokens
  dialogVisible.value = true
}

async function handleSubmit() {
  if (!formRef.value) return
  const valid = await formRef.value.validate().catch(() => false)
  if (!valid) return

  submitting.value = true
  try {
    if (isEditing.value) {
      // 编辑时如果密钥为空则排除该字段，表示不修改密钥
      const { api_key, ...rest } = form
      const payload = api_key ? form : rest
      await store.editConfig(editingId.value, payload)
      ElMessage.success('配置更新成功')
    } else {
      await store.addConfig({ ...form })
      ElMessage.success('配置创建成功')
    }
    dialogVisible.value = false
  } catch (e: any) {
    ElMessage.error(e?.message || '操作失败')
  } finally {
    submitting.value = false
  }
}

async function handleActivate(row: AIConfigItem) {
  try {
    await store.setActive(row.id)
    ElMessage.success(`已激活配置: ${row.name}`)
  } catch (e: any) {
    ElMessage.error(e?.message || '激活失败')
  }
}

async function handleDelete(id: string) {
  try {
    await store.removeConfig(id)
    ElMessage.success('配置已删除')
  } catch (e: any) {
    ElMessage.error(e?.message || '删除失败')
  }
}
</script>

<style scoped>
.settings-page {
  max-width: 960px;
}

.page-header {
  margin-bottom: 24px;
}

.page-title {
  font-size: 22px;
  font-weight: 700;
  color: var(--text-primary);
  margin-bottom: 6px;
}

.page-desc {
  font-size: 13px;
  color: var(--text-secondary);
}

.section {
  background: #fff;
  border-radius: var(--radius-lg);
  padding: 20px;
  box-shadow: 0 1px 3px rgba(0, 0, 0, 0.04);
}

.section-header {
  display: flex;
  align-items: center;
  justify-content: space-between;
  margin-bottom: 16px;
}

.section-header h3 {
  font-size: 16px;
  font-weight: 600;
  color: var(--text-primary);
}

.config-table {
  margin-top: 8px;
}

.param-text {
  font-size: 12px;
  color: var(--text-secondary);
  white-space: nowrap;
}

.test-result {
  padding: 12px 0;
}

.test-result p {
  margin: 4px 0;
  font-size: 13px;
}

/* ======== 响应式 ======== */
@media (max-width: 767px) {
  .settings-page {
    max-width: 100%;
    padding: 0 4px;
  }
  .section {
    padding: 12px;
    border-radius: var(--radius-md);
  }
  .section-header {
    flex-direction: column;
    align-items: flex-start;
    gap: 10px;
  }
  .config-table {
    display: block;
    overflow-x: auto;
    -webkit-overflow-scrolling: touch;
  }
  .config-table :deep(.el-table__body-wrapper) {
    overflow-x: auto;
  }
  .config-table :deep(.el-table) {
    min-width: 700px;
  }
  .page-title {
    font-size: 18px;
  }
}

@media (min-width: 768px) and (max-width: 1023px) {
  .settings-page {
    max-width: 100%;
    padding: 0 12px;
  }
}
</style>
