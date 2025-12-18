import { useState, useCallback, useRef, useEffect } from 'react'
import ReactFlow, {
  Node,
  Edge,
  Controls,
  Background,
  useNodesState,
  useEdgesState,
  addEdge,
  Connection,
  BackgroundVariant,
  Panel,
  NodeTypes,
} from 'reactflow'
import 'reactflow/dist/style.css'
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/components/ui/card'
import { Button } from '@/components/ui/button'
import { Input } from '@/components/ui/input'
import { Textarea } from '@/components/ui/textarea'
import { useToast } from '@/components/ui/use-toast'
import { Play, Trash2, Download, Upload, Loader2, Plus, Info } from 'lucide-react'
import ModelNode from '@/components/playground/ModelNode'

interface AvailableModel {
  id: string
  name: string
  type: string
  status: string
}

interface ExecutionResult {
  success: boolean
  error?: string
  total_execution_time?: number
  layers?: number
  nodes: Record<string, {
    model_id: string
    model_name: string
    output: string | null
    error: string | null
    execution_time: number
  }>
}

const nodeTypes: NodeTypes = {
  modelNode: ModelNode,
}

export default function Playground() {
  const [nodes, setNodes, onNodesChange] = useNodesState([])
  const [edges, setEdges, onEdgesChange] = useEdgesState([])
  const [availableModels, setAvailableModels] = useState<AvailableModel[]>([])
  const [userInput, setUserInput] = useState('')
  const [executing, setExecuting] = useState(false)
  const [executionResult, setExecutionResult] = useState<ExecutionResult | null>(null)
  const [selectedNode, setSelectedNode] = useState<Node | null>(null)
  const [promptTemplate, setPromptTemplate] = useState('')
  const reactFlowWrapper = useRef<HTMLDivElement>(null)
  const { toast } = useToast()

  // Fetch available models
  useEffect(() => {
    fetchAvailableModels()
    const interval = setInterval(fetchAvailableModels, 5000)
    return () => clearInterval(interval)
  }, [])

  const fetchAvailableModels = async () => {
    try {
      const response = await fetch('http://localhost:7860/api/playground/available-models')
      const data = await response.json()
      setAvailableModels(data.models || [])
    } catch (error) {
      console.error('Failed to fetch models:', error)
    }
  }

  // Handle adding edges (allow self-loops)
  const onConnect = useCallback(
    (params: Connection) => setEdges((eds) => addEdge(params, eds)),
    [setEdges]
  )

  // Allow connections including self-loops
  const isValidConnection = useCallback((connection: Connection) => {
    // Allow all connections including self-loops (source === target)
    return true
  }, [])

  // Add a new model node to canvas
  const addModelNode = (model: AvailableModel) => {
    const newNode: Node = {
      id: `node-${Date.now()}`,
      type: 'modelNode',
      position: { x: Math.random() * 300 + 100, y: Math.random() * 300 + 100 },
      data: {
        modelId: model.id,
        modelName: model.name,
        promptTemplate: '{input}',
        onEdit: (nodeId: string) => handleEditNode(nodeId),
        onDelete: (nodeId: string) => handleDeleteNode(nodeId),
      },
    }
    setNodes((nds) => [...nds, newNode])
    
    toast({
      title: 'Node Added',
      description: `${model.name} added to canvas`,
    })
  }

  // Handle node editing
  const handleEditNode = (nodeId: string) => {
    const node = nodes.find((n) => n.id === nodeId)
    if (node) {
      setSelectedNode(node)
      setPromptTemplate(node.data.promptTemplate || '{input}')
    }
  }

  // Update node prompt
  const updateNodePrompt = () => {
    if (!selectedNode) return

    setNodes((nds) =>
      nds.map((node) =>
        node.id === selectedNode.id
          ? { ...node, data: { ...node.data, promptTemplate } }
          : node
      )
    )

    toast({
      title: 'Prompt Updated',
      description: 'Node prompt template has been updated',
    })

    setSelectedNode(null)
    setPromptTemplate('')
  }

  // Delete node
  const handleDeleteNode = (nodeId: string) => {
    setNodes((nds) => nds.filter((n) => n.id !== nodeId))
    setEdges((eds) => eds.filter((e) => e.source !== nodeId && e.target !== nodeId))
  }

  // Clear canvas
  const clearCanvas = () => {
    setNodes([])
    setEdges([])
    setExecutionResult(null)
    toast({
      title: 'Canvas Cleared',
      description: 'All nodes and edges have been removed',
    })
  }

  // Execute workflow
  const executeWorkflow = async () => {
    if (!userInput.trim()) {
      toast({
        title: 'Input Required',
        description: 'Please enter an input for the workflow',
        variant: 'destructive',
      })
      return
    }

    if (nodes.length === 0) {
      toast({
        title: 'No Nodes',
        description: 'Add at least one model node to the canvas',
        variant: 'destructive',
      })
      return
    }

    setExecuting(true)
    setExecutionResult(null)

    try {
      // Build workflow definition
      const workflow = {
        nodes: nodes.map((node) => ({
          id: node.id,
          model_id: node.data.modelId,
          model_name: node.data.modelName,
          prompt_template: node.data.promptTemplate || '{input}',
          position: node.position,
        })),
        edges: edges.map((edge) => ({
          source: edge.source,
          target: edge.target,
          id: edge.id,
        })),
      }

      const response = await fetch('http://localhost:7860/api/playground/execute', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({
          workflow,
          input: userInput,
        }),
      })

      if (!response.ok) {
        const error = await response.json()
        throw new Error(error.detail || 'Execution failed')
      }

      const result: ExecutionResult = await response.json()
      setExecutionResult(result)

      if (result.success) {
        toast({
          title: 'Workflow Completed',
          description: `Executed ${Object.keys(result.nodes).length} nodes in ${result.total_execution_time?.toFixed(2)}s`,
        })
      } else {
        toast({
          title: 'Workflow Failed',
          description: result.error || 'Unknown error',
          variant: 'destructive',
        })
      }
    } catch (error: any) {
      toast({
        title: 'Execution Failed',
        description: error.message,
        variant: 'destructive',
      })
    } finally {
      setExecuting(false)
    }
  }

  // Save workflow
  const saveWorkflow = () => {
    const workflow = {
      nodes: nodes.map((n) => ({
        id: n.id,
        type: n.type,
        position: n.position,
        data: n.data,
      })),
      edges: edges.map((e) => ({
        id: e.id,
        source: e.source,
        target: e.target,
      })),
    }

    const blob = new Blob([JSON.stringify(workflow, null, 2)], { type: 'application/json' })
    const url = URL.createObjectURL(blob)
    const link = document.createElement('a')
    link.href = url
    link.download = `workflow-${Date.now()}.json`
    link.click()
    URL.revokeObjectURL(url)

    toast({
      title: 'Workflow Saved',
      description: 'Workflow has been downloaded',
    })
  }

  // Load workflow
  const loadWorkflow = (event: React.ChangeEvent<HTMLInputElement>) => {
    const file = event.target.files?.[0]
    if (!file) return

    const reader = new FileReader()
    reader.onload = (e) => {
      try {
        const workflow = JSON.parse(e.target?.result as string)
        setNodes(workflow.nodes || [])
        setEdges(workflow.edges || [])
        toast({
          title: 'Workflow Loaded',
          description: `Loaded ${workflow.nodes?.length || 0} nodes`,
        })
      } catch (error) {
        toast({
          title: 'Load Failed',
          description: 'Invalid workflow file',
          variant: 'destructive',
        })
      }
    }
    reader.readAsText(file)
  }

  return (
    <div className="h-full flex gap-4">
      {/* Left Sidebar - Model Palette */}
      <div className="w-56 flex flex-col gap-4">
        <Card className="glass border-gray-800">
          <CardHeader>
            <CardTitle className="text-white text-sm flex items-center">
              <Plus className="w-4 h-4 mr-2" />
              Available Models
            </CardTitle>
            <CardDescription className="text-xs">
              Click to add • Drag to connect • Self-loops allowed
            </CardDescription>
          </CardHeader>
          <CardContent className="space-y-2">
            {availableModels.length === 0 ? (
              <p className="text-xs text-gray-500">No models running</p>
            ) : (
              availableModels.map((model) => (
                <button
                  key={model.id}
                  onClick={() => addModelNode(model)}
                  className="w-full p-3 rounded-lg bg-gray-800 hover:bg-gray-700 border border-gray-700 hover:border-blue-500 transition-all text-left group"
                >
                  <div className="text-sm font-medium text-white group-hover:text-blue-400">
                    {model.name}
                  </div>
                  <div className="text-xs text-gray-500 mt-1">
                    {model.type === 'chat' ? '💬 Chat Model' : '🔢 Embedding'}
                  </div>
                </button>
              ))
            )}
            <div className="pt-3 mt-3 border-t border-gray-700">
              <p className="text-xs text-gray-500 mb-1.5">
                💡 <strong className="text-gray-400">Prompt Variables:</strong>
              </p>
              <p className="text-xs text-gray-500 space-y-0.5">
                <code className="text-blue-400 bg-gray-900 px-1 rounded">{'{input}'}</code> User input<br />
                <code className="text-blue-400 bg-gray-900 px-1 rounded">{'{node-id}'}</code> Node output
              </p>
            </div>
          </CardContent>
        </Card>

      </div>

      {/* Main Canvas */}
      <div className="flex-1 flex flex-col gap-4">
        {/* Controls */}
        <Card className="glass border-gray-800">
          <CardContent className="pt-4">
            <div className="flex gap-2">
              <Input
                value={userInput}
                onChange={(e) => setUserInput(e.target.value)}
                placeholder="Enter your input for the workflow..."
                className="flex-1 bg-gray-800 border-gray-700 text-white"
              />
              <Button
                onClick={executeWorkflow}
                disabled={executing || nodes.length === 0}
                className="bg-green-600 hover:bg-green-700"
              >
                {executing ? (
                  <>
                    <Loader2 className="w-4 h-4 mr-2 animate-spin" />
                    Running
                  </>
                ) : (
                  <>
                    <Play className="w-4 h-4 mr-2" />
                    Run
                  </>
                )}
              </Button>
              <Button
                onClick={clearCanvas}
                variant="outline"
                className="border-gray-700 text-white hover:bg-gray-800"
              >
                <Trash2 className="w-4 h-4" />
              </Button>
              <Button
                onClick={saveWorkflow}
                variant="outline"
                className="border-gray-700 text-white hover:bg-gray-800"
                disabled={nodes.length === 0}
              >
                <Download className="w-4 h-4" />
              </Button>
              <label>
                <input
                  type="file"
                  accept=".json"
                  onChange={loadWorkflow}
                  className="hidden"
                />
                <Button
                  as="span"
                  variant="outline"
                  className="border-gray-700 text-white hover:bg-gray-800 cursor-pointer"
                >
                  <Upload className="w-4 h-4" />
                </Button>
              </label>
            </div>
          </CardContent>
        </Card>

        {/* React Flow Canvas */}
        <div ref={reactFlowWrapper} className="flex-1 bg-gray-950 rounded-lg border border-gray-800 min-h-[600px]">
          <ReactFlow
            nodes={nodes}
            edges={edges}
            onNodesChange={onNodesChange}
            onEdgesChange={onEdgesChange}
            onConnect={onConnect}
            isValidConnection={isValidConnection}
            nodeTypes={nodeTypes}
            fitView
            className="bg-gray-950"
          >
            <Background variant={BackgroundVariant.Dots} gap={20} size={1} color="#374151" />
            <Controls className="bg-gray-800 border-gray-700" />
            <Panel position="top-right" className="bg-gray-900 p-2 rounded-lg border border-gray-800">
              <div className="text-xs text-gray-400">
                <div>Nodes: {nodes.length}</div>
                <div>Edges: {edges.length}</div>
              </div>
            </Panel>
          </ReactFlow>
        </div>
      </div>

      {/* Right Sidebar - Results & Editor */}
      <div className="w-72 flex flex-col gap-4">
        {/* Node Editor */}
        {selectedNode && (
          <Card className="glass border-gray-800">
            <CardHeader>
              <CardTitle className="text-white text-sm">Edit Node Prompt</CardTitle>
              <CardDescription className="text-xs">
                {selectedNode.data.modelName}
              </CardDescription>
            </CardHeader>
            <CardContent className="space-y-3">
              <Textarea
                value={promptTemplate}
                onChange={(e) => setPromptTemplate(e.target.value)}
                placeholder="Enter prompt template..."
                className="bg-gray-800 border-gray-700 text-white min-h-[120px] text-sm font-mono"
              />
              <div className="flex gap-2">
                <Button
                  onClick={updateNodePrompt}
                  className="flex-1 bg-blue-600 hover:bg-blue-700"
                  size="sm"
                >
                  Update
                </Button>
                <Button
                  onClick={() => setSelectedNode(null)}
                  variant="outline"
                  className="border-gray-700 text-white hover:bg-gray-800"
                  size="sm"
                >
                  Cancel
                </Button>
              </div>
            </CardContent>
          </Card>
        )}

        {/* Execution Results */}
        {executionResult && (
          <Card className="glass border-gray-800 flex-1 overflow-auto">
            <CardHeader>
              <CardTitle className="text-white text-sm">Execution Results</CardTitle>
              <CardDescription className="text-xs">
                {executionResult.success ? (
                  <span className="text-green-400">
                    ✓ Completed in {executionResult.total_execution_time?.toFixed(2)}s
                  </span>
                ) : (
                  <span className="text-red-400">✗ Failed</span>
                )}
              </CardDescription>
            </CardHeader>
            <CardContent className="space-y-3">
              {executionResult.success ? (
                Object.entries(executionResult.nodes).map(([nodeId, result]) => (
                  <div key={nodeId} className="bg-gray-900 p-3 rounded-lg border border-gray-800">
                    <div className="flex items-center justify-between mb-2">
                      <span className="text-xs font-semibold text-blue-400">{nodeId}</span>
                      <span className="text-xs text-gray-500">
                        {result.execution_time.toFixed(2)}s
                      </span>
                    </div>
                    <div className="text-xs font-mono text-gray-300 bg-gray-950 p-2 rounded border border-gray-800 max-h-32 overflow-auto">
                      {result.output || result.error || 'No output'}
                    </div>
                  </div>
                ))
              ) : (
                <div className="text-sm text-red-400">{executionResult.error}</div>
              )}
            </CardContent>
          </Card>
        )}

        {!selectedNode && !executionResult && (
          <Card className="glass border-gray-800 flex-1 flex items-center justify-center">
            <CardContent className="text-center text-gray-500">
              <p className="text-sm">No results yet</p>
              <p className="text-xs mt-1">Run a workflow to see results</p>
            </CardContent>
          </Card>
        )}
      </div>
    </div>
  )
}
