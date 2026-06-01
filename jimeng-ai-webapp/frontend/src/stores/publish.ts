import { defineStore } from 'pinia'
import { ref } from 'vue'
import {
  publishToXiaohongshu, getPublishRecords,
  getPlatformAccounts, addPlatformAccount, deletePlatformAccount,
  type PublishRecord, type PlatformAccount,
} from '@/api/publish'

export const usePublishStore = defineStore('publish', () => {
  const records = ref<PublishRecord[]>([])
  const accounts = ref<PlatformAccount[]>([])
  const total = ref(0)
  const loading = ref(false)

  async function publishToXHS(data: {
    article_id: string
    platform_account_id: string
    title?: string
    images?: string[]
    tags?: string[]
  }) {
    const res: any = await publishToXiaohongshu(data)
    return res.data as PublishRecord
  }

  async function fetchRecords(params?: { page?: number; page_size?: number; platform?: string }) {
    loading.value = true
    try {
      const res: any = await getPublishRecords(params || {})
      records.value = res.data?.list || []
      total.value = res.data?.total || 0
    } finally {
      loading.value = false
    }
  }

  async function fetchAccounts(platform?: string) {
    const res: any = await getPlatformAccounts(platform)
    accounts.value = res.data || []
  }

  async function addAccount(data: {
    platform: string
    account_name: string
    access_token: string
    token_expires_at?: string
  }) {
    await addPlatformAccount(data)
    await fetchAccounts()
  }

  async function removeAccount(id: string) {
    await deletePlatformAccount(id)
    await fetchAccounts()
  }

  return {
    records, accounts, total, loading,
    publishToXHS, fetchRecords, fetchAccounts, addAccount, removeAccount,
  }
})
