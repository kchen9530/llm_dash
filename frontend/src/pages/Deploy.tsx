import { useState, useEffect } from 'react'
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/components/ui/card'
import { Button } from '@/components/ui/button'
import { Input } from '@/components/ui/input'
import { Label } from '@/components/ui/label'
import { Tabs, TabsContent, TabsList, TabsTrigger } from '@/components/ui/tabs'
import { useModelStore } from '@/store/useModelStore'
import { useNavigate } from 'react-router-dom'
import { Rocket, Loader2, AlertCircle, Cpu, Zap, MessageSquare, Binary } from 'lucide-react'
import { useToast } from '@/components/ui/use-toast'
import { api } from '@/lib/api'

interface RecommendedModel {
  type: string
  size: string
  display_name?: string
  label?: string
  size_mb: number
  ram_mb: number
  speed: string
  quality?: string
  dimensions?: number
  description: string
  recommended_for: string
  downloaded?: boolean
  download_size?: string
  family?: string
  requires_gpu?: boolean
}

interface RecommendedModels {
  chat_models: Record<string, RecommendedModel>
  embedding_models: Record<string, RecommendedModel>
  note: string
}

interface DownloadedModel {
  name: string
  path: string
  size: string
}

interface DownloadedModels {
  chat: DownloadedModel[]
  embedding: DownloadedModel[]
}

