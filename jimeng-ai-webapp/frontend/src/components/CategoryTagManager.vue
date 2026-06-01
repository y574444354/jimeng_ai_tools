<template>
  <div class="category-tag-manager">
    <el-tabs v-model="activeTab">
      <!-- ===== 分类管理 ===== -->
      <el-tab-pane label="分类管理" name="categories">
        <div class="manage-header">
          <el-button size="small" type="primary" @click="showAddCategory = true">
            <el-icon :size="14"><Plus /></el-icon>
            添加分类
          </el-button>
        </div>

        <div v-if="articleStore.categories.length === 0" class="empty">
          暂无分类，点击上方按钮添加
        </div>

        <div v-else class="manage-list">
          <div v-for="cat in articleStore.categories" :key="cat.id" class="manage-item">
            <div class="item-info">
              <span class="item-name">{{ cat.name }}</span>
              <span class="item-count">{{ cat.article_count || 0 }} 篇文章</span>
            </div>
            <div class="item-actions">
              <el-button size="small" text @click="editCategory(cat)">
                <el-icon :size="14"><Edit /></el-icon>
              </el-button>
              <el-button size="small" text type="danger" @click="removeCategory(cat.id)">
                <el-icon :size="14"><Delete /></el-icon>
              </el-button>
            </div>
          </div>
        </div>

        <!-- 添加/编辑分类对话框 -->
        <el-dialog v-model="showAddCategory" :title="editingCategory ? '编辑分类' : '添加分类'" width="400px">
          <el-form label-position="top">
            <el-form-item label="分类名称">
              <el-input v-model="categoryForm.name" placeholder="输入分类名称" maxlength="50" />
            </el-form-item>
            <el-form-item label="描述">
              <el-input v-model="categoryForm.description" placeholder="分类描述（可选）" maxlength="200" />
            </el-form-item>
            <el-form-item label="排序">
              <el-input-number v-model="categoryForm.sort_order" :min="0" :max="999" />
            </el-form-item>
          </el-form>
          <template #footer>
            <el-button @click="showAddCategory = false">取消</el-button>
            <el-button type="primary" @click="saveCategory">
              {{ editingCategory ? '保存' : '添加' }}
            </el-button>
          </template>
        </el-dialog>
      </el-tab-pane>

      <!-- ===== 标签管理 ===== -->
      <el-tab-pane label="标签管理" name="tags">
        <div class="manage-header">
          <el-button size="small" type="primary" @click="showAddTag = true">
            <el-icon :size="14"><Plus /></el-icon>
            添加标签
          </el-button>
        </div>

        <div v-if="articleStore.tags.length === 0" class="empty">
          暂无标签，点击上方按钮添加
        </div>

        <div v-else class="tag-grid">
          <div v-for="tag in articleStore.tags" :key="tag.id" class="tag-item" :style="{ borderColor: tag.color + '40' }">
            <div class="tag-color" :style="{ background: tag.color }"></div>
            <span class="tag-name">{{ tag.name }}</span>
            <span class="tag-count">{{ tag.article_count || 0 }}篇</span>
            <el-button size="small" text @click="editTag(tag)">
              <el-icon :size="14"><Edit /></el-icon>
            </el-button>
            <el-button size="small" text type="danger" @click="removeTag(tag.id)">
              <el-icon :size="14"><Delete /></el-icon>
            </el-button>
          </div>
        </div>

        <!-- 添加/编辑标签对话框 -->
        <el-dialog v-model="showAddTag" :title="editingTag ? '编辑标签' : '添加标签'" width="400px">
          <el-form label-position="top">
            <el-form-item label="标签名称">
              <el-input v-model="tagForm.name" placeholder="输入标签名称" maxlength="30" />
            </el-form-item>
            <el-form-item label="标签颜色">
              <div class="color-picker-row">
                <div
                  v-for="c in presetColors"
                  :key="c"
                  class="color-swatch"
                  :class="{ active: tagForm.color === c }"
                  :style="{ background: c }"
                  @click="tagForm.color = c"
                />
              </div>
            </el-form-item>
          </el-form>
          <template #footer>
            <el-button @click="showAddTag = false">取消</el-button>
            <el-button type="primary" @click="saveTag">
              {{ editingTag ? '保存' : '添加' }}
            </el-button>
          </template>
        </el-dialog>
      </el-tab-pane>
    </el-tabs>
  </div>
</template>

<script setup lang="ts">
import { ref, reactive, onMounted } from 'vue'
import { Plus, Edit, Delete } from '@element-plus/icons-vue'
import { useArticleStore } from '@/stores/article'
import { ElMessage } from 'element-plus'

