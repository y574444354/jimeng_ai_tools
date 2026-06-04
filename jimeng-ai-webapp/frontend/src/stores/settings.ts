import { defineStore } from 'pinia'
import { ref } from 'vue'
import {
  listAIConfigs,
  createAIConfig,
  updateAIConfig,
  deleteAIConfig,
  activateAIConfig,
  testAIConnection,
  type AIConfigItem,
  type AIConfigForm,
  type AIConfigTestParams,
  type AIConfigTestResult,
} from '@/api/settings'

export const useSettingsStore = defineStore('settings', () => {
  const configs = ref<AIConfigItem[]>([])
  const loading = ref(false)
  const testResult = ref<AIConfigTestResult | null>(null)
  const testLoading = ref(false)

  async function fetchConfigs() {
    loading.value = true
    try {
      configs.value = await listAIConfigs()
    } finally {
      loading.value = false
    }
  }

  async function addConfig(data: AIConfigForm) {
    const created = await createAIConfig(data)
    await fetchConfigs()
    return created
  }

  async function editConfig(id: string, data: Partial<AIConfigForm>) {
    const updated = await updateAIConfig(id, data)
    await fetchConfigs()
    return updated
  }

  async function removeConfig(id: string) {
    await deleteAIConfig(id)
    await fetchConfigs()
  }

  async function setActive(id: string) {
    await activateAIConfig(id)
    await fetchConfigs()
  }

  async function testConnection(params: AIConfigTestParams) {
    testLoading.value = true
    testResult.value = null
    try {
      testResult.value = await testAIConnection(params)
    } finally {
      testLoading.value = false
    }
  }

  return {
    configs,
    loading,
    testResult,
    testLoading,
    fetchConfigs,
    addConfig,
    editConfig,
    removeConfig,
    setActive,
    testConnection,
  }
})