export default function Deploy() {
  const navigate = useNavigate()
  const { toast } = useToast()
  const { deployModel } = useModelStore()
  
  const [loading, setLoading] = useState(false)
  const [computeMode, setComputeMode] = useState<{mode: string, use_gpu: boolean} | null>(null)
  const [recommendations, setRecommendations] = useState<RecommendedModels | null>(null)
  const [downloaded, setDownloaded] = useState<DownloadedModels | null>(null)
  const [formData, setFormData] = useState({
    model_name: '',
    local_path: '',
    port: '',
    gpu_memory_utilization: '0.85',
    max_model_len: '4096',
    dtype: 'auto',
    trust_remote_code: true,
  })

  useEffect(() => {
    // Fetch compute mode, recommendations, and downloaded models on mount
    api.get('/api/system/compute-mode')
      .then(res => {
        console.log('✅ Compute mode loaded:', res.data)
        setComputeMode(res.data)
      })
      .catch(err => console.error('❌ Failed to fetch compute mode:', err))
    
    api.get('/api/recommendations/models')
      .then(res => {
        console.log('✅ Recommendations loaded:', res.data)
        console.log('✅ Chat models count:', Object.keys(res.data.chat_models || {}).length)
        setRecommendations(res.data)
      })
      .catch(err => console.error('❌ Failed to fetch recommendations:', err))
    
    api.get('/api/recommendations/downloaded')
      .then(res => {
        console.log('✅ Downloaded models loaded:', res.data)
        setDownloaded(res.data)
      })
      .catch(err => console.error('❌ Failed to fetch downloaded models:', err))
  }, [])

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault()
    
    if (!formData.model_name) {
      toast({
        title: 'Error',
        description: 'Please enter a model name',
        variant: 'destructive',
      })
      return
    }

    setLoading(true)
    
    try {
      const deployRequest = {
        model_name: formData.model_name,
        local_path: formData.local_path || undefined,
        port: formData.port ? parseInt(formData.port) : undefined,
        parameters: {
          dtype: formData.dtype,
          gpu_memory_utilization: parseFloat(formData.gpu_memory_utilization),
          max_model_len: parseInt(formData.max_model_len),
          trust_remote_code: formData.trust_remote_code,
        },
      }

      await deployModel(deployRequest)
      
      toast({
        title: 'Success!',
        description: `Deploying ${formData.model_name}`,
      })
      
      navigate('/')
    } catch (error: any) {
      toast({
        title: 'Deployment Failed',
        description: error.message,
        variant: 'destructive',
      })
    } finally {
      setLoading(false)
    }
  }

  const selectPreset = (modelName: string) => {
    setFormData({ ...formData, model_name: modelName })
  }

  return (
    <div className="space-y-6 max-w-4xl mx-auto">
      {/* Header */}
      <div>
        <h1 className="text-3xl font-bold text-white">Deploy Model</h1>
        <p className="text-gray-400 mt-1">
          Launch a new LLM instance {computeMode?.use_gpu ? 'on your GPU' : 'on CPU'}
        </p>
      </div>

      {/* Compute Mode Warning */}
      {computeMode && !computeMode.use_gpu && (
        <div className="bg-amber-600/20 border border-amber-600/40 rounded-lg p-4 flex items-start gap-3">
          <Cpu className="w-5 h-5 text-amber-400 flex-shrink-0 mt-0.5" />
          <div className="flex-1">
            <h3 className="text-amber-300 font-semibold mb-1">
              CPU Mode - Testing Only
            </h3>
            <p className="text-amber-200/80 text-sm">
              Currently running in CPU mode for reference testing. Only small models (0.5B-1.5B) are recommended. 
              Inference will be slow (5-30s per response).
            </p>
            <p className="text-amber-200/60 text-xs mt-2">
              💡 To enable GPU: Set <code className="bg-black/30 px-1 rounded">FORCE_CPU_MODE=False</code> in backend/.env
            </p>
          </div>
        </div>
      )}

      {/* GPU Mode Indicator */}
      {computeMode && computeMode.use_gpu && (
        <div className="bg-green-600/20 border border-green-600/40 rounded-lg p-4 flex items-center gap-3">
          <Zap className="w-5 h-5 text-green-400" />
          <div>
            <h3 className="text-green-300 font-semibold">
              GPU Acceleration Enabled
            </h3>
            <p className="text-green-200/80 text-sm">
              Ready to deploy production-grade models with fast inference
            </p>
          </div>
        </div>
      )}

      {/* Recommended Models */}
      <Card className="glass border-gray-800">
        <CardHeader>
          <CardTitle className="text-white flex items-center gap-2">
            <Rocket className="w-5 h-5" />
            Recommended for 8GB RAM
          </CardTitle>
          <CardDescription>Pre-optimized models for your system</CardDescription>
        </CardHeader>
        <CardContent>
          <Tabs defaultValue="chat" className="w-full">
            <TabsList className="grid w-full grid-cols-2 bg-gray-800/50">
              <TabsTrigger value="chat" className="data-[state=active]:bg-blue-600">
                <MessageSquare className="w-4 h-4 mr-2" />
                Chat Models
              </TabsTrigger>
              <TabsTrigger value="embedding" className="data-[state=active]:bg-purple-600">
                <Binary className="w-4 h-4 mr-2" />
                Embedding Models
              </TabsTrigger>
            </TabsList>

            {/* Chat Models */}
            <TabsContent value="chat" className="mt-4">
              {!recommendations && <p className="text-gray-400 p-4">Loading models...</p>}
              {recommendations && !recommendations.chat_models && <p className="text-red-400 p-4">No chat_models field!</p>}
              {recommendations && recommendations.chat_models && Object.keys(recommendations.chat_models).length === 0 && <p className="text-yellow-400 p-4">No chat models found!</p>}
              <div className="grid grid-cols-1 md:grid-cols-2 gap-3">
                {recommendations && recommendations.chat_models && Object.entries(recommendations.chat_models).map(([name, info]) => {
                  const isDownloaded = info.downloaded || false
                  const isCpuMode = computeMode && !computeMode.use_gpu
                  const needsGpu = info.requires_gpu || false
                  const isDisabled = isCpuMode && needsGpu
                  
                  return (
                    <button
                      key={name}
                      onClick={() => !isDisabled && selectPreset(name)}
                      disabled={isDisabled}
                      className={`p-5 text-left rounded-lg border-2 transition-all ${
                        formData.model_name === name
                          ? isDownloaded ? 'bg-green-600/20 border-green-500 shadow-lg' : 'bg-blue-600/20 border-blue-500 shadow-lg'
                          : isDisabled
                          ? 'bg-gray-900/30 border-gray-800 opacity-50 cursor-not-allowed'
                          : isDownloaded
                          ? 'bg-gray-800/30 border-green-700/50 hover:border-green-600 hover:shadow-md'
                          : 'bg-gray-800/30 border-gray-700/50 hover:border-blue-500 hover:shadow-md'
                      }`}
                    >
                      {/* Title and badges */}
                      <div className="flex justify-between items-start mb-3">
                        <div>
                          <h3 className="font-bold text-white text-base mb-1">
                            {info.display_name || name.split('/').pop()}
                          </h3>
                          <p className="text-xs text-gray-400 italic">
                            {info.label || info.description}
                          </p>
                        </div>
                        <div className="flex gap-1 flex-wrap justify-end">
                          <span className="text-xs bg-blue-600 text-white px-2 py-0.5 rounded font-semibold">
                            {info.size}
                          </span>
                          {isDownloaded ? (
                            <span className="text-xs bg-green-600 text-white px-2 py-0.5 rounded font-semibold">
                              ✓ Downloaded
                            </span>
                          ) : (
                            <span className="text-xs bg-gray-600 text-white px-2 py-0.5 rounded">
                              Not Downloaded
                            </span>
                          )}
                        </div>
                      </div>
                      
                      {/* Stats */}
                      <div className="flex items-center gap-3 text-xs text-gray-400 mb-2 flex-wrap">
                        {isDownloaded && info.download_size && (
                          <span className="text-green-400 font-semibold">💾 {info.download_size}</span>
                        )}
                        <span>RAM: ~{Math.round(info.ram_mb / 1024 * 10) / 10}GB</span>
                        <span>Speed: {info.speed}</span>
                        {info.quality && <span>Quality: {info.quality}</span>}
                      </div>
                      
                      {/* Action text */}
                      <p className={`text-sm font-semibold mt-3 ${isDownloaded ? 'text-green-400' : 'text-blue-400'}`}>
                        {isDownloaded ? '⚡ Click to deploy instantly!' : `💡 Click to deploy (will download)`}
                      </p>
                      
                      {isDisabled && (
                        <p className="text-xs text-amber-400 mt-2 flex items-center gap-1 font-semibold">
                          <AlertCircle className="w-3 h-3" />
                          Requires GPU server
                        </p>
                      )}
                    </button>
                  )
                })}
              </div>
            </TabsContent>

            {/* Embedding Models */}
            <TabsContent value="embedding" className="mt-4">
              <div className="grid grid-cols-1 md:grid-cols-2 gap-3">
                {recommendations && Object.entries(recommendations.embedding_models).map(([name, info]) => {
                  const isDownloaded = info.downloaded || false
                  
                  return (
                    <button
                      key={name}
                      onClick={() => selectPreset(name)}
                      className={`p-4 text-left rounded-lg border transition-all ${
                        formData.model_name === name
                          ? isDownloaded ? 'bg-green-600/20 border-green-500' : 'bg-purple-600/20 border-purple-500'
                          : isDownloaded
                          ? 'bg-gray-800/30 border-green-700 hover:border-green-600'
                          : 'bg-gray-800/30 border-gray-700 hover:border-gray-600'
                      }`}
                    >
                      <div className="flex justify-between items-start mb-2">
                        <h3 className="font-semibold text-white text-sm truncate pr-2">{name.split('/').pop()}</h3>
                        <div className="flex gap-1 flex-shrink-0 flex-wrap justify-end">
                          <span className="text-xs bg-purple-600 text-white px-2 py-0.5 rounded">
                            {info.size}
                          </span>
                          {isDownloaded ? (
                            <span className="text-xs bg-green-600 text-white px-2 py-0.5 rounded">
                              ✓ Downloaded
                            </span>
                          ) : (
                            <span className="text-xs bg-gray-600 text-white px-2 py-0.5 rounded">
                              Not Downloaded
                            </span>
                          )}
                        </div>
                      </div>
                      <p className="text-xs text-gray-400 mb-1">{info.description}</p>
                      <div className="flex items-center gap-3 text-xs text-gray-500 mt-2 flex-wrap">
                        {isDownloaded && info.download_size && (
                          <span className="text-green-400">💾 {info.download_size}</span>
                        )}
                        <span>RAM: ~{Math.round(info.ram_mb)}MB</span>
                        <span>Dim: {info.dimensions}</span>
                        <span>Speed: {info.speed}</span>
                      </div>
                      <p className={`text-xs mt-2 ${isDownloaded ? 'text-green-400' : 'text-purple-400'}`}>
                        {isDownloaded ? '⚡ Ready to deploy!' : `💡 ${info.recommended_for}`}
                      </p>
                    </button>
                  )
                })}
              </div>
              <div className="mt-4 p-3 bg-purple-600/10 border border-purple-600/30 rounded-lg">
                <p className="text-xs text-purple-300">
                  <Binary className="w-3 h-3 inline mr-1" />
                  <strong>Note:</strong> Embedding models output vectors (floats), not chat responses. 
                  Use them in Photo Search tab, not Chat tab.
                </p>
              </div>
            </TabsContent>
          </Tabs>
        </CardContent>
      </Card>

      {/* Deploy Form */}
      <Card className="glass border-gray-800">
        <CardHeader>
          <CardTitle className="text-white">Configuration</CardTitle>
          <CardDescription>Customize deployment parameters</CardDescription>
        </CardHeader>
        <CardContent>
          <form onSubmit={handleSubmit} className="space-y-6">
            {/* Model Name */}
            <div className="space-y-2">
              <Label htmlFor="model_name" className="text-white">
                Model Name <span className="text-red-500">*</span>
              </Label>
              <Input
                id="model_name"
                placeholder="e.g., Qwen/Qwen2-0.5B-Instruct"
                value={formData.model_name}
                onChange={(e) => setFormData({ ...formData, model_name: e.target.value })}
                className="bg-gray-800 border-gray-700 text-white"
                required
              />
              <p className="text-xs text-gray-500">HuggingFace model ID or local path</p>
            </div>

            {/* Local Path (Optional) */}
            <div className="space-y-2">
              <Label htmlFor="local_path" className="text-white">
                Local Path (Optional)
              </Label>
              <Input
                id="local_path"
                placeholder="/path/to/model"
                value={formData.local_path}
                onChange={(e) => setFormData({ ...formData, local_path: e.target.value })}
                className="bg-gray-800 border-gray-700 text-white"
              />
              <p className="text-xs text-gray-500">Use local model if already downloaded</p>
            </div>

            {/* Advanced Settings */}
            <div className="grid grid-cols-2 gap-4">
              <div className="space-y-2">
                <Label htmlFor="port" className="text-white">Port (Optional)</Label>
                <Input
                  id="port"
                  type="number"
                  placeholder="Auto-assign"
                  value={formData.port}
                  onChange={(e) => setFormData({ ...formData, port: e.target.value })}
                  className="bg-gray-800 border-gray-700 text-white"
                />
              </div>

              <div className="space-y-2">
                <Label htmlFor="gpu_memory" className="text-white">GPU Memory</Label>
                <Input
                  id="gpu_memory"
                  type="number"
                  step="0.05"
                  min="0.1"
                  max="1.0"
                  value={formData.gpu_memory_utilization}
                  onChange={(e) => setFormData({ ...formData, gpu_memory_utilization: e.target.value })}
                  className="bg-gray-800 border-gray-700 text-white"
                />
              </div>

              <div className="space-y-2">
                <Label htmlFor="max_len" className="text-white">Max Context Length</Label>
                <Input
                  id="max_len"
                  type="number"
                  value={formData.max_model_len}
                  onChange={(e) => setFormData({ ...formData, max_model_len: e.target.value })}
                  className="bg-gray-800 border-gray-700 text-white"
                />
              </div>

              <div className="space-y-2">
                <Label htmlFor="dtype" className="text-white">Data Type</Label>
                <select
                  id="dtype"
                  value={formData.dtype}
                  onChange={(e) => setFormData({ ...formData, dtype: e.target.value })}
                  className="flex h-10 w-full rounded-md border border-gray-700 bg-gray-800 px-3 py-2 text-sm text-white"
                >
                  <option value="auto">Auto</option>
                  <option value="float16">Float16</option>
                  <option value="bfloat16">BFloat16</option>
                  <option value="float32">Float32</option>
                </select>
              </div>
            </div>

            {/* Trust Remote Code */}
            <div className="flex items-center space-x-2">
              <input
                type="checkbox"
                id="trust_remote_code"
                checked={formData.trust_remote_code}
                onChange={(e) => setFormData({ ...formData, trust_remote_code: e.target.checked })}
                className="w-4 h-4 text-blue-600 bg-gray-800 border-gray-700 rounded focus:ring-blue-500"
              />
              <Label htmlFor="trust_remote_code" className="text-white cursor-pointer">
                Trust Remote Code
              </Label>
            </div>

            {/* Submit */}
            <div className="flex gap-3 pt-4">
              <Button
                type="submit"
                disabled={loading}
                className="flex-1 bg-blue-600 hover:bg-blue-700"
              >
                {loading ? (
                  <>
                    <Loader2 className="w-4 h-4 mr-2 animate-spin" />
                    Deploying...
                  </>
                ) : (
                  <>
                    <Rocket className="w-4 h-4 mr-2" />
                    Deploy Model
                  </>
                )}
              </Button>
              <Button
                type="button"
                variant="outline"
                onClick={() => navigate('/')}
                disabled={loading}
                className="border-gray-700"
              >
                Cancel
              </Button>
            </div>
          </form>
        </CardContent>
      </Card>
    </div>
  )
}

