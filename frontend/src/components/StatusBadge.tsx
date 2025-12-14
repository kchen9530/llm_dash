import { Badge } from '@/components/ui/badge'
import { Loader2 } from 'lucide-react'

interface StatusBadgeProps {
  status: string
}

const statusConfig: Record<string, { variant: any; label: string; icon?: React.ReactNode }> = {
  RUNNING: {
    variant: 'success',
    label: 'Running',
  },
  STARTING: {
    variant: 'warning',
    label: 'Starting',
    icon: <Loader2 className="w-3 h-3 animate-spin mr-1" />,
  },
  INITIALIZING: {
    variant: 'warning',
    label: 'Initializing',
    icon: <Loader2 className="w-3 h-3 animate-spin mr-1" />,
  },
  DOWNLOADING: {
    variant: 'warning',
    label: 'Downloading',
    icon: <Loader2 className="w-3 h-3 animate-spin mr-1" />,
  },
  STOPPING: {
    variant: 'warning',
    label: 'Stopping',
  },
  STOPPED: {
    variant: 'secondary',
    label: 'Stopped',
  },
  ERROR: {
    variant: 'destructive',
    label: 'Error',
  },
  FAILED: {
    variant: 'destructive',
    label: 'Failed',
  },
}

export default function StatusBadge({ status }: StatusBadgeProps) {
  const config = statusConfig[status] || statusConfig.STOPPED

  return (
    <Badge variant={config.variant} className="flex items-center">
      {config.icon}
      {config.label}
    </Badge>
  )
}

