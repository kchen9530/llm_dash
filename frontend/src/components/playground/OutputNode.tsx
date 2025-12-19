import { memo } from 'react'
import { Handle, Position, NodeProps } from 'reactflow'
import { Terminal } from 'lucide-react'

interface OutputNodeData {
  output?: string
  loading?: boolean
  error?: string
}

function OutputNode({ data }: NodeProps<OutputNodeData>) {
  return (
    <div className="relative bg-gray-800 border-2 border-purple-500 rounded-lg shadow-lg min-w-[250px] max-w-[400px]">
      <Handle
        type="target"
        position={Position.Left}
        className="w-3 h-3 bg-purple-500 border-2 border-white"
      />

      <div className="p-3">
        <div className="flex items-center gap-2 mb-3">
          <div className="flex items-center justify-center w-8 h-8 rounded-full bg-purple-600">
            <Terminal className="w-4 h-4 text-white" />
          </div>
          <div className="text-sm font-semibold text-white">Output</div>
        </div>

        <div className="bg-gray-900 border border-gray-700 rounded p-2 min-h-[128px] max-h-[400px] overflow-auto">
          {data.loading ? (
            <div className="flex items-center justify-center h-full text-gray-500 text-xs">
              <span className="animate-pulse">Waiting for output...</span>
            </div>
          ) : data.error ? (
            <div className="text-red-400 text-xs font-mono whitespace-pre-wrap">
              Error: {data.error}
            </div>
          ) : data.output ? (
            <div className="text-gray-300 text-xs font-mono whitespace-pre-wrap">
              {data.output}
            </div>
          ) : (
            <div className="text-gray-500 text-xs italic">
              Connect a node and run the workflow to see output...
            </div>
          )}
        </div>
      </div>
    </div>
  )
}

export default memo(OutputNode)
