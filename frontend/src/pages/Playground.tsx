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
  MiniMap,
} from 'reactflow'
import 'reactflow/dist/style.css'
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/components/ui/card'
import { Button } from '@/components/ui/button'
import { Input } from '@/components/ui/input'
import { Textarea } from '@/components/ui/textarea'
import { useToast } from '@/components/ui/use-toast'
import { Play, Trash2, Download, Upload, Loader2, Plus, Info, PanelLeftOpen, PanelLeftClose, PanelRightOpen, PanelRightClose, Maximize2, Minimize2 } from 'lucide-react'
import ModelNode from '@/components/playground/ModelNode'
import { cn } from '@/lib/utils'

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
  const [leftSidebarOpen, setLeftSidebarOpen] = useState(true)
  const [rightSidebarOpen, setRightSidebarOpen] = useState(true)
  const reactFlowWrapper = useRef<HTMLDivElement>(null)
  const { toast } = useToast()

  const toggleFocusMode = () => {
    if (leftSidebarOpen || rightSidebarOpen) {
      setLeftSidebarOpen(false)
      setRightSidebarOpen(false)
    } else {
      setLeftSidebarOpen(true)
      setRightSidebarOpen(true)
    }
  }

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
      setRightSidebarOpen(true) // Open right sidebar when editing
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
    setRightSidebarOpen(true) // Open right sidebar to show results

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
    <div className="h-full flex relative overflow-hidden">
      {/* Left Sidebar Toggle (when closed) */}
      {!leftSidebarOpen && (
        <Button
          variant="outline"
          size="icon"
          className="absolute left-2 top-4 z-10 border-gray-700 bg-gray-900 text-white hover:bg-gray-800 shadow-md"
          onClick={() => setLeftSidebarOpen(true)}
        >
          <PanelLeftOpen className="w-4 h-4" />
        </Button>
      )}

      {/* Left Sidebar - Model Palette */}
      <div className={cn(
        "flex flex-col transition-all duration-300 ease-in-out overflow-hidden",
        leftSidebarOpen ? "w-64 opacity-100 mr-4" : "w-0 opacity-0 mr-0"
      )}>
        <Card className="glass border-gray-800 h-full flex flex-col">
          <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2 px-4 pt-4">
            <CardTitle className="text-white text-sm flex items-center">
              <Plus className="w-4 h-4 mr-2" />
              Models
            </CardTitle>
            <Button
              variant="ghost"
              size="icon"
              className="h-6 w-6 text-gray-400 hover:text-white"
              onClick={() => setLeftSidebarOpen(false)}
            >
              <PanelLeftClose className="w-4 h-4" />
            </Button>
          </CardHeader>
          <CardDescription className="px-4 text-xs pb-2">
            Click to add • Drag to connect
          </CardDescription>
          <CardContent className="space-y-2 overflow-y-auto flex-1 px-4 pb-4">
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
      <div className="flex-1 flex flex-col min-w-0 h-full">
        {/* Controls */}
        <Card className="glass border-gray-800 mb-4">
          <CardContent className="pt-4 pb-4 px-4">
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
                title="Clear Canvas"
              >
                <Trash2 className="w-4 h-4" />
              </Button>
              <div className="w-px bg-gray-700 mx-1" />
              <Button
                onClick={saveWorkflow}
                variant="outline"
                className="border-gray-700 text-white hover:bg-gray-800"
                disabled={nodes.length === 0}
                title="Save Workflow"
              >
                <Download className="w-4 h-4" />
              </Button>
              <label className="cursor-pointer">
                <input
                  type="file"
                  accept=".json"
                  onChange={loadWorkflow}
                  className="hidden"
                  />
                <div className={cn(
                    "inline-flex items-center justify-center whitespace-nowrap rounded-md text-sm font-medium ring-offset-background transition-colors focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-ring focus-visible:ring-offset-2 disabled:pointer-events-none disabled:opacity-50 border border-gray-700 text-white hover:bg-gray-800 h-10 w-10"
                  )}
                  title="Load Workflow"
                >
                  <Upload className="w-4 h-4" />
                </div>
              </label>
              <div className="w-px bg-gray-700 mx-1" />
              <Button
                onClick={toggleFocusMode}
                variant={(!leftSidebarOpen && !rightSidebarOpen) ? "secondary" : "outline"}
                className={cn(
                  "border-gray-700 text-white hover:bg-gray-800",
                  (!leftSidebarOpen && !rightSidebarOpen) && "bg-blue-900/50 border-blue-500 text-blue-100"
                )}
                title={(!leftSidebarOpen && !rightSidebarOpen) ? "Exit Focus Mode" : "Enter Focus Mode (Maximize Canvas)"}
              >
                {(!leftSidebarOpen && !rightSidebarOpen) ? (
                  <Minimize2 className="w-4 h-4" />
                ) : (
                  <Maximize2 className="w-4 h-4" />
                )}
              </Button>
            </div>
          </CardContent>
        </Card>

        {/* React Flow Canvas */}
        <div ref={reactFlowWrapper} className="flex-1 bg-gray-950 rounded-lg border border-gray-800 h-full relative overflow-hidden shadow-inner">
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
            <MiniMap 
                className="bg-gray-900 border border-gray-800 rounded-lg"
                nodeColor={(node) => '#1f2937'}
                maskColor="rgba(0, 0, 0, 0.7)"
            />
            <Panel position="top-right" className="bg-gray-900 p-2 rounded-lg border border-gray-800">
              <div className="text-xs text-gray-400">
                <div>Nodes: {nodes.length}</div>
                <div>Edges: {edges.length}</div>
              </div>
            </Panel>
          </ReactFlow>
        </div>
      </div>

      {/* Right Sidebar Toggle (when closed) */}
      {!rightSidebarOpen && (
        <Button
          variant="outline"
          size="icon"
          className="absolute right-2 top-4 z-10 border-gray-700 bg-gray-900 text-white hover:bg-gray-800 shadow-md"
          onClick={() => setRightSidebarOpen(true)}
        >
          <PanelRightOpen className="w-4 h-4" />
        </Button>
      )}

      {/* Right Sidebar - Results & Editor */}
      <div className={cn(
        "flex flex-col transition-all duration-300 ease-in-out overflow-hidden",
        rightSidebarOpen ? "w-80 opacity-100 ml-4" : "w-0 opacity-0 ml-0"
      )}>
        {/* Node Editor */}
        {selectedNode && (
          <Card className="glass border-gray-800 flex-shrink-0">
            <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
              <div>
                <CardTitle className="text-white text-sm">Edit Node Prompt</CardTitle>
                <CardDescription className="text-xs">
                  {selectedNode.data.modelName}
                </CardDescription>
              </div>
              <Button
                variant="ghost"
                size="icon"
                className="h-6 w-6 text-gray-400 hover:text-white"
                onClick={() => setRightSidebarOpen(false)}
              >
                <PanelRightClose className="w-4 h-4" />
              </Button>
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
          <Card className="glass border-gray-800 flex-1 overflow-hidden flex flex-col">
            <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
              <div>
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
              </div>
              {!selectedNode && (
                <Button
                  variant="ghost"
                  size="icon"
                  className="h-6 w-6 text-gray-400 hover:text-white"
                  onClick={() => setRightSidebarOpen(false)}
                >
                  <PanelRightClose className="w-4 h-4" />
                </Button>
              )}
            </CardHeader>
            <CardContent className="space-y-3 overflow-y-auto flex-1">
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
          <Card className="glass border-gray-800 flex-1 flex items-center justify-center relative">
            <Button
              variant="ghost"
              size="icon"
              className="absolute top-2 right-2 h-6 w-6 text-gray-400 hover:text-white"
              onClick={() => setRightSidebarOpen(false)}
            >
              <PanelRightClose className="w-4 h-4" />
            </Button>
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
