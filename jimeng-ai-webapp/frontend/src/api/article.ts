import request from './request'

// ========== 类型定义 ==========

export interface Article {
  id: string
  title: string
  content?: string
  summary?: string
  status: string
  category_id?: string
  category_name?: string
  cover_image_path?: string
  word_count: number
  view_count: number
  tags: Tag[]
  created_at?: string
  updated_at?: string
}

export interface ArticleListItem {
  id: string
  title: string
  summary?: string
  status: string
  category_name?: string
  cover_image_path?: string
  word_count: number
  tags: Tag[]
  created_at?: string
}

export interface Tag {
  id: string
  name: string
  color: string
  article_count?: number
}

export interface Category {
  id: string
  name: string
  description?: string
  sort_order: number
  article_count?: number
}

export interface ArticleVersion {
  id: string
  article_id: string
  version_number: number
  title: string
  content?: string
  change_summary?: string
  created_at?: string
}

// ========== 文章API ==========

export async function getArticleList(params: {
  page?: number
  page_size?: number
  status?: string
  category_id?: string
  keyword?: string
}) {
  return request.get('/articles', { params })
}

export async function getArticle(id: string) {
  return request.get(`/articles/${id}`)
}

export async function createArticle(data: {
  title: string
  content?: string
  summary?: string
  category_id?: string
  tag_ids?: string[]
  cover_image_path?: string
  status?: string
}) {
  return request.post('/articles', data)
}

export async function updateArticle(id: string, data: {
  title?: string
  content?: string
  summary?: string
  category_id?: string
  tag_ids?: string[]
  cover_image_path?: string
  status?: string
}) {
  return request.put(`/articles/${id}`, data)
}

export async function deleteArticle(id: string) {
  return request.delete(`/articles/${id}`)
}

export async function autoSaveArticle(id: string, data: {
  title: string
  content?: string
  summary?: string
}) {
  return request.post(`/articles/${id}/auto-save`, data)
}

export async function getArticleVersions(id: string) {
  return request.get(`/articles/${id}/versions`)
}

export async function restoreArticleVersion(articleId: string, versionId: string) {
  return request.post(`/articles/${articleId}/versions/${versionId}/restore`)
}

export async function saveArticleSources(articleId: string, sources: any[]) {
  return request.post(`/articles/${articleId}/sources`, sources)
}

export async function getArticleSources(articleId: string) {
  return request.get(`/articles/${articleId}/sources`)
}

export async function generateArticle(articleId: string, data: {
  query: string
  source_ids?: string[]
  style?: string
}) {
  return request.post(`/articles/${articleId}/generate`, data)
}

// ========== 分类API ==========

export async function getCategories() {
  return request.get('/categories')
}

export async function createCategory(data: { name: string; description?: string; sort_order?: number }) {
  return request.post('/categories', data)
}

export async function updateCategory(id: string, data: { name?: string; description?: string; sort_order?: number }) {
  return request.put(`/categories/${id}`, data)
}

export async function deleteCategory(id: string) {
  return request.delete(`/categories/${id}`)
}

// ========== 标签API ==========

export async function getTags() {
  return request.get('/tags')
}

export async function createTag(data: { name: string; color?: string }) {
  return request.post('/tags', data)
}

export async function updateTag(id: string, data: { name?: string; color?: string }) {
  return request.put(`/tags/${id}`, data)
}

export async function deleteTag(id: string) {
  return request.delete(`/tags/${id}`)
}
