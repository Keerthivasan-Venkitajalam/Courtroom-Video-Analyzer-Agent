import { useState } from 'react'
import './App.css'
import VideoPlayer from './components/VideoPlayer.tsx'
import ChatPanel from './components/ChatPanel.tsx'
import TranscriptPanel from './components/TranscriptPanel.tsx'
import LatencyBadge from './components/LatencyBadge.tsx'
import { StreamVideo, StreamVideoClient } from '@stream-io/video-react-sdk'
import '@stream-io/video-react-sdk/dist/css/styles.css'
import Logo from './assets/Logo.svg'

interface QueryResult {
  query_id: string
  transcript_results: any[]
  video_results: any[]
  video_clips: any[]
  total_latency_ms: number
}

// Initialize Stream Video Client
const apiKey = import.meta.env.VITE_STREAM_API_KEY || 'x563t6g4ysy7'
const userId = 'attorney-user'
const userName = 'Attorney User'

const user = {
  id: userId,
  name: userName,
}

const tokenProvider = async () => {
  const response = await fetch('http://localhost:8000/api/stream/token', {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({ user_id: userId })
  })
  const data = await response.json()
  return data.token
}

const client = new StreamVideoClient({
  apiKey,
  user,
  tokenProvider
})

function App() {
  const [queryResult, setQueryResult] = useState<QueryResult | null>(null)
  const [isLoading, setIsLoading] = useState(false)
  const [currentClipUrl, setCurrentClipUrl] = useState<string>('')

  const handleQuerySubmit = async (query: string) => {
    setIsLoading(true)
    const startTime = Date.now()

    try {
      // Call backend API
      const response = await fetch('http://localhost:8000/api/query', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          query,
          session_id: 'courtroom-session-1',
          user_id: userId
        })
      })

      if (!response.ok) {
        throw new Error(`API error: ${response.status}`)
      }

      const result: QueryResult = await response.json()

      // Log latency
      console.log(`Query latency: ${result.total_latency_ms}ms`)
      if (result.total_latency_ms > 500) {
        console.warn('⚠️ Query latency exceeded 500ms threshold')
      }

      setQueryResult(result)
    } catch (error) {
      console.error('Query failed:', error)

      // Fallback response on error
      const result: QueryResult = {
        query_id: `query_${Date.now()}`,
        transcript_results: [],
        video_results: [],
        video_clips: [],
        total_latency_ms: Date.now() - startTime
      }
      setQueryResult(result)
    } finally {
      setIsLoading(false)
    }
  }

  const handleClipSelect = (clipUrl: string) => {
    setCurrentClipUrl(clipUrl)
  }

  return (
    <StreamVideo client={client}>
      <div className="app-container">
        <header className="app-header">
          <div className="header-left">
            <img src={Logo} alt="Courtroom Video Analyzer Logo" className="app-logo" />
            <h1>Courtroom Video Analyzer</h1>
          </div>
          <LatencyBadge latency={queryResult?.total_latency_ms || 0} />
        </header>

        <div className="main-content">
          <div className="video-section">
            <VideoPlayer
              liveStreamUrl="rtsp://localhost:8554/courtcam"
              clipUrl={currentClipUrl}
              client={client}
            />
          </div>

          <div className="side-panel">
            <TranscriptPanel />
            <ChatPanel
              onQuerySubmit={handleQuerySubmit}
              isLoading={isLoading}
              queryResult={queryResult}
              onClipSelect={handleClipSelect}
            />
          </div>
        </div>
      </div>
    </StreamVideo>
  )
}

export default App
