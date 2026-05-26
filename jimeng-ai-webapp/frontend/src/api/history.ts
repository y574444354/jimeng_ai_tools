import request from './request'

export interface HistoryItem {
  id: string
  task_type: string
  prompt: string
  image_size: string
  style: string | null
  status: string
  image_count: number
  created_at: string
  thumbnail_path: string | null
}

export interface HistoryListResponse {
  list: HistoryItem[]
  total: number
  page: number
  pageSize: number
}

export async function getHistoryList(page: number = 1, pageSize: number = 20) {
  return request.get('/generations', { params: { page, page_size: pageSize } })
}

export async function getHistoryDetail(id: string) {
  return request.get(`/generations/${id}`)
}

export async function deleteHistory(id: string) {
  return request.delete(`/generations/${id}`)
}