import { create } from 'zustand'
import { api, ModelInfo } from '@/lib/api'

interface ModelStore {
  models: ModelInfo[]
  loading: boolean
  error: string | null
  
  fetchModels: () => Promise<void>
  addModel: (model: ModelInfo) => void
  updateModel: (modelId: string, updates: Partial<ModelInfo>) => void
  removeModel: (modelId: string) => void
  
  // Actions
  deployModel: (request: any) => Promise<ModelInfo>
  stopModel: (modelId: string) => Promise<void>
  deleteModel: (modelId: string) => Promise<void>
}

export const useModelStore = create<ModelStore>((set, get) => ({
  models: [],
  loading: false,
  error: null,

  fetchModels: async () => {
    set({ loading: true, error: null })
    try {
      const models = await api.listModels()
      set({ models, loading: false })
    } catch (error: any) {
      set({ error: error.message, loading: false })
    }
  },

  addModel: (model) => {
    set((state) => ({
      models: [...state.models, model],
    }))
  },

  updateModel: (modelId, updates) => {
    set((state) => ({
      models: state.models.map((m) =>
        m.id === modelId ? { ...m, ...updates } : m
      ),
    }))
  },

  removeModel: (modelId) => {
    set((state) => ({
      models: state.models.filter((m) => m.id !== modelId),
    }))
  },

  deployModel: async (request) => {
    set({ loading: true, error: null })
    try {
      const model = await api.deployModel(request)
      get().addModel(model)
      set({ loading: false })
      return model
    } catch (error: any) {
      set({ error: error.message, loading: false })
      throw error
    }
  },

  stopModel: async (modelId) => {
    try {
      await api.stopModel(modelId)
      get().updateModel(modelId, { status: 'STOPPED' })
    } catch (error: any) {
      set({ error: error.message })
      throw error
    }
  },

  deleteModel: async (modelId) => {
    try {
      await api.removeModel(modelId)
      get().removeModel(modelId)
    } catch (error: any) {
      set({ error: error.message })
      throw error
    }
  },
}))

