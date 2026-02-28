import { useState, useEffect, useRef } from 'react'
import './TranscriptPanel.css'
import Logo from '../assets/Logo.svg'

interface TranscriptSegment {
  id: string
  speaker: string
  text: string
  timestamp: number
  highlighted?: boolean
}

export default function TranscriptPanel() {
  const [segments] = useState<TranscriptSegment[]>([
    {
      id: '1',
      speaker: 'Judge',
      text: 'The court is now in session. Please be seated.',
      timestamp: Date.now() - 120000
    },
    {
      id: '2',
      speaker: 'Prosecution',
      text: 'Your Honor, we would like to present evidence regarding the timeline of events.',
      timestamp: Date.now() - 90000
    },
    {
      id: '3',
      speaker: 'Witness',
      text: 'I saw the blue vehicle arrive at approximately 4:15 PM.',
      timestamp: Date.now() - 60000
    }
  ])
  const scrollRef = useRef<HTMLDivElement>(null)

  useEffect(() => {
    // Auto-scroll to bottom when new segments arrive with smooth behavior
    if (scrollRef.current) {
      scrollRef.current.scrollTo({
        top: scrollRef.current.scrollHeight,
        behavior: 'smooth'
      })
    }
  }, [segments])

  const getSpeakerColor = (speaker: string) => {
    const colors: Record<string, string> = {
      'Judge': '#d4af37',
      'Prosecution': '#4caf50',
      'Defense': '#2196f3',
      'Witness': '#ff9800'
    }
    return colors[speaker] || '#9e9e9e'
  }

  return (
    <div className="transcript-panel">
      <div className="transcript-header">
        <div className="transcript-header-left">
          <img src={Logo} alt="Logo" className="panel-logo" />
          <h3>Live Transcript</h3>
        </div>
        <div className="recording-indicator">
          <span className="recording-dot"></span>
          <span>Recording</span>
        </div>
      </div>

      <div className="transcript-content" ref={scrollRef}>
        {segments.map(segment => (
          <div 
            key={segment.id} 
            className={`transcript-segment ${segment.highlighted ? 'highlighted' : ''}`}
          >
            <div className="segment-header">
              <span 
                className="speaker-label"
                style={{ color: getSpeakerColor(segment.speaker) }}
              >
                {segment.speaker}
              </span>
              <span className="segment-time">
                {new Date(segment.timestamp).toLocaleTimeString()}
              </span>
            </div>
            <p className="segment-text">{segment.text}</p>
          </div>
        ))}
      </div>
    </div>
  )
}
