import { defineStore } from 'pinia'
import { ref } from 'vue'
import { submitText2Img, submitImg2Img, submitInpainting, queryStatus, getResult } from '@/api/generation'

export const useGenerationStore = defineStore('generation', () => {
  const isGenerating = ref(false)
  const currentTaskId = ref<string | null>(null)
  const currentStatus = ref<string>('')
  const error = ref<string | null>(null)
  const result = ref<any>(null)

  async function startText2Img(params: any) {
    console.log('[DEBUG store] startText2Img 被调用, params=', params)
    isGenerating.value = true
    error.value = null
    currentStatus.value = 'generating'
    try {
      console.log('[DEBUG store] 即将调用 submitText2Img API...')
      const res = await submitText2Img(params)
      console.log('[DEBUG store] submitText2Img 返回:', res)
      // 后端同步生成，直接返回含 images 的完整结果
      result.value = res.data
      currentTaskId.value = res.data.id
      currentStatus.value = 'completed'
      isGenerating.value = false
      return res
    } catch (e: any) {
      console.error('[DEBUG store] startText2Img 失败:', e)
      error.value = e.message || '生成失败'
      currentStatus.value = 'failed'
      isGenerating.value = false
      throw e
    }
  }

  async function startImg2Img(params: any) {
    isGenerating.value = true
    error.value = null
    currentStatus.value = 'generating'
    try {
      const res = await submitImg2Img(params)
      result.value = res.data
      currentTaskId.value = res.data.id
      currentStatus.value = 'completed'
      isGenerating.value = false
      return res
    } catch (e: any) {
      error.value = e.message || '生成失败'
      currentStatus.value = 'failed'
      isGenerating.value = false
      throw e
    }
  }

  async function startInpainting(params: any) {
    isGenerating.value = true
    error.value = null
    currentStatus.value = 'generating'
    try {
      const res = await submitInpainting(params)
      result.value = res.data
      currentTaskId.value = res.data.id
      currentStatus.value = 'completed'
      isGenerating.value = false
      return res
    } catch (e: any) {
      error.value = e.message || '生成失败'
      currentStatus.value = 'failed'
      isGenerating.value = false
      throw e
    }
  }

  function reset() {
    isGenerating.value = false
    currentTaskId.value = null
    currentStatus.value = ''
    error.value = null
    result.value = null
  }

  return {
    isGenerating,
    currentTaskId,
    currentStatus,
    error,
    result,
    startText2Img,
    startImg2Img,
    startInpainting,
    reset,
  }
})