import { useEffect, useState } from 'react'
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/components/ui/card'
import { Button } from '@/components/ui/button'
import { useModelStore } from '@/store/useModelStore'
import { useNavigate } from 'react-router-dom'
import { Play, Square, Trash2, Eye, Server, FileText, X } from 'lucide-react'
import StatusBadge from '@/components/StatusBadge'
import SystemStats from '@/components/SystemStats'
import { useToast } from '@/components/ui/use-toast'
import { api } from '@/lib/api'

export default function Dashboard() {
  const { models, fetchModels, stopModel, deleteModel } = useModelStore()
  const navigate = useNavigate()
  const { toast } = useToast()
  const [selectedModelLogs, setSelectedModelLogs] = useState<string | null>(null)
  const [logs, setLogs] = useState<string[]>([])
  const [logsLoading, setLogsLoading] = useState(false)

  useEffect(() => {
    fetchModels()
    const interval = setInterval(fetchModels, 5000)
    return () => clearInterval(interval)
  }, [fetchModels])

  const handleViewLogs = async (modelId: string) => {
    setSelectedModelLogs(modelId)
    setLogsLoading(true)
    try {
      const response = await api.get(`/api/models/${modelId}/logs`)
      setLogs(response.data.logs || [])
    } catch (error: any) {
      toast({
        title: 'Error',
        description: 'Failed to fetch logs',
        variant: 'destructive',
      })
      setLogs([`Error: ${error.message}`])
    } finally {
      setLogsLoading(false)
    }
  }

  const closeLogs = () => {
    setSelectedModelLogs(null)
    setLogs([])
  }

  const handleStop = async (modelId: string) => {
    try {
      await stopModel(modelId)
      toast({
        title: 'Success',
        description: `Model ${modelId} stopped`,
      })
    } catch (error: any) {
      toast({
        title: 'Error',
        description: error.message,
        variant: 'destructive',
      })
    }
  }

  const handleDelete = async (modelId: string) => {
    try {
      await deleteModel(modelId)
      toast({
        title: 'Success',
        description: `Model ${modelId} removed`,
      })
    } catch (error: any) {
      toast({
        title: 'Error',
        description: error.message,
        variant: 'destructive',
      })
    }
  }

  return (
    <div className="space-y-6 h-full">
      {/* Header */}
      <div className="flex justify-between items-center">
        <div>
          <h1 className="text-3xl font-bold text-white">Dashboard</h1>
          <p className="text-gray-400 mt-1">Monitor and manage your LLM instances</p>
        </div>
        <Button
          onClick={() => navigate('/deploy')}
          className="bg-blue-600 hover:bg-blue-700"
        >
          <Play className="w-4 h-4 mr-2" />
          Deploy Model
        </Button>
      </div>

      {/* System Stats */}
      <SystemStats />

      {/* Models List */}
      <Card className="glass border-gray-800">
        <CardHeader>
          <CardTitle className="flex items-center text-white">
            <Server className="w-5 h-5 mr-2" />
            Running Models ({models.length})
          </CardTitle>
          <CardDescription>Active model instances and their status</CardDescription>
        </CardHeader>
        <CardContent>
          {models.length === 0 ? (
            <div className="text-center py-12">
              <Server className="w-16 h-16 mx-auto text-gray-600 mb-4" />
              <p className="text-gray-400 mb-4">No models running</p>
              <Button
                variant="outline"
                onClick={() => navigate('/deploy')}
                className="border-gray-700"
              >
                Deploy Your First Model
              </Button>
            </div>
          ) : (
            <div className="space-y-3">
              {models.map((model) => (
                <div
                  key={model.id}
                  className="flex items-center justify-between p-4 bg-gray-800/50 rounded-lg border border-gray-700 hover:border-gray-600 transition-all"
                >
                  <div className="flex-1">
                    <div className="flex items-center gap-3 mb-2">
                      <h3 className="text-lg font-semibold text-white">{model.model_name}</h3>
                      <StatusBadge status={model.status} />
                    </div>
                    <div className="flex gap-4 text-sm text-gray-400">
                      <span>ID: {model.id}</span>
                      <span>Port: {model.port}</span>
                      {model.pid && <span>PID: {model.pid}</span>}
                      {model.start_time && (
                        <span>
                          Started: {new Date(model.start_time).toLocaleTimeString()}
                        </span>
                      )}
                    </div>
                    {model.error_message && (
                      <p className="text-sm text-red-400 mt-2">⚠️ {model.error_message}</p>
                    )}
                  </div>

                  <div className="flex gap-2">
                    <Button
                      variant="outline"
                      size="sm"
                      onClick={() => navigate(`/chat?model=${model.id}`)}
                      disabled={model.status !== 'RUNNING'}
                      className="border-gray-700"
                    >
                      <Eye className="w-4 h-4 mr-1" />
                      Chat
                    </Button>
                    <Button
                      variant="outline"
                      size="sm"
                      onClick={() => handleViewLogs(model.id)}
                      className="border-gray-700"
                    >
                      <FileText className="w-4 h-4 mr-1" />
                      Logs
                    </Button>
                    <Button
                      variant="outline"
                      size="sm"
                      onClick={() => handleStop(model.id)}
                      disabled={
                        model.status === 'STOPPED' || 
                        model.status === 'STOPPING' ||
                        model.status === 'INITIALIZING' ||
                        model.status === 'STARTING'
                      }
                      className="border-gray-700"
                    >
                      <Square className="w-4 h-4 mr-1" />
                      Stop
                    </Button>
                    <Button
                      variant="destructive"
                      size="sm"
                      onClick={() => handleDelete(model.id)}
                      disabled={
                        model.status === 'RUNNING' ||
                        model.status === 'INITIALIZING' ||
                        model.status === 'STARTING'
                      }
                    >
                      <Trash2 className="w-4 h-4 mr-1" />
                      Remove
                    </Button>
                  </div>
                </div>
              ))}
            </div>
          )}
        </CardContent>
      </Card>

      {/* Logs Modal */}
      {selectedModelLogs && (
        <div className="fixed inset-0 bg-black/80 flex items-center justify-center z-50 p-4">
          <div className="bg-gray-900 rounded-lg border border-gray-700 w-full max-w-4xl max-h-[80vh] flex flex-col">
            {/* Header */}
            <div className="flex items-center justify-between p-4 border-b border-gray-700">
              <div className="flex items-center gap-2">
                <FileText className="w-5 h-5 text-blue-400" />
                <h2 className="text-lg font-semibold text-white">Model Logs</h2>
                <span className="text-sm text-gray-400">({selectedModelLogs})</span>
              </div>
              <Button
                variant="ghost"
                size="sm"
                onClick={closeLogs}
                className="text-gray-400 hover:text-white"
              >
                <X className="w-5 h-5" />
              </Button>
            </div>

            {/* Logs Content */}
            <div className="flex-1 overflow-auto p-4 bg-black/40">
              {logsLoading ? (
                <div className="text-center text-gray-400 py-8">
                  Loading logs...
                </div>
              ) : logs.length === 0 ? (
                <div className="text-center text-gray-400 py-8">
                  No logs available yet
                </div>
              ) : (
                <div className="font-mono text-sm space-y-1">
                  {logs.map((log, index) => (
                    <div
                      key={index}
                      className={`${
                        log.includes('ERROR') || log.includes('❌')
                          ? 'text-red-400'
                          : log.includes('WARNING') || log.includes('⚠️')
                          ? 'text-yellow-400'
                          : log.includes('✅') || log.includes('SUCCESS')
                          ? 'text-green-400'
                          : 'text-gray-300'
                      }`}
                    >
                      {log}
                    </div>
                  ))}
                </div>
              )}
            </div>

            {/* Footer */}
            <div className="p-4 border-t border-gray-700 flex justify-between items-center">
              <span className="text-xs text-gray-400">
                {logs.length} log {logs.length === 1 ? 'entry' : 'entries'}
              </span>
              <Button
                variant="outline"
                size="sm"
                onClick={closeLogs}
                className="border-gray-700"
              >
                Close
              </Button>
            </div>
          </div>
        </div>
      )}
    </div>
  )
}

