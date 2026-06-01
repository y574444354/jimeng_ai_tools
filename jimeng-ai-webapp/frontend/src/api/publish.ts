import request from './request'

// ========== 类型定义 ==========

export interface PublishRecord {
  id: string
  article_id: string
  article_title?: string
  platform: string
  platform_post_id?: string
  status: string
  publish_url?: string
  error_message?: string
  published_at?: string
  created_at?: string
}

export interface PlatformAccount {
  id: string
  platform: string
  account_name: string
  is_active: boolean
  token_expires_at?: string
  created_at?: string
}

// ========== 发布API ==========

export async function publishToXiaohongshu(data: {
  article_id: string
  platform_account_id: string
  title?: string
  images?: string[]
  tags?: string[]
  schedule_at?: string
}) {
  return request.post('/publish/xiaohongshu', data)
}

export async function getPublishRecords(params: {
  page?: number
  page_size?: number
  platform?: string
}) {
  return request.get('/publish/records', { params })
}

export async function getPublishRecord(id: string) {
  return request.get(`/publish/records/${id}`)
}

// ========== 平台账号API ==========

export async function getPlatformAccounts(platform?: string) {
  return request.get('/publish/accounts', { params: { platform } })
}

export async function addPlatformAccount(data: {
  platform: string
  account_name: string
  access_token: string
  token_expires_at?: string
}) {
  return request.post('/publish/accounts', data)
}

export async function updatePlatformAccount(id: string, data: {
  account_name?: string
  access_token?: string
  token_expires_at?: string
  is_active?: boolean
}) {
  return request.put(`/publish/accounts/${id}`, data)
}

export async function deletePlatformAccount(id: string) {
  return request.delete(`/publish/accounts/${id}`)
}
