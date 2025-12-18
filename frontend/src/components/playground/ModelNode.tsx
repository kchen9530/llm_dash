import { memo } from 'react'
import { Handle, Position, NodeProps } from 'reactflow'
import { Edit, Trash2, Brain } from 'lucide-react'

interface ModelNodeData {
  modelId: string
  modelName: string
  promptTemplate: string
  onEdit: (nodeId: string) => void
  onDelete: (nodeId: string) => void
}

function ModelNode({ id, data }: NodeProps<ModelNodeData>) {
  return (
    <div className="relative bg-gray-800 border-2 border-blue-500 rounded-lg shadow-lg min-w-[200px]">
      {/* Input Handle */}
      <Handle
        type="target"
        position={Position.Left}
        className="w-3 h-3 bg-blue-500 border-2 border-white"
      />

      {/* Node Content */}
      <div className="p-3">
        {/* Header */}
        <div className="flex items-center gap-2 mb-2">
          <div className="flex items-center justify-center w-8 h-8 rounded-full bg-blue-600">
            <Brain className="w-4 h-4 text-white" />
          </div>
          <div className="flex-1 min-w-0">
            <div className="text-sm font-semibold text-white truncate">
              {data.modelName}
            </div>
            <div className="text-xs text-gray-400 truncate">
              {id}
            </div>
          </div>
        </div>

        {/* Prompt Preview */}
        <div className="mb-2 p-2 bg-gray-900 rounded border border-gray-700">
          <div className="text-xs text-gray-500 mb-1">Prompt:</div>
          <div className="text-xs text-gray-300 font-mono line-clamp-2">
            {data.promptTemplate || '{input}'}
          </div>
        </div>

        {/* Actions */}
        <div className="flex gap-1">
          <button
            onClick={() => data.onEdit(id)}
            className="flex-1 flex items-center justify-center gap-1 px-2 py-1 text-xs bg-blue-600 hover:bg-blue-700 text-white rounded transition-colors"
          >
            <Edit className="w-3 h-3" />
            Edit
          </button>
          <button
            onClick={() => data.onDelete(id)}
            className="flex items-center justify-center px-2 py-1 text-xs bg-red-600 hover:bg-red-700 text-white rounded transition-colors"
          >
            <Trash2 className="w-3 h-3" />
          </button>
        </div>
      </div>

      {/* Output Handle */}
      <Handle
        type="source"
        position={Position.Right}
        className="w-3 h-3 bg-green-500 border-2 border-white"
      />
    </div>
  )
}

export default memo(ModelNode)