const articleStore = useArticleStore()
const activeTab = ref('categories')

// 分类
const showAddCategory = ref(false)
const editingCategory = ref<any>(null)
const categoryForm = reactive({ name: '', description: '', sort_order: 0 })

// 标签
const showAddTag = ref(false)
const editingTag = ref<any>(null)
const tagForm = reactive({ name: '', color: '#6366F1' })

const presetColors = [
  '#6366F1', '#8B5CF6', '#EC4899', '#EF4444',
  '#F59E0B', '#10B981', '#06B6D4', '#3B82F6',
  '#6B7280', '#111827',
]

function editCategory(cat: any) {
  editingCategory.value = cat
  categoryForm.name = cat.name
  categoryForm.description = cat.description || ''
  categoryForm.sort_order = cat.sort_order || 0
  showAddCategory.value = true
}

async function saveCategory() {
  if (!categoryForm.name.trim()) {
    ElMessage.warning('请输入分类名称')
    return
  }
  try {
    if (editingCategory.value) {
      await articleStore.editCategory(editingCategory.value.id, { ...categoryForm })
    } else {
      await articleStore.addCategory({ ...categoryForm })
    }
    showAddCategory.value = false
    editingCategory.value = null
    categoryForm.name = ''
    categoryForm.description = ''
    categoryForm.sort_order = 0
  } catch (e: any) {
    ElMessage.error(e.message || '操作失败')
  }
}

async function removeCategory(id: string) {
  try {
    await articleStore.removeCategory(id)
  } catch (e: any) {
    ElMessage.error(e.message || '删除失败')
  }
}

function editTag(tag: any) {
  editingTag.value = tag
  tagForm.name = tag.name
  tagForm.color = tag.color
  showAddTag.value = true
}

async function saveTag() {
  if (!tagForm.name.trim()) {
    ElMessage.warning('请输入标签名称')
    return
  }
  try {
    if (editingTag.value) {
      await articleStore.editTag(editingTag.value.id, { ...tagForm })
    } else {
      await articleStore.addTag({ ...tagForm })
    }
    showAddTag.value = false
    editingTag.value = null
    tagForm.name = ''
    tagForm.color = '#6366F1'
  } catch (e: any) {
    ElMessage.error(e.message || '操作失败')
  }
}

async function removeTag(id: string) {
  try {
    await articleStore.removeTag(id)
  } catch (e: any) {
    ElMessage.error(e.message || '删除失败')
  }
}

onMounted(() => {
  articleStore.fetchCategories()
  articleStore.fetchTags()
})
</script>

<style scoped>
.manage-header {
  margin-bottom: 12px;
}

.empty {
  text-align: center;
  padding: 24px 0;
  color: var(--text-placeholder);
  font-size: 13px;
}

.manage-list {
  display: flex;
  flex-direction: column;
  gap: 4px;
}

.manage-item {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 10px 12px;
  border-radius: var(--radius-sm);
  transition: background var(--transition-fast);
}

.manage-item:hover {
  background: var(--bg-hover);
}

.item-info {
  display: flex;
  align-items: center;
  gap: 12px;
}

.item-name {
  font-weight: 500;
  color: var(--text-primary);
}

.item-count {
  font-size: 12px;
  color: var(--text-placeholder);
}

.item-actions {
  display: flex;
  gap: 4px;
}

.tag-grid {
  display: grid;
  grid-template-columns: repeat(auto-fill, minmax(200px, 1fr));
  gap: 8px;
}

.tag-item {
  display: flex;
  align-items: center;
  gap: 8px;
  padding: 10px 12px;
  border-radius: var(--radius-sm);
  border: 1px solid;
}

.tag-color {
  width: 12px;
  height: 12px;
  border-radius: 50%;
  flex-shrink: 0;
}

.tag-name {
  flex: 1;
  font-weight: 500;
  font-size: 13px;
  color: var(--text-primary);
}

.tag-count {
  font-size: 11px;
  color: var(--text-placeholder);
}

.color-picker-row {
  display: flex;
  gap: 8px;
  flex-wrap: wrap;
}

.color-swatch {
  width: 28px;
  height: 28px;
  border-radius: 50%;
  cursor: pointer;
  border: 2px solid transparent;
  transition: all var(--transition-fast);
}

.color-swatch:hover {
  transform: scale(1.15);
}

.color-swatch.active {
  border-color: var(--text-primary);
  box-shadow: 0 0 0 2px white inset;
}
</style>
