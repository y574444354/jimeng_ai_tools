<template>
  <div class="publish-center-view">
    <div class="page-section">
      <div class="section-title">
        <div class="title-row">
          <span class="title-left">
            <el-icon :size="18"><Promotion /></el-icon>
            发布中心
          </span>
          <el-button size="small" @click="loadData">
            <el-icon :size="14"><Refresh /></el-icon>
            刷新
          </el-button>
        </div>
      </div>

      <!-- Tab 切换 -->
      <el-tabs v-model="activeTab" @tab-change="loadData">
        <el-tab-pane label="发布记录" name="records" />
        <el-tab-pane label="平台账号" name="accounts" />
      </el-tabs>

      <!-- ==== 发布记录 ==== -->
      <div v-if="activeTab === 'records'">
        <div v-if="publishStore.records.length === 0" class="empty-state">
          <el-icon :size="48"><FolderOpened /></el-icon>
          <p>暂无发布记录</p>
        </div>

        <div v-else class="records-list">
          <div v-for="r in publishStore.records" :key="r.id" class="record-item">
            <div class="record-info">
              <div class="record-platform">
                <el-tag :type="r.platform === 'xiaohongshu' ? 'danger' : 'info'" size="small">
                  {{ r.platform === 'xiaohongshu' ? '小红书' : r.platform }}
                </el-tag>
                <span class="record-title">{{ r.article_title || '-' }}</span>
              </div>
              <div class="record-meta">
                <span class="meta-text" v-if="r.published_at">{{ formatTime(r.published_at) }}</span>
                <el-tag :type="recordStatusType(r.status)" size="small" effect="plain">
                  {{ recordStatusLabel(r.status) }}
                </el-tag>
              </div>
              <div v-if="r.error_message" class="record-error">{{ r.error_message }}</div>
            </div>
            <div class="record-action">
              <a v-if="r.publish_url" :href="r.publish_url" target="_blank" class="view-link">查看</a>
            </div>
          </div>
        </div>

        <div class="pagination-wrapper" v-if="publishStore.total > 20">
          <el-pagination layout="prev, pager, next" :total="publishStore.total" background />
        </div>
      </div>

      <!-- ==== 平台账号 ==== -->
      <div v-if="activeTab === 'accounts'">
        <div style="margin-bottom: 16px">
          <el-button type="primary" size="small" @click="showAddAccount = true">
            <el-icon :size="14"><Plus /></el-icon>
            添加账号
          </el-button>
        </div>

        <div v-if="publishStore.accounts.length === 0" class="empty-state">
          <el-icon :size="48"><User /></el-icon>
          <p>暂无平台账号</p>
          <p class="sub">添加小红书开放平台账号授权</p>
        </div>

        <div v-else class="accounts-list">
          <div v-for="acc in publishStore.accounts" :key="acc.id" class="account-item">
            <div class="account-info">
              <span class="account-platform">
                <el-tag type="danger" size="small">小红书</el-tag>
              </span>
              <span class="account-name">{{ acc.account_name }}</span>
              <el-tag :type="acc.is_active ? 'success' : 'info'" size="small" effect="plain">
                {{ acc.is_active ? '已激活' : '已禁用' }}
              </el-tag>
            </div>
            <el-button size="small" type="danger" text @click="removeAccount(acc.id)">
              <el-icon :size="14"><Delete /></el-icon>
            </el-button>
          </div>
        </div>

        <!-- 添加账号对话框 -->
        <el-dialog v-model="showAddAccount" title="添加平台账号" width="460px">
          <el-form label-position="top">
            <el-form-item label="平台">
              <el-select v-model="newAccount.platform" style="width: 100%">
                <el-option label="小红书" value="xiaohongshu" />
              </el-select>
            </el-form-item>
            <el-form-item label="账号昵称">
              <el-input v-model="newAccount.account_name" placeholder="输入账号昵称" />
            </el-form-item>
            <el-form-item label="Access Token">
              <el-input v-model="newAccount.access_token" type="textarea" :rows="3" placeholder="输入小红书OAuth授权后的Access Token" />
            </el-form-item>
          </el-form>
          <template #footer>
            <el-button @click="showAddAccount = false">取消</el-button>
            <el-button type="primary" :loading="adding" @click="doAddAccount">确认添加</el-button>
          </template>
        </el-dialog>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, onMounted } from 'vue'
import { Promotion, Refresh, FolderOpened, Plus, User, Delete } from '@element-plus/icons-vue'
import { usePublishStore } from '@/stores/publish'
import { ElMessage } from 'element-plus'

const publishStore = usePublishStore()
const activeTab = ref('records')
const showAddAccount = ref(false)
const adding = ref(false)

