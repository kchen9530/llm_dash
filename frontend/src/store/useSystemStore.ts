import { create } from 'zustand'
import { api, SystemStatus } from '@/lib/api'

interface SystemStore {
  status: SystemStatus | null
  loading: boolean
  error: string | null
  
  fetchStatus: () => Promise<void>
  startPolling: (interval?: number) => void
  stopPolling: () => void
}

let pollInterval: NodeJS.Timeout | null = null

export const useSystemStore = create<SystemStore>((set, get) => ({
  status: null,
  loading: false,
  error: null,

  fetchStatus: async () => {
    try {
      const status = await api.getSystemStatus()
      set({ status, error: null })
    } catch (error: any) {
      set({ error: error.message })
    }
  },

  startPolling: (interval = 3000) => {
    // 先立即获取一次
    get().fetchStatus()
    
    // 停止之前的轮询
    if (pollInterval) {
      clearInterval(pollInterval)
    }
    
    // 开始新的轮询
    pollInterval = setInterval(() => {
      get().fetchStatus()
    }, interval)
  },

  stopPolling: () => {
    if (pollInterval) {
      clearInterval(pollInterval)
      pollInterval = null
    }
  },
}))

