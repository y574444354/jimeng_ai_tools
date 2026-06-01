import { defineStore } from 'pinia'
import { ref } from 'vue'
import { searchWeb, summarizeSearch, type SearchResult, type SummarizeResult } from '@/api/search'

export const useSearchStore = defineStore('search', () => {
  const query = ref('')
  const results = ref<SearchResult[]>([])
  const isSearching = ref(false)
  const selectedSources = ref<SearchResult[]>([])
  const summarizeResult = ref<SummarizeResult | null>(null)
  const isSummarizing = ref(false)

  async function search(queryText: string, maxResults: number = 10) {
    query.value = queryText
    isSearching.value = true
    try {
      const res: any = await searchWeb(queryText, maxResults)
      results.value = res.data?.results || []
      return res.data
    } finally {
      isSearching.value = false
    }
  }

  async function summarize(sources: SearchResult[], style?: string) {
    isSummarizing.value = true
    try {
      const res: any = await summarizeSearch({
        query: query.value,
        sources,
        style,
      })
      summarizeResult.value = res.data
      return res.data as SummarizeResult
    } finally {
      isSummarizing.value = false
    }
  }

  function toggleSource(source: SearchResult) {
    const idx = selectedSources.value.findIndex(s => s.url === source.url)
    if (idx >= 0) {
      selectedSources.value.splice(idx, 1)
    } else {
      selectedSources.value.push(source)
    }
  }

  function isSelected(source: SearchResult): boolean {
    return selectedSources.value.some(s => s.url === source.url)
  }

  function clearSearch() {
    query.value = ''
    results.value = []
    selectedSources.value = []
    summarizeResult.value = null
  }

  return {
    query, results, isSearching,
    selectedSources, summarizeResult, isSummarizing,
    search, summarize, toggleSource, isSelected, clearSearch,
  }
})
