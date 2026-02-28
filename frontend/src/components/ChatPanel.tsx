import { useState, useRef, useEffect } from 'react'
import './ChatPanel.css'
import Logo from '../assets/Logo.svg'

interface TranscriptResult {
  segment: {
    text: string
    speaker: {
      role: string
    }
    start_timestamp_us: number
    end_timestamp_us: number
  }
  matched_terms: string[]
  relevance_score: number
}

interface VideoClip {
  clip_id: string
  hls_manifest_url: string
  start_timestamp_us: number
  end_timestamp_us: number
  duration_ms: number
}

interface Message {
  id: string
  type: 'user' | 'agent'
  text: string
  timestamp: number
  transcriptResults?: TranscriptResult[]
  videoClips?: VideoClip[]
  totalLatencyMs?: number
}

interface ChatPanelProps {
  onQuerySubmit: (query: string) => void
  isLoading: boolean
  queryResult: any
  onClipSelect: (clipUrl: string) => void
}

// Helper function to highlight matched terms in text
function highlightMatches(text: string, matchedTerms: string[]): React.ReactElement {
  if (!matchedTerms || matchedTerms.length === 0) {
    return <>{text}</>
  }

  // Create a regex pattern that matches any of the matched terms (case-insensitive)
  const pattern = matchedTerms
    .map(term => term.replace(/[.*+?^${}()|[\]\\]/g, '\\$&')) // Escape special chars
    .join('|')
  
  const regex = new RegExp(`(${pattern})`, 'gi')
  const parts = text.split(regex)

  return (
    <>
      {parts.map((part, index) => {
        const isMatch = matchedTerms.some(term => 
          part.toLowerCase() === term.toLowerCase()
        )
        return isMatch ? (
          <mark key={index} className="highlight">{part}</mark>
        ) : (
          <span key={index}>{part}</span>
        )
      })}
    </>
  )
}

// Helper function to format timestamp
function formatTimestamp(timestampUs: number): string {
  const seconds = Math.floor(timestampUs / 1000000)
  const minutes = Math.floor(seconds / 60)
  const hours = Math.floor(minutes / 60)
  
  const displayHours = hours % 24
  const displayMinutes = minutes % 60
  const displaySeconds = seconds % 60
  
  if (hours > 0) {
    return `${displayHours}:${displayMinutes.toString().padStart(2, '0')}:${displaySeconds.toString().padStart(2, '0')}`
  }
  return `${displayMinutes}:${displaySeconds.toString().padStart(2, '0')}`
}

