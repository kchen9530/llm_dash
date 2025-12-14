import { useState, useEffect, useRef } from 'react'
import { useSearchParams } from 'react-router-dom'
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card'
import { Button } from '@/components/ui/button'
import { Input } from '@/components/ui/input'
import { useModelStore } from '@/store/useModelStore'
import { api, ChatMessage } from '@/lib/api'
import { Send, Bot, User, Loader2 } from 'lucide-react'
import { useToast } from '@/components/ui/use-toast'

export default function Chat() {
  const [searchParams] = useSearchParams()
  const { models, fetchModels } = useModelStore()
  const { toast } = useToast()
  
  const [selectedModel, setSelectedModel] = useState<string>('')
  const [messages, setMessages] = useState<ChatMessage[]>([])
  const [input, setInput] = useState('')
  const [loading, setLoading] = useState(false)
  
  const messagesEndRef = useRef<HTMLDivElement>(null)

  useEffect(() => {
    fetchModels()
    const modelId = searchParams.get('model')
    if (modelId) {
      setSelectedModel(modelId)
    }
  }, [fetchModels, searchParams])

  useEffect(() => {
    messagesEndRef.current?.scrollIntoView({ behavior: 'smooth' })
  }, [messages])

  const runningModels = models.filter((m) => m.status === 'RUNNING')

  const handleSend = async () => {
    if (!input.trim() || !selectedModel) return

    const userMessage: ChatMessage = {
      role: 'user',
      content: input.trim(),
    }

    setMessages((prev) => [...prev, userMessage])
    setInput('')
    setLoading(true)

    try {
      const response = await api.chat(selectedModel, [...messages, userMessage], {
        stream: true,
        temperature: 0.7,
        max_tokens: 2048,
      })

      const reader = response.body?.getReader()
      if (!reader) throw new Error('No reader available')

      const decoder = new TextDecoder()
      let assistantMessage = ''

      // 添加助手消息占位符
      setMessages((prev) => [
        ...prev,
        { role: 'assistant', content: '' },
      ])

      while (true) {
        const { done, value } = await reader.read()
        if (done) break

        const chunk = decoder.decode(value)
        const lines = chunk.split('\n')

        for (const line of lines) {
          if (line.startsWith('data: ')) {
            const data = line.slice(6)
            if (data === '[DONE]') continue

            try {
              const parsed = JSON.parse(data)
              const delta = parsed.choices?.[0]?.delta?.content
              if (delta) {
                assistantMessage += delta
                // 更新最后一条消息
                setMessages((prev) => {
                  const newMessages = [...prev]
                  newMessages[newMessages.length - 1] = {
                    role: 'assistant',
                    content: assistantMessage,
                  }
                  return newMessages
                })
              }
            } catch (e) {
              // 忽略解析错误
            }
          }
        }
      }
    } catch (error: any) {
      toast({
        title: 'Chat Error',
        description: error.message,
        variant: 'destructive',
      })
      // 移除占位符消息
      setMessages((prev) => prev.slice(0, -1))
    } finally {
      setLoading(false)
    }
  }

  const handleKeyPress = (e: React.KeyboardEvent) => {
    if (e.key === 'Enter' && !e.shiftKey) {
      e.preventDefault()
      handleSend()
    }
  }

  return (
    <div className="h-full flex flex-col space-y-4">
      {/* Header */}
      <div className="flex justify-between items-center">
        <div>
          <h1 className="text-3xl font-bold text-white">Chat</h1>
          <p className="text-gray-400 mt-1">Test your deployed models</p>
        </div>
        <div className="flex items-center gap-2">
          <label className="text-sm text-gray-400">Model:</label>
          <select
            value={selectedModel}
            onChange={(e) => setSelectedModel(e.target.value)}
            className="h-10 rounded-md border border-gray-700 bg-gray-800 px-3 py-2 text-sm text-white"
            disabled={runningModels.length === 0}
          >
            <option value="">Select a model</option>
            {runningModels.map((model) => (
              <option key={model.id} value={model.id}>
                {model.model_name} (:{model.port})
              </option>
            ))}
          </select>
        </div>
      </div>

      {/* Chat Container */}
      <Card className="glass border-gray-800 flex-1 flex flex-col">
        <CardHeader className="border-b border-gray-800">
          <CardTitle className="text-white flex items-center">
            <Bot className="w-5 h-5 mr-2 text-blue-400" />
            {selectedModel ? `Chatting with ${selectedModel}` : 'Select a model to start'}
          </CardTitle>
        </CardHeader>
        
        <CardContent className="flex-1 flex flex-col p-0">
          {/* Messages */}
          <div className="flex-1 overflow-y-auto p-6 space-y-4">
            {messages.length === 0 ? (
              <div className="text-center text-gray-500 mt-8">
                <Bot className="w-16 h-16 mx-auto mb-4 text-gray-600" />
                <p>Start a conversation with your LLM</p>
              </div>
            ) : (
              messages.map((msg, idx) => (
                <div
                  key={idx}
                  className={`flex gap-3 ${
                    msg.role === 'user' ? 'justify-end' : 'justify-start'
                  }`}
                >
                  {msg.role === 'assistant' && (
                    <div className="w-8 h-8 rounded-full bg-blue-600 flex items-center justify-center flex-shrink-0">
                      <Bot className="w-5 h-5 text-white" />
                    </div>
                  )}
                  <div
                    className={`max-w-[70%] rounded-lg p-4 ${
                      msg.role === 'user'
                        ? 'bg-blue-600 text-white'
                        : 'bg-gray-800 text-gray-100 border border-gray-700'
                    }`}
                  >
                    <p className="whitespace-pre-wrap">{msg.content}</p>
                  </div>
                  {msg.role === 'user' && (
                    <div className="w-8 h-8 rounded-full bg-green-600 flex items-center justify-center flex-shrink-0">
                      <User className="w-5 h-5 text-white" />
                    </div>
                  )}
                </div>
              ))
            )}
            {loading && messages[messages.length - 1]?.content === '' && (
              <div className="flex gap-3">
                <div className="w-8 h-8 rounded-full bg-blue-600 flex items-center justify-center">
                  <Loader2 className="w-5 h-5 text-white animate-spin" />
                </div>
                <div className="bg-gray-800 border border-gray-700 rounded-lg p-4">
                  <p className="text-gray-400">Thinking...</p>
                </div>
              </div>
            )}
            <div ref={messagesEndRef} />
          </div>

          {/* Input */}
          <div className="border-t border-gray-800 p-4">
            <div className="flex gap-2">
              <Input
                value={input}
                onChange={(e) => setInput(e.target.value)}
                onKeyPress={handleKeyPress}
                placeholder={
                  selectedModel
                    ? 'Type your message... (Press Enter to send)'
                    : 'Select a model first'
                }
                disabled={!selectedModel || loading}
                className="bg-gray-800 border-gray-700 text-white"
              />
              <Button
                onClick={handleSend}
                disabled={!selectedModel || !input.trim() || loading}
                className="bg-blue-600 hover:bg-blue-700"
              >
                {loading ? (
                  <Loader2 className="w-4 h-4 animate-spin" />
                ) : (
                  <Send className="w-4 h-4" />
                )}
              </Button>
            </div>
            {runningModels.length === 0 && (
              <p className="text-xs text-gray-500 mt-2">
                No running models. Deploy a model first.
              </p>
            )}
          </div>
        </CardContent>
      </Card>
    </div>
  )
}

