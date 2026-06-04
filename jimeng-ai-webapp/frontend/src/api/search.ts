import request from './request'

// ========== 类型定义 ==========

export interface SearchResult {
  title: string
  url?: string
  snippet?: string
  content?: string
}

export interface OutlineItem {
  heading: string
  key_points: string[]
}

export interface SummarizeResult {
  title_suggestions: string[]
  outline: OutlineItem[]
  summary?: string
  full_content?: string
}

// ========== 搜索API ==========

export async function searchWeb(query: string, maxResults: number = 10, language: string = 'zh') {
  return request.post('/search/web', { query, max_results: maxResults, language })
}

export async function summarizeSearch(data: {
  query: string
  sources: SearchResult[]
  style?: string
}) {
  return request.post('/search/summarize', data)
}

export interface FetchContentResult {
  url: string
  content: string
  content_length: number
}

export async function fetchWebContent(url: string, useBrowser: boolean = false): Promise<FetchContentResult> {
  return request
    .post('/search/fetch-content', { url, use_browser: useBrowser })
    .then((res: any) => res.data)
}
