/**
 * API 客户端
 */

const API_BASE = '/api'

export interface DeployRequest {
  model_name: string
  local_path?: string
  port?: number
  parameters?: {
    dtype?: string
    gpu_memory_utilization?: number
    max_model_len?: number
    trust_remote_code?: boolean
  }
}

export interface ModelInfo {
  id: string
  model_name: string
  status: string
  pid?: number
  port: number
  start_time?: string
  error_message?: string
  parameters: Record<string, any>
}

export interface SystemStatus {
  cpu_percent: number
  memory_percent: number
  memory_used_gb: number
  memory_total_gb: number
  gpu_info: GPUInfo[]
}

export interface GPUInfo {
  id: number
  name: string
  memory_used_mb: number
  memory_total_mb: number
  memory_percent: number
  utilization_percent: number
  temperature?: number
}

export interface ChatMessage {
  role: 'user' | 'assistant' | 'system'
  content: string
}

class ApiClient {
  // Generic HTTP methods
  async get(url: string): Promise<any> {
    const res = await fetch(url)
    if (!res.ok) throw new Error(`Failed to fetch ${url}`)
    const data = await res.json()
    return { data }  // Return in format that matches existing code
  }

  // System APIs
  async getSystemStatus(): Promise<SystemStatus> {
    const res = await fetch(`${API_BASE}/system/status`)
    if (!res.ok) throw new Error('Failed to fetch system status')
    return res.json()
  }

  async getGPUInfo(): Promise<GPUInfo[]> {
    const res = await fetch(`${API_BASE}/system/gpu`)
    if (!res.ok) throw new Error('Failed to fetch GPU info')
    return res.json()
  }

  // Model APIs
  async deployModel(request: DeployRequest): Promise<ModelInfo> {
    const res = await fetch(`${API_BASE}/models/deploy`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify(request),
    })
    if (!res.ok) {
      const error = await res.json()
      throw new Error(error.detail || 'Failed to deploy model')
    }
    return res.json()
  }

  async listModels(): Promise<ModelInfo[]> {
    const res = await fetch(`${API_BASE}/models/list`)
    if (!res.ok) throw new Error('Failed to list models')
    return res.json()
  }

  async getModel(modelId: string): Promise<ModelInfo> {
    const res = await fetch(`${API_BASE}/models/${modelId}`)
    if (!res.ok) throw new Error(`Failed to get model ${modelId}`)
    return res.json()
  }

  async stopModel(modelId: string): Promise<void> {
    const res = await fetch(`${API_BASE}/models/${modelId}/stop`, {
      method: 'POST',
    })
    if (!res.ok) throw new Error(`Failed to stop model ${modelId}`)
  }

  async removeModel(modelId: string): Promise<void> {
    const res = await fetch(`${API_BASE}/models/${modelId}`, {
      method: 'DELETE',
    })
    if (!res.ok) throw new Error(`Failed to remove model ${modelId}`)
  }

  async getModelLogs(modelId: string, lines = 100): Promise<string[]> {
    const res = await fetch(`${API_BASE}/models/${modelId}/logs?lines=${lines}`)
    if (!res.ok) throw new Error(`Failed to get logs for ${modelId}`)
    const data = await res.json()
    return data.logs
  }

  // WebSocket for logs
  connectLogsWebSocket(modelId: string, onMessage: (data: any) => void): WebSocket {
    const protocol = window.location.protocol === 'https:' ? 'wss:' : 'ws:'
    const ws = new WebSocket(`${protocol}//${window.location.host}/api/models/ws/logs/${modelId}`)
    
    ws.onmessage = (event) => {
      const data = JSON.parse(event.data)
      onMessage(data)
    }
    
    return ws
  }

  // Chat API
  async chat(
    modelId: string,
    messages: ChatMessage[],
    options: {
      stream?: boolean
      temperature?: number
      max_tokens?: number
    } = {}
  ): Promise<Response> {
    const res = await fetch(`${API_BASE}/chat/completions`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({
        model_id: modelId,
        messages,
        stream: options.stream ?? true,
        temperature: options.temperature ?? 0.7,
        max_tokens: options.max_tokens ?? 2048,
      }),
    })
    
    if (!res.ok) {
      const error = await res.json()
      throw new Error(error.detail || 'Chat request failed')
    }
    
    return res
  }
}

export const api = new ApiClient()

