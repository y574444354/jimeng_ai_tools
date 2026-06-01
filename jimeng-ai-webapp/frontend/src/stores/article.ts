import { defineStore } from 'pinia'
import { ref, computed } from 'vue'
import {
  getArticleList, getArticle, createArticle, updateArticle, deleteArticle,
  autoSaveArticle, getArticleVersions, restoreArticleVersion,
  getCategories, createCategory, updateCategory, deleteCategory,
  getTags, createTag, updateTag, deleteTag,
  getArticleSources, saveArticleSources, generateArticle,
  type Article, type ArticleListItem, type Category, type Tag, type ArticleVersion,
} from '@/api/article'

export const useArticleStore = defineStore('article', () => {
  // 文章列表
  const articles = ref<ArticleListItem[]>([])
  const total = ref(0)
  const currentPage = ref(1)
  const pageSize = ref(20)
  const loading = ref(false)

  // 当前编辑的文章
  const currentArticle = ref<Article | null>(null)
  const currentVersions = ref<ArticleVersion[]>([])
  const currentSources = ref<any[]>([])

  // 分类和标签
  const categories = ref<Category[]>([])
  const tags = ref<Tag[]>([])

  // AI生成
  const isGenerating = ref(false)
  const generatedContent = ref<string | null>(null)

  // ======== 文章操作 ========

  async function fetchArticles(params?: {
    page?: number
    page_size?: number
    status?: string
    category_id?: string
    keyword?: string
  }) {
    loading.value = true
    try {
      const res: any = await getArticleList({
        page: params?.page || currentPage.value,
        page_size: params?.page_size || pageSize.value,
        status: params?.status,
        category_id: params?.category_id,
        keyword: params?.keyword,
      })
      articles.value = res.data.list || []
      total.value = res.data.total || 0
      currentPage.value = res.data.page || 1
    } finally {
      loading.value = false
    }
  }

  async function fetchArticle(id: string) {
    const res: any = await getArticle(id)
    currentArticle.value = res.data
    return res.data as Article
  }

  async function create(data: {
    title: string
    content?: string
    summary?: string
    category_id?: string
    tag_ids?: string[]
    cover_image_path?: string
    status?: string
  }) {
    const res: any = await createArticle(data)
    return res.data as Article
  }

  async function update(id: string, data: {
    title?: string
    content?: string
    summary?: string
    category_id?: string
    tag_ids?: string[]
    cover_image_path?: string
    status?: string
  }) {
    const res: any = await updateArticle(id, data)
    currentArticle.value = res.data
    return res.data as Article
  }

  async function remove(id: string) {
    await deleteArticle(id)
    currentArticle.value = null
  }

  async function autoSave(id: string, data: { title: string; content?: string; summary?: string }) {
    const res: any = await autoSaveArticle(id, data)
    currentArticle.value = res.data
  }

  // ======== 版本管理 ========

  async function fetchVersions(articleId: string) {
    const res: any = await getArticleVersions(articleId)
    currentVersions.value = res.data || []
  }

  async function restoreVersion(articleId: string, versionId: string) {
    const res: any = await restoreArticleVersion(articleId, versionId)
    currentArticle.value = res.data
  }

  // ======== 素材管理 ========

  async function fetchSources(articleId: string) {
    const res: any = await getArticleSources(articleId)
    currentSources.value = res.data || []
  }

  async function saveSources(articleId: string, sources: any[]) {
    const res: any = await saveArticleSources(articleId, sources)
    currentSources.value = res.data || []
  }

  // ======== AI生成 ========

  async function generate(articleId: string, query: string, style?: string) {
    isGenerating.value = true
    try {
      const res: any = await generateArticle(articleId, { query, style })
      generatedContent.value = res.data?.full_content || null
      return res.data
    } finally {
      isGenerating.value = false
    }
  }

  // ======== 分类管理 ========

  async function fetchCategories() {
    const res: any = await getCategories()
    categories.value = res.data || []
  }

  async function addCategory(data: { name: string; description?: string; sort_order?: number }) {
    await createCategory(data)
    await fetchCategories()
  }

  async function editCategory(id: string, data: { name?: string; description?: string; sort_order?: number }) {
    await updateCategory(id, data)
    await fetchCategories()
  }

  async function removeCategory(id: string) {
    await deleteCategory(id)
    await fetchCategories()
  }

  // ======== 标签管理 ========

  async function fetchTags() {
    const res: any = await getTags()
    tags.value = res.data || []
  }

  async function addTag(data: { name: string; color?: string }) {
    await createTag(data)
    await fetchTags()
  }

  async function editTag(id: string, data: { name?: string; color?: string }) {
    await updateTag(id, data)
    await fetchTags()
  }

  async function removeTag(id: string) {
    await deleteTag(id)
    await fetchTags()
  }

  return {
    articles, total, currentPage, pageSize, loading,
    currentArticle, currentVersions, currentSources,
    categories, tags,
    isGenerating, generatedContent,
    fetchArticles, fetchArticle, create, update, remove, autoSave,
    fetchVersions, restoreVersion,
    fetchSources, saveSources,
    generate,
    fetchCategories, addCategory, editCategory, removeCategory,
    fetchTags, addTag, editTag, removeTag,
  }
})
