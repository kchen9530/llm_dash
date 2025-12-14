import { useEffect } from 'react'
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card'
import { Cpu, MemoryStick, Gauge } from 'lucide-react'
import { useSystemStore } from '@/store/useSystemStore'
import { formatBytes } from '@/lib/utils'

export default function SystemStats() {
  const { status, fetchStatus, startPolling, stopPolling } = useSystemStore()

  useEffect(() => {
    startPolling(3000)
    return () => stopPolling()
  }, [startPolling, stopPolling])

  if (!status) {
    return (
      <div className="grid gap-4 md:grid-cols-3">
        {[1, 2, 3].map((i) => (
          <Card key={i} className="glass animate-pulse">
            <CardHeader className="pb-2">
              <div className="h-4 bg-gray-700 rounded w-20"></div>
            </CardHeader>
            <CardContent>
              <div className="h-8 bg-gray-700 rounded w-16"></div>
            </CardContent>
          </Card>
        ))}
      </div>
    )
  }

  return (
    <div className="grid gap-4 md:grid-cols-3">
      {/* CPU */}
      <Card className="glass border-gray-800">
        <CardHeader className="flex flex-row items-center justify-between pb-2">
          <CardTitle className="text-sm font-medium text-gray-300">CPU Usage</CardTitle>
          <Cpu className="w-4 h-4 text-blue-400" />
        </CardHeader>
        <CardContent>
          <div className="text-2xl font-bold text-white">
            {status.cpu_percent.toFixed(1)}%
          </div>
          <div className="mt-2 h-2 bg-gray-700 rounded-full overflow-hidden">
            <div
              className="h-full bg-gradient-to-r from-blue-500 to-blue-600 transition-all duration-500"
              style={{ width: `${Math.min(status.cpu_percent, 100)}%` }}
            />
          </div>
        </CardContent>
      </Card>

      {/* Memory */}
      <Card className="glass border-gray-800">
        <CardHeader className="flex flex-row items-center justify-between pb-2">
          <CardTitle className="text-sm font-medium text-gray-300">Memory</CardTitle>
          <MemoryStick className="w-4 h-4 text-green-400" />
        </CardHeader>
        <CardContent>
          <div className="text-2xl font-bold text-white">
            {status.memory_percent.toFixed(1)}%
          </div>
          <p className="text-xs text-gray-400 mt-1">
            {status.memory_used_gb.toFixed(1)} / {status.memory_total_gb.toFixed(1)} GB
          </p>
          <div className="mt-2 h-2 bg-gray-700 rounded-full overflow-hidden">
            <div
              className="h-full bg-gradient-to-r from-green-500 to-green-600 transition-all duration-500"
              style={{ width: `${Math.min(status.memory_percent, 100)}%` }}
            />
          </div>
        </CardContent>
      </Card>

      {/* GPU */}
      <Card className="glass border-gray-800">
        <CardHeader className="flex flex-row items-center justify-between pb-2">
          <CardTitle className="text-sm font-medium text-gray-300">
            GPU {status.gpu_info.length > 0 ? `(${status.gpu_info.length})` : ''}
          </CardTitle>
          <Gauge className="w-4 h-4 text-purple-400" />
        </CardHeader>
        <CardContent>
          {status.gpu_info.length > 0 ? (
            <div className="space-y-2">
              {status.gpu_info.map((gpu) => (
                <div key={gpu.id}>
                  <div className="flex justify-between text-sm">
                    <span className="text-white font-semibold">GPU {gpu.id}</span>
                    <span className="text-gray-400">{gpu.memory_percent.toFixed(1)}%</span>
                  </div>
                  <div className="mt-1 h-1.5 bg-gray-700 rounded-full overflow-hidden">
                    <div
                      className="h-full bg-gradient-to-r from-purple-500 to-purple-600 transition-all duration-500"
                      style={{ width: `${Math.min(gpu.memory_percent, 100)}%` }}
                    />
                  </div>
                  <p className="text-xs text-gray-500 mt-0.5">
                    {(gpu.memory_used_mb / 1024).toFixed(1)} / {(gpu.memory_total_mb / 1024).toFixed(1)} GB
                    {gpu.temperature && ` • ${gpu.temperature}°C`}
                  </p>
                </div>
              ))}
            </div>
          ) : (
            <p className="text-sm text-gray-400">No GPU detected</p>
          )}
        </CardContent>
      </Card>
    </div>
  )
}

