import { create } from 'zustand'
import { persist } from 'zustand/middleware'
import { ChatMessage } from '@/lib/api'

interface ChatSession {
  modelId: string
  modelName: string
  messages: ChatMessage[]
  lastUpdated: number
}

interface ChatStore {
  sessions: Record<string, ChatSession>
  
  // Get messages for a specific model
  getMessages: (modelId: string) => ChatMessage[]
  
  // Add a message to a model's chat
  addMessage: (modelId: string, modelName: string, message: ChatMessage) => void
  
  // Update the last message (for streaming)
  updateLastMessage: (modelId: string, content: string) => void
  
  // Clear messages for a specific model
  clearMessages: (modelId: string) => void
  
  // Clear all chat history
  clearAllSessions: () => void
}

export const useChatStore = create<ChatStore>()(
  persist(
    (set, get) => ({
      sessions: {},
      
      getMessages: (modelId: string) => {
        const session = get().sessions[modelId]
        return session?.messages || []
      },
      
      addMessage: (modelId: string, modelName: string, message: ChatMessage) => {
        set((state) => {
          const session = state.sessions[modelId] || {
            modelId,
            modelName,
            messages: [],
            lastUpdated: Date.now()
          }
          
          return {
            sessions: {
              ...state.sessions,
              [modelId]: {
                ...session,
                messages: [...session.messages, message],
                lastUpdated: Date.now()
              }
            }
          }
        })
      },
      
      updateLastMessage: (modelId: string, content: string) => {
        set((state) => {
          const session = state.sessions[modelId]
          if (!session || session.messages.length === 0) return state
          
          const messages = [...session.messages]
          messages[messages.length - 1] = {
            ...messages[messages.length - 1],
            content
          }
          
          return {
            sessions: {
              ...state.sessions,
              [modelId]: {
                ...session,
                messages,
                lastUpdated: Date.now()
              }
            }
          }
        })
      },
      
      clearMessages: (modelId: string) => {
        set((state) => {
          const { [modelId]: _, ...rest } = state.sessions
          return { sessions: rest }
        })
      },
      
      clearAllSessions: () => {
        set({ sessions: {} })
      }
    }),
    {
      name: 'chat-storage', // localStorage key
      version: 1,
    }
  )
)
