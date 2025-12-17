import { useState, useEffect } from 'react'
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/components/ui/card'
import { Button } from '@/components/ui/button'
import { Input } from '@/components/ui/input'
import { Label } from '@/components/ui/label'
import { useToast } from '@/components/ui/use-toast'
import { Loader2, ArrowRight, Sparkles, Code, Info } from 'lucide-react'
import { api } from '@/lib/api'

interface TransformResult {
  success: boolean
  result: Record<string, any>
  method: string
  model_used?: string
}

export default function Transform() {
  const [inputText, setInputText] = useState('')
  const [schemaHint, setSchemaHint] = useState('')
  const [loading, setLoading] = useState(false)
  const [result, setResult] = useState<TransformResult | null>(null)
  const [availableMethods, setAvailableMethods] = useState<any>(null)
  const { toast } = useToast()

  useEffect(() => {
    fetchAvailableMethods()
  }, [])

  const fetchAvailableMethods = async () => {
    try {
      const response = await fetch('http://localhost:7860/api/transform/methods')
      const data = await response.json()
      setAvailableMethods(data)
    } catch (error) {
      console.error('Failed to fetch methods:', error)
    }
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

    setLoading(true)
    setResult(null)

    try {
      const response = await fetch('http://localhost:7860/api/transform/text-to-json', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({
          text: inputText,
          schema_hint: schemaHint || null,
          prefer_llm: true,
        }),
      })

      if (!response.ok) {
        const error = await response.json()
        throw new Error(error.detail || 'Transformation failed')
      }

      const data = await response.json()
      setResult(data)
      
      toast({
        title: 'Success',
        description: `Transformed using ${data.method}${data.model_used ? ` (${data.model_used})` : ''}`,
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
        {availableMethods && (
          <div className="flex items-center gap-2 text-sm">
            <div className={`px-3 py-1 rounded-full ${
              availableMethods.llm_available 
                ? 'bg-green-900 text-green-300' 
                : 'bg-yellow-900 text-yellow-300'
            }`}>
              {availableMethods.llm_available ? (
                <span className="flex items-center gap-1">
                  <Sparkles className="w-3 h-3" />
                  LLM Available
                </span>
              ) : (
                <span>Rule-based Only</span>
              )}
            </div>
          </div>
        )}
      </div>

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
              disabled={!inputText.trim() || loading}
              className="bg-blue-600 hover:bg-blue-700 w-full h-12"
            >
              {loading ? (
                <>
                  <Loader2 className="w-4 h-4 mr-2 animate-spin" />
                  Transforming...
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
                <div className="bg-gray-900 rounded-lg p-4 border border-gray-700 flex-1">
                  <pre className="text-green-400 font-mono text-sm overflow-auto">
                    {JSON.stringify(result.result, null, 2)}
                  </pre>
                </div>

                {/* Metadata */}
                <div className="space-y-2">
                  <div className="flex items-center justify-between text-sm">
                    <span className="text-gray-400">Method:</span>
                    <span className="text-white font-mono">{result.method}</span>
                  </div>
                  {result.model_used && (
                    <div className="flex items-center justify-between text-sm">
                      <span className="text-gray-400">Model:</span>
                      <span className="text-white font-mono">{result.model_used}</span>
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
                  className="w-full border-gray-700"
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

      {/* Info Banner */}
      {availableMethods && !availableMethods.llm_available && (
        <Card className="glass border-yellow-900 bg-yellow-900/10">
          <CardContent className="pt-4">
            <div className="flex items-start gap-3">
              <Info className="w-5 h-5 text-yellow-400 mt-0.5" />
              <div className="flex-1">
                <p className="text-yellow-300 text-sm font-semibold">Rule-based Mode Active</p>
                <p className="text-yellow-400/80 text-xs mt-1">
                  No LLM models are currently running. Using simple pattern matching rules.
                  Deploy a model for better results with complex queries.
                </p>
              </div>
            </div>
          </CardContent>
        </Card>
      )}
    </div>
  )
}