const newAccount = ref({
  platform: 'xiaohongshu',
  account_name: '',
  access_token: '',
})

function recordStatusType(status: string): 'success' | 'danger' | 'warning' | 'info' {
  const map: Record<string, 'success' | 'danger' | 'warning' | 'info'> = {
    published: 'success',
    failed: 'danger',
    pending: 'warning',
  }
  return map[status] || 'info'
}

function recordStatusLabel(status: string): string {
  const map: Record<string, string> = {
    pending: '待发布',
    published: '已发布',
    failed: '失败',
  }
  return map[status] || status
}

function formatTime(timeStr?: string): string {
  if (!timeStr) return ''
  const d = new Date(timeStr)
  return `${d.getFullYear()}-${String(d.getMonth() + 1).padStart(2, '0')}-${String(d.getDate()).padStart(2, '0')} ${String(d.getHours()).padStart(2, '0')}:${String(d.getMinutes()).padStart(2, '0')}`
}

async function loadData() {
  if (activeTab.value === 'records') {
    await publishStore.fetchRecords()
  } else {
    await publishStore.fetchAccounts()
  }
}

async function doAddAccount() {
  if (!newAccount.value.account_name || !newAccount.value.access_token) {
    ElMessage.warning('请填写完整信息')
    return
  }
  adding.value = true
  try {
    await publishStore.addAccount({
      platform: newAccount.value.platform,
      account_name: newAccount.value.account_name,
      access_token: newAccount.value.access_token,
    })
    ElMessage.success('账号添加成功')
    showAddAccount.value = false
    newAccount.value = { platform: 'xiaohongshu', account_name: '', access_token: '' }
  } catch (e: any) {
    ElMessage.error(e.message || '添加失败')
  } finally {
    adding.value = false
  }
}

async function removeAccount(id: string) {
  try {
    await publishStore.removeAccount(id)
    ElMessage.success('账号已删除')
  } catch (e: any) {
    ElMessage.error(e.message || '删除失败')
  }
}

onMounted(() => {
  publishStore.fetchRecords()
})
</script>

<style scoped>
.publish-center-view {
  animation: fadeInUp 0.35s cubic-bezier(0.4, 0, 0.2, 1);
}

.title-row {
  display: flex;
  justify-content: space-between;
  align-items: center;
  width: 100%;
}

.title-left {
  display: flex;
  align-items: center;
  gap: 6px;
}

.empty-state {
  text-align: center;
  padding: 48px 0;
  color: var(--text-placeholder);
}
.empty-state p { font-size: 14px; margin-top: 8px; }
.empty-state .sub { font-size: 12px; color: var(--text-secondary); }

.records-list {
  display: flex;
  flex-direction: column;
  gap: 8px;
}

.record-item {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 14px 16px;
  border-radius: var(--radius-md);
  border: 1px solid var(--border-light);
  transition: all var(--transition-fast);
}

.record-item:hover {
  background: var(--bg-hover);
}

.record-platform {
  display: flex;
  align-items: center;
  gap: 8px;
  margin-bottom: 6px;
}

.record-title {
  font-weight: 500;
  color: var(--text-primary);
  font-size: 14px;
}

.record-meta {
  display: flex;
  align-items: center;
  gap: 8px;
}

.meta-text {
  font-size: 12px;
  color: var(--text-placeholder);
}

.record-error {
  font-size: 12px;
  color: var(--danger);
  margin-top: 4px;
}

.view-link {
  font-size: 13px;
  color: var(--primary);
  text-decoration: none;
}

.view-link:hover {
  text-decoration: underline;
}

.accounts-list {
  display: flex;
  flex-direction: column;
  gap: 8px;
}

.account-item {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 14px 16px;
  border-radius: var(--radius-md);
  border: 1px solid var(--border-light);
}

.account-info {
  display: flex;
  align-items: center;
  gap: 10px;
}

.account-name {
  font-weight: 500;
  color: var(--text-primary);
}

.pagination-wrapper {
  display: flex;
  justify-content: center;
  margin-top: 20px;
}

/* ======== 响应式 ======== */
@media (max-width: 767px) {
  .record-item {
    flex-direction: column;
    align-items: flex-start;
    gap: 10px;
    padding: 12px;
  }
  .record-action {
    align-self: flex-end;
  }
  .account-item {
    flex-direction: column;
    align-items: flex-start;
    gap: 10px;
    padding: 12px;
  }
  .account-info {
    flex-wrap: wrap;
    gap: 6px;
  }
  .record-meta {
    flex-wrap: wrap;
  }
}
</style>
