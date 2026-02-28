import './LatencyBadge.css'

interface LatencyBadgeProps {
  latency: number
}

export default function LatencyBadge({ latency }: LatencyBadgeProps) {
  const getLatencyStatus = () => {
    if (latency === 0) return 'idle'
    if (latency < 500) return 'excellent'
    if (latency < 1000) return 'warning'
    return 'error'
  }

  const status = getLatencyStatus()

  return (
    <div className={`latency-badge ${status}`}>
      <div className="latency-indicator">
        <div className="ping-wave"></div>
        <div className="ping-wave"></div>
      </div>
      <div className="latency-content">
        <span className="latency-label">Query Latency</span>
        <span className="latency-value">
          {latency === 0 ? 'Ready' : `${latency}ms`}
        </span>
        {latency > 0 && latency < 500 && (
          <span className="latency-status">⚡ Sub-500ms</span>
        )}
      </div>
    </div>
  )
}
