import { ref } from 'vue'
import { ElMessage } from 'element-plus'
import { optimizePrompt } from '@/api/generation'

/**
 * AI 提示词优化 composable
 * 封装提示词优化/扩写/翻译的共享逻辑，避免在多个视图中重复代码
 *
 * @param getPrompt - 获取当前提示词的函数
 * @param setPrompt - 设置优化后提示词的函数
 * @param getStyle - 获取当前风格的函数（可选），用于引导优化方向
 */
export function usePromptOptimize(
  getPrompt: () => string,
  setPrompt: (value: string) => void,
  getStyle?: () => string | undefined,
) {
  const optimizing = ref(false)

  async function handleOptimize(action: string) {
    const prompt = getPrompt()
    if (!prompt.trim()) return
    optimizing.value = true
    try {
      const res = await optimizePrompt({
        prompt,
        action: action as 'optimize' | 'expand' | 'translate',
        style: getStyle?.() || undefined,
      })
      setPrompt(res.data.optimized_prompt)
      ElMessage.success(`提示词${action === 'translate' ? '翻译' : action === 'expand' ? '扩写' : '优化'}完成`)
    } catch (e: any) {
      ElMessage.error(e?.message || 'AI 优化失败，请检查 AI 模型配置')
    } finally {
      optimizing.value = false
    }
  }

  return { optimizing, handleOptimize }
}
