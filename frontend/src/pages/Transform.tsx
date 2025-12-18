import { useState, useEffect } from 'react'
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/components/ui/card'
import { Button } from '@/components/ui/button'
import { Input } from '@/components/ui/input'
import { Label } from '@/components/ui/label'
import { useToast } from '@/components/ui/use-toast'
import { Loader2, ArrowRight, Sparkles, Code, Info, Zap, Brain, Binary, ChevronRight } from 'lucide-react'
import { api } from '@/lib/api'

interface TransformResult {
  success: boolean
  result: Record<string, any>
  method: string
  model_used?: any
}

interface AvailableMethods {
  rule_based_available: boolean
  llm_available: boolean
  llm_models: Array<{ id: string; name: string; status: string }>
  embed_models: Array<{ id: string; name: string; status: string }>
  recommendation: string
}

export default function Transform() {
  const [inputText, setInputText] = useState('')
  const [schemaHint, setSchemaHint] = useState('')
  const [loading, setLoading] = useState(false)
  const [result, setResult] = useState<TransformResult | null>(null)
  const [availableMethods, setAvailableMethods] = useState<AvailableMethods | null>(null)
  
  // Mode selection
  const [useLLM, setUseLLM] = useState(false)
  
  // Model selections for LLM mode
  const [model1Id, setModel1Id] = useState('')
  const [model2Id, setModel2Id] = useState('')
  const [embedModelId, setEmbedModelId] = useState('')
  
  const { toast } = useToast()

  useEffect(() => {
    fetchAvailableMethods()
    // Refresh methods every 5 seconds
    const interval = setInterval(fetchAvailableMethods, 5000)
    return () => clearInterval(interval)
  }, [])

  // Auto-select first available models when they become available
  useEffect(() => {
    if (availableMethods) {
      if (availableMethods.llm_models.length > 0 && !model1Id) {
        setModel1Id(availableMethods.llm_models[0].id)
        setModel2Id(availableMethods.llm_models[0].id) // Default to same model
      }
      if (availableMethods.embed_models.length > 0 && !embedModelId) {
        setEmbedModelId(availableMethods.embed_models[0].id)
      }
    }
  }, [availableMethods])

  const fetchAvailableMethods = async () => {
    try {
      const response = await fetch('http://localhost:7860/api/transform/methods')
      const data = await response.json()
      setAvailableMethods(data)
    } catch (error) {
      console.error('Failed to fetch methods:', error)
    }
  }

  const canUseLLM = () => {
    return availableMethods?.llm_available && model1Id && model2Id && embedModelId
  }

  const handleTransform = async () => {
    if (!inputText.trim()) {
      toast({
        title: 'Input Required',
        description: 'Please enter some text to transform',
        variant: 'destructive',
      })
      return
    }

    if (useLLM && !canUseLLM()) {
      toast({
        title: 'Models Required',
        description: 'Please select all required models for LLM processing',
        variant: 'destructive',
      })
      return
    }

    setLoading(true)
    setResult(null)

    try {
      const requestBody: any = {
        text: inputText,
        schema_hint: schemaHint || null,
        prefer_llm: useLLM,
      }

      if (useLLM) {
        requestBody.model1_id = model1Id
        requestBody.model2_id = model2Id
        requestBody.embed_model_id = embedModelId
      }

      const response = await fetch('http://localhost:7860/api/transform/text-to-json', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify(requestBody),
      })

      if (!response.ok) {
        const error = await response.json()
        throw new Error(error.detail || 'Transformation failed')
      }

      const data = await response.json()
      setResult(data)
      
      toast({
        title: 'Success',
        description: `Transformed using ${data.method}`,
      })
    } catch (error: any) {
      toast({
        title: 'Transformation Failed',
        description: error.message,
        variant: 'destructive',
      })
    } finally {
      setLoading(false)
    }
  }

  const handleKeyPress = (e: React.KeyboardEvent) => {
    if (e.key === 'Enter' && !e.shiftKey && inputText.trim()) {
      e.preventDefault()
      handleTransform()
    }
  }

  const examples = [
    { text: 'this is a cat', expected: '{"pet": {"category": "cat"}}' },
    { text: 'I have a red car', expected: '{"item": {"color": "red", "type": "car"}}' },
    { text: 'dog named Max', expected: '{"dog": {"name": "Max"}}' },
  ]

  return (
    <div className="h-full flex flex-col space-y-4">
      {/* Header */}
      <div className="flex justify-between items-center">
        <div>
          <h1 className="text-3xl font-bold text-white">Transform</h1>
          <p className="text-gray-400 mt-1">Convert natural language to structured JSON</p>
        </div>
      </div>

      {/* Mode Selection */}
      <Card className="glass border-gray-800">
        <CardHeader>
          <CardTitle className="text-white text-lg">Processing Mode</CardTitle>
          <CardDescription>Choose how to transform text to JSON</CardDescription>
        </CardHeader>
        <CardContent>
          <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
            {/* Rule-based Option */}
            <button
              onClick={() => setUseLLM(false)}
              className={`p-4 rounded-lg border-2 transition-all text-left ${
                !useLLM
                  ? 'border-blue-500 bg-blue-600/20'
                  : 'border-gray-700 bg-gray-800/30 hover:border-gray-600'
              }`}
            >
              <div className="flex items-start gap-3">
                <Zap className={`w-5 h-5 mt-0.5 ${!useLLM ? 'text-blue-400' : 'text-gray-400'}`} />
                <div className="flex-1">
                  <h3 className={`font-semibold mb-1 ${!useLLM ? 'text-white' : 'text-gray-300'}`}>
                    Rule-Based
                  </h3>
                  <p className="text-xs text-gray-400 mb-2">
                    Fast pattern matching • Always available • Deterministic
                  </p>
                  <div className="flex items-center gap-1 text-xs text-green-400">
                    <span className="w-2 h-2 bg-green-400 rounded-full"></span>
                    Ready
                  </div>
                </div>
              </div>
            </button>

            {/* LLM-based Option */}
            <button
              onClick={() => setUseLLM(true)}
              disabled={!availableMethods?.llm_available}
              className={`p-4 rounded-lg border-2 transition-all text-left ${
                useLLM
                  ? 'border-purple-500 bg-purple-600/20'
                  : availableMethods?.llm_available
                  ? 'border-gray-700 bg-gray-800/30 hover:border-gray-600'
                  : 'border-gray-800 bg-gray-900/50 opacity-50 cursor-not-allowed'
              }`}
            >
              <div className="flex items-start gap-3">
                <Brain className={`w-5 h-5 mt-0.5 ${useLLM ? 'text-purple-400' : 'text-gray-400'}`} />
                <div className="flex-1">
                  <h3 className={`font-semibold mb-1 ${useLLM ? 'text-white' : 'text-gray-300'}`}>
                    LLM-Based (3-Step Pipeline)
                  </h3>
                  <p className="text-xs text-gray-400 mb-2">
                    AI-powered • High accuracy • Context-aware
                  </p>
                  {availableMethods?.llm_available ? (
                    <div className="flex items-center gap-1 text-xs text-green-400">
                      <span className="w-2 h-2 bg-green-400 rounded-full"></span>
                      {availableMethods.llm_models.length} LLM + {availableMethods.embed_models.length} Embed
                    </div>
                  ) : (
                    <div className="flex items-center gap-1 text-xs text-yellow-400">
                      <span className="w-2 h-2 bg-yellow-400 rounded-full"></span>
                      Deploy models first
                    </div>
                  )}
                </div>
              </div>
            </button>
          </div>

          {/* LLM Model Selection */}
          {useLLM && availableMethods?.llm_available && (
            <div className="mt-6 p-4 bg-gray-900/50 rounded-lg border border-gray-800">
              <h4 className="text-sm font-semibold text-white mb-4 flex items-center">
                <Sparkles className="w-4 h-4 mr-2 text-purple-400" />
                3-Step Processing Pipeline
              </h4>
              
              <div className="space-y-4">
                {/* Step 1: Category Generation */}
                <div className="flex items-center gap-3">
                  <div className="flex items-center justify-center w-8 h-8 rounded-full bg-blue-600 text-white text-sm font-bold flex-shrink-0">
                    1
                  </div>
                  <div className="flex-1">
                    <Label className="text-xs text-gray-400 mb-1">Category Generation (LLM Model 1)</Label>
                    <select
                      value={model1Id}
                      onChange={(e) => setModel1Id(e.target.value)}
                      className="w-full h-9 rounded-md border border-gray-700 bg-gray-800 px-3 text-sm text-white"
                    >
                      <option value="">Select model...</option>
                      {availableMethods.llm_models.map((model) => (
                        <option key={model.id} value={model.id}>
                          {model.name}
                        </option>
                      ))}
                    </select>
                  </div>
                  <ChevronRight className="w-4 h-4 text-gray-600 flex-shrink-0" />
                </div>

                {/* Step 2: Detail Generation */}
                <div className="flex items-center gap-3">
                  <div className="flex items-center justify-center w-8 h-8 rounded-full bg-green-600 text-white text-sm font-bold flex-shrink-0">
                    2
                  </div>
                  <div className="flex-1">
                    <Label className="text-xs text-gray-400 mb-1">Detail Generation (LLM Model 2)</Label>
                    <select
                      value={model2Id}
                      onChange={(e) => setModel2Id(e.target.value)}
                      className="w-full h-9 rounded-md border border-gray-700 bg-gray-800 px-3 text-sm text-white"
                    >
                      <option value="">Select model...</option>
                      {availableMethods.llm_models.map((model) => (
                        <option key={model.id} value={model.id}>
                          {model.name}
                        </option>
                      ))}
                    </select>
                  </div>
                  <ChevronRight className="w-4 h-4 text-gray-600 flex-shrink-0" />
                </div>

                {/* Step 3: Embedding */}
                <div className="flex items-center gap-3">
                  <div className="flex items-center justify-center w-8 h-8 rounded-full bg-purple-600 text-white text-sm font-bold flex-shrink-0">
                    3
                  </div>
                  <div className="flex-1">
                    <Label className="text-xs text-gray-400 mb-1">Add Embedding Info (Embed Model)</Label>
                    <select
                      value={embedModelId}
                      onChange={(e) => setEmbedModelId(e.target.value)}
                      className="w-full h-9 rounded-md border border-gray-700 bg-gray-800 px-3 text-sm text-white"
                    >
                      <option value="">Select model...</option>
                      {availableMethods.embed_models.map((model) => (
                        <option key={model.id} value={model.id}>
                          {model.name}
                        </option>
                      ))}
                    </select>
                  </div>
                </div>
              </div>

              <p className="text-xs text-gray-500 mt-4 italic">
                💡 Tip: You can use the same LLM for both steps, or different ones for varied perspectives
              </p>
            </div>
          )}
        </CardContent>
      </Card>

      {/* Main Content */}
      <div className="grid grid-cols-1 lg:grid-cols-2 gap-4 flex-1">
        {/* Input Section */}
        <Card className="glass border-gray-800 flex flex-col">
          <CardHeader>
            <CardTitle className="text-white flex items-center">
              <ArrowRight className="w-5 h-5 mr-2 text-blue-400" />
              Input
            </CardTitle>
            <CardDescription>Enter text to transform into JSON</CardDescription>
          </CardHeader>
          <CardContent className="flex-1 flex flex-col gap-4">
            {/* Text Input */}
            <div className="space-y-2">
              <Label htmlFor="input-text" className="text-gray-300">
                Text to Transform
              </Label>
              <Input
                id="input-text"
                value={inputText}
                onChange={(e) => setInputText(e.target.value)}
                onKeyPress={handleKeyPress}
                placeholder="e.g., this is a cat"
                className="bg-gray-800 border-gray-700 text-white h-12 text-base"
              />
            </div>

            {/* Schema Hint (Optional) */}
            <div className="space-y-2">
              <Label htmlFor="schema-hint" className="text-gray-300">
                Schema Hint (Optional)
              </Label>
              <Input
                id="schema-hint"
                value={schemaHint}
                onChange={(e) => setSchemaHint(e.target.value)}
                placeholder='e.g., {"category": {"type": "string"}}'
                className="bg-gray-800 border-gray-700 text-white"
              />
            </div>

            {/* Transform Button */}
            <Button
              onClick={handleTransform}
              disabled={!inputText.trim() || loading || (useLLM && !canUseLLM())}
              className="bg-blue-600 hover:bg-blue-700 w-full h-12"
            >
              {loading ? (
                <>
                  <Loader2 className="w-4 h-4 mr-2 animate-spin" />
                  Processing Pipeline...
                </>
              ) : (
                <>
                  <Sparkles className="w-4 h-4 mr-2" />
                  Transform to JSON
                </>
              )}
            </Button>

            {/* Examples */}
            <div className="mt-auto pt-4 border-t border-gray-800">
              <p className="text-xs text-gray-500 mb-2 flex items-center">
                <Info className="w-3 h-3 mr-1" />
                Try these examples:
              </p>
              <div className="space-y-1">
                {examples.map((example, idx) => (
                  <button
                    key={idx}
                    onClick={() => setInputText(example.text)}
                    className="text-xs text-blue-400 hover:text-blue-300 hover:underline block w-full text-left"
                  >
                    "{example.text}"
                  </button>
                ))}
              </div>
            </div>
          </CardContent>
        </Card>

        {/* Output Section */}
        <Card className="glass border-gray-800 flex flex-col">
          <CardHeader>
            <CardTitle className="text-white flex items-center">
              <Code className="w-5 h-5 mr-2 text-green-400" />
              Output
            </CardTitle>
            <CardDescription>Structured JSON result</CardDescription>
          </CardHeader>
          <CardContent className="flex-1 flex flex-col">
            {result ? (
              <div className="space-y-4 flex-1">
                {/* Result JSON */}
                <div className="bg-gray-900 rounded-lg p-4 border border-gray-700 flex-1 overflow-auto">
                  <pre className="text-green-400 font-mono text-sm">
                    {JSON.stringify(result.result, null, 2)}
                  </pre>
                </div>

                {/* Metadata */}
                <div className="space-y-2">
                  <div className="flex items-center justify-between text-sm">
                    <span className="text-gray-400">Method:</span>
                    <span className={`font-mono ${
                      result.method === 'llm' ? 'text-purple-400' : 'text-blue-400'
                    }`}>
                      {result.method}
                    </span>
                  </div>
                  {result.model_used && result.method === 'llm' && (
                    <div className="text-xs text-gray-500 space-y-1">
                      <div>Step 1: {result.model_used.model1}</div>
                      <div>Step 2: {result.model_used.model2}</div>
                      <div>Step 3: {result.model_used.embed}</div>
                    </div>
                  )}
                  <div className="flex items-center justify-between text-sm">
                    <span className="text-gray-400">Status:</span>
                    <span className="text-green-400 font-semibold">
                      {result.success ? '✓ Success' : '✗ Failed'}
                    </span>
                  </div>
                </div>

                {/* Copy Button */}
                <Button
                  onClick={() => {
                    navigator.clipboard.writeText(JSON.stringify(result.result, null, 2))
                    toast({ title: 'Copied to clipboard!' })
                  }}
                  variant="outline"
                  className="w-full border-gray-700 text-white hover:bg-gray-800"
                >
                  Copy JSON
                </Button>
              </div>
            ) : (
              <div className="flex-1 flex items-center justify-center text-gray-500">
                <div className="text-center">
                  <Code className="w-16 h-16 mx-auto mb-4 text-gray-700" />
                  <p>Transform results will appear here</p>
                  <p className="text-sm mt-2">Enter text and click "Transform to JSON"</p>
                </div>
              </div>
            )}
          </CardContent>
        </Card>
      </div>
    </div>
  )
}