export default function ChatPanel({ 
  onQuerySubmit, 
  isLoading, 
  queryResult,
  onClipSelect 
}: ChatPanelProps) {
  const [messages, setMessages] = useState<Message[]>([
    {
      id: '1',
      type: 'agent',
      text: 'Hello! I\'m monitoring the courtroom proceedings. Ask me anything about what\'s been said or shown.',
      timestamp: Date.now()
    }
  ])
  const [inputValue, setInputValue] = useState('')
  const [isVoiceMode, setIsVoiceMode] = useState(false)
  const messagesEndRef = useRef<HTMLDivElement>(null)

  const scrollToBottom = () => {
    if (messagesEndRef.current) {
      messagesEndRef.current.scrollIntoView({ 
        behavior: 'smooth',
        block: 'nearest',
        inline: 'nearest'
      })
    }
  }

  useEffect(() => {
    scrollToBottom()
  }, [messages])

  useEffect(() => {
    if (queryResult) {
      // Parse the structured JSON payload from agent
      const transcriptResults: TranscriptResult[] = queryResult.transcriptResults || []
      const videoClips: VideoClip[] = queryResult.videoClips || []
      const totalLatencyMs = queryResult.totalLatencyMs || 0

      // Generate response text based on results
      let responseText = ''
      if (transcriptResults.length > 0 || videoClips.length > 0) {
        responseText = `Found ${transcriptResults.length} transcript match${transcriptResults.length !== 1 ? 'es' : ''}`
        if (videoClips.length > 0) {
          responseText += ` and ${videoClips.length} video clip${videoClips.length !== 1 ? 's' : ''}`
        }
        responseText += '.'
        
        // Add latency info
        if (totalLatencyMs > 0) {
          responseText += ` (${totalLatencyMs}ms)`
        }
      } else {
        responseText = 'No results found for your query.'
      }

      const agentMessage: Message = {
        id: `msg_${Date.now()}`,
        type: 'agent',
        text: responseText,
        timestamp: Date.now(),
        transcriptResults,
        videoClips,
        totalLatencyMs
      }
      
      setMessages(prev => [...prev, agentMessage])

      // Auto-play the first clip if available
      if (videoClips.length > 0 && videoClips[0].hls_manifest_url) {
        onClipSelect(videoClips[0].hls_manifest_url)
      }
    }
  }, [queryResult, onClipSelect])

  const handleSubmit = (e: React.FormEvent) => {
    e.preventDefault()
    if (!inputValue.trim() || isLoading) return

    const userMessage: Message = {
      id: `msg_${Date.now()}`,
      type: 'user',
      text: inputValue,
      timestamp: Date.now()
    }

    setMessages(prev => [...prev, userMessage])
    onQuerySubmit(inputValue)
    setInputValue('')
  }

  const handleVoiceToggle = () => {
    setIsVoiceMode(!isVoiceMode)
    // TODO: Implement voice input using Stream's microphone toggle
  }

  return (
    <div className="chat-panel">
      <div className="chat-header">
        <div className="chat-header-left">
          <img src={Logo} alt="Logo" className="panel-logo" />
          <h3>Query Assistant</h3>
        </div>
        <button 
          className={`voice-btn ${isVoiceMode ? 'active' : ''}`}
          onClick={handleVoiceToggle}
          title="Toggle voice mode"
        >
          <span className="mic-icon">🎤</span>
        </button>
      </div>

      <div className="messages-container">
        {messages.map(message => (
          <div key={message.id} className={`message ${message.type}`}>
            <div className="message-content">
              <p>{message.text}</p>
              
              {/* Display transcript results with highlighting */}
              {message.transcriptResults && message.transcriptResults.length > 0 && (
                <div className="transcript-results">
                  <h4>Transcript Matches:</h4>
                  {message.transcriptResults.map((result, idx) => (
                    <div key={idx} className="transcript-result">
                      <div className="result-header">
                        <span className="speaker-label">{result.segment.speaker.role}</span>
                        <span className="timestamp">
                          {formatTimestamp(result.segment.start_timestamp_us)}
                        </span>
                        <span className="relevance-score">
                          {(result.relevance_score * 100).toFixed(0)}% match
                        </span>
                      </div>
                      <div className="result-text">
                        {highlightMatches(result.segment.text, result.matched_terms)}
                      </div>
                    </div>
                  ))}
                </div>
              )}

              {/* Display video clip buttons */}
              {message.videoClips && message.videoClips.length > 0 && (
                <div className="clip-buttons">
                  <h4>Video Clips:</h4>
                  {message.videoClips.map((clip, idx) => (
                    <button
                      key={clip.clip_id}
                      className="clip-btn"
                      onClick={() => onClipSelect(clip.hls_manifest_url)}
                    >
                      <span className="clip-icon">▶</span>
                      Clip {idx + 1} ({formatTimestamp(clip.start_timestamp_us)})
                      <span className="clip-duration">
                        {(clip.duration_ms / 1000).toFixed(1)}s
                      </span>
                    </button>
                  ))}
                </div>
              )}
            </div>
            <span className="message-time">
              {new Date(message.timestamp).toLocaleTimeString()}
            </span>
          </div>
        ))}
        {isLoading && (
          <div className="message agent loading">
            <div className="message-content">
              <p>Searching...</p>
              <div className="loading-dots">
                <span></span>
                <span></span>
                <span></span>
              </div>
            </div>
          </div>
        )}
        <div ref={messagesEndRef} />
      </div>

      <form className="chat-input-form" onSubmit={handleSubmit}>
        <input
          type="text"
          className="chat-input"
          placeholder="Ask about the proceedings..."
          value={inputValue}
          onChange={(e) => setInputValue(e.target.value)}
          disabled={isLoading}
        />
        <button 
          type="submit" 
          className="send-btn"
          disabled={isLoading || !inputValue.trim()}
        >
          Send
        </button>
      </form>
    </div>
  )
}
