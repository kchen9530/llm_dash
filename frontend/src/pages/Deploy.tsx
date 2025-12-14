import { useState, useEffect } from 'react'
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/components/ui/card'
import { Button } from '@/components/ui/button'
import { Input } from '@/components/ui/input'
import { Label } from '@/components/ui/label'
import { useModelStore } from '@/store/useModelStore'
import { useNavigate } from 'react-router-dom'
import { Rocket, Loader2, AlertCircle, Cpu, Zap } from 'lucide-react'
import { useToast } from '@/components/ui/use-toast'
import { api } from '@/lib/api'

const presetModels = [
  { name: 'Qwen/Qwen2-0.5B-Instruct', size: '0.5B', memory: '~1GB', description: 'Tiny model for testing', cpuOk: true },
  { name: 'Qwen/Qwen2-1.5B-Instruct', size: '1.5B', memory: '~3GB', description: 'Small efficient model', cpuOk: true },
  { name: 'Qwen/Qwen2-7B-Instruct', size: '7B', memory: '~14GB', description: 'Production ready', cpuOk: false },
  { name: 'meta-llama/Llama-3-8B-Instruct', size: '8B', memory: '~16GB', description: 'Meta Llama 3', cpuOk: false },
  { name: 'mistralai/Mistral-7B-Instruct-v0.3', size: '7B', memory: '~14GB', description: 'Mistral AI', cpuOk: false },
]

export default function Deploy() {
  const navigate = useNavigate()
  const { toast } = useToast()
  const { deployModel } = useModelStore()
  
  const [loading, setLoading] = useState(false)
  const [computeMode, setComputeMode] = useState<{mode: string, use_gpu: boolean} | null>(null)
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
    // Fetch compute mode on mount
    api.get('/api/system/compute-mode')
      .then(res => setComputeMode(res.data))
      .catch(err => console.error('Failed to fetch compute mode:', err))
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

      {/* Preset Models */}
      <Card className="glass border-gray-800">
        <CardHeader>
          <CardTitle className="text-white">Quick Select</CardTitle>
          <CardDescription>Popular models ready to deploy</CardDescription>
        </CardHeader>
        <CardContent>
          <div className="grid grid-cols-1 md:grid-cols-2 gap-3">
            {presetModels.map((model) => {
              const isCpuMode = computeMode && !computeMode.use_gpu
              const isDisabled = isCpuMode && !model.cpuOk
              
              return (
                <button
                  key={model.name}
                  onClick={() => !isDisabled && selectPreset(model.name)}
                  disabled={isDisabled}
                  className={`p-4 text-left rounded-lg border transition-all ${
                    formData.model_name === model.name
                      ? 'bg-blue-600/20 border-blue-500'
                      : isDisabled
                      ? 'bg-gray-900/30 border-gray-800 opacity-50 cursor-not-allowed'
                      : 'bg-gray-800/30 border-gray-700 hover:border-gray-600'
                  }`}
                >
                  <div className="flex justify-between items-start mb-2">
                    <h3 className="font-semibold text-white text-sm">{model.name.split('/')[1]}</h3>
                    <div className="flex gap-1">
                      <span className="text-xs bg-blue-600 text-white px-2 py-0.5 rounded">
                        {model.size}
                      </span>
                      {model.cpuOk && isCpuMode && (
                        <span className="text-xs bg-green-600 text-white px-2 py-0.5 rounded">
                          CPU OK
                        </span>
                      )}
                    </div>
                  </div>
                  <p className="text-xs text-gray-400">{model.description}</p>
                  <p className="text-xs text-gray-500 mt-1">Memory: {model.memory}</p>
                  {isDisabled && (
                    <p className="text-xs text-amber-400 mt-2 flex items-center gap-1">
                      <AlertCircle className="w-3 h-3" />
                      GPU required
                    </p>
                  )}
                </button>
              )
            })}
          </div>
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

