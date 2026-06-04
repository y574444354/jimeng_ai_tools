import request from './request'

// ========== 类型定义 ==========

export interface AIConfigItem {
  id: string
  name: string
  api_base_url: string
  model_name: string
  api_key: string // 已脱敏
  is_active: boolean
  temperature: number
  max_tokens: number
  created_at?: string
  updated_at?: string
}

export interface AIConfigForm {
  name: string
  api_base_url: string
  model_name: string
  api_key: string
  temperature: number
  max_tokens: number
}

export interface AIConfigTestParams {
  api_base_url: string
  model_name: string
  api_key: string
}

export interface AIConfigTestResult {
  ok: boolean
  model?: string
  latency_ms?: number
  reply_preview?: string
  error?: string
}

// ========== API 调用 ==========

export function listAIConfigs(): Promise<AIConfigItem[]> {
  return request.get('/settings/ai-configs').then((res: any) => res.data)
}

export function getAIConfig(id: string): Promise<AIConfigItem> {
  return request.get(`/settings/ai-configs/${id}`).then((res: any) => res.data)
}

export function createAIConfig(data: AIConfigForm): Promise<AIConfigItem> {
  return request.post('/settings/ai-configs', data).then((res: any) => res.data)
}

export function updateAIConfig(id: string, data: Partial<AIConfigForm>): Promise<AIConfigItem> {
  return request.put(`/settings/ai-configs/${id}`, data).then((res: any) => res.data)
}

export function deleteAIConfig(id: string): Promise<void> {
  return request.delete(`/settings/ai-configs/${id}`)
}

export function activateAIConfig(id: string): Promise<AIConfigItem> {
  return request.post(`/settings/ai-configs/${id}/activate`).then((res: any) => res.data)
}

export function testAIConnection(params: AIConfigTestParams): Promise<AIConfigTestResult> {
  return request.post('/settings/ai-configs/test', params).then((res: any) => res.data)
}
