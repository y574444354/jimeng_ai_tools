import { defineStore } from 'pinia'
import { ref } from 'vue'
import { recognizeText, type OCRResponse } from '@/api/ocr'

export const useOcrStore = defineStore('ocr', () => {
  // 是否正在识别
  const isRecognizing = ref(false)
  // 错误信息
  const error = ref<string | null>(null)
  // 识别结果
  const result = ref<OCRResponse | null>(null)
  // 已上传的图片路径
  const uploadedImagePath = ref<string>('')

  // 开始识别
  async function startRecognize(imagePath: string) {
    isRecognizing.value = true
    error.value = null
    uploadedImagePath.value = imagePath
    try {
      const res = await recognizeText(imagePath)
      result.value = res.data
      isRecognizing.value = false
      return res
    } catch (e: any) {
      error.value = e.message || '识别失败'
      isRecognizing.value = false
      throw e
    }
  }

  // 重置状态
  function reset() {
    isRecognizing.value = false
    error.value = null
    result.value = null
    uploadedImagePath.value = ''
  }

  return {
    isRecognizing,
    error,
    result,
    uploadedImagePath,
    startRecognize,
    reset,
  }
})
