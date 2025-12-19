import { memo } from 'react'
import { Handle, Position, NodeProps } from 'reactflow'
import { Play } from 'lucide-react'

interface InputNodeData {
  value: string
  onChange: (value: string) => void
}

function InputNode({ data }: NodeProps<InputNodeData>) {
  return (
    <div className="relative bg-gray-800 border-2 border-green-500 rounded-lg shadow-lg min-w-[250px]">
      <div className="p-3">
        <div className="flex items-center gap-2 mb-3">
          <div className="flex items-center justify-center w-8 h-8 rounded-full bg-green-600">
            <Play className="w-4 h-4 text-white" />
          </div>
          <div className="text-sm font-semibold text-white">Input</div>
        </div>

        <textarea
          value={data.value}
          onChange={(e) => data.onChange(e.target.value)}
          placeholder="Enter your input here..."
          className="w-full h-32 bg-gray-900 border border-gray-700 rounded p-2 text-xs text-white resize-none focus:outline-none focus:border-green-500"
          onKeyDown={(e) => {
            // Prevent deleting the node when pressing Backspace/Delete in the textarea
            e.stopPropagation()
          }}
        />
      </div>

      <Handle
        type="source"
        position={Position.Right}
        className="w-3 h-3 bg-green-500 border-2 border-white"
      />
    </div>
  )
}

export default memo(InputNode)
