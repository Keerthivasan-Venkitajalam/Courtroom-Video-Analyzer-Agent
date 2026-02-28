import { useEffect, useRef, useState } from 'react'
import Hls from 'hls.js'
import './VideoPlayer.css'
import { 
  StreamVideoClient, 
  Call, 
  useCallStateHooks,
  StreamCall,
  ParticipantView
} from '@stream-io/video-react-sdk'

interface VideoPlayerProps {
  liveStreamUrl: string
  clipUrl?: string
  client: StreamVideoClient
}

export default function VideoPlayer({ clipUrl, client }: VideoPlayerProps) {
  const clipVideoRef = useRef<HTMLVideoElement>(null)
  const [activePlayer, setActivePlayer] = useState<'live' | 'clip'>('live')
  const [call, setCall] = useState<Call | null>(null)
  const [callJoined, setCallJoined] = useState(false)

  // Initialize WebRTC call using Stream Video SDK
  useEffect(() => {
    const callId = import.meta.env.VITE_SESSION_ID || 'wemakedevs-demo-room'
    const newCall = client.call('default', callId)
    
    const joinCall = async () => {
      try {
        await newCall.join({ create: true })
        setCall(newCall)
        setCallJoined(true)
        console.log('Successfully joined WebRTC courtroom room:', callId)
      } catch (error) {
        console.error('Failed to join call:', error)
      }
    }

    joinCall()

    return () => {
      if (newCall) {
        newCall.leave().catch(console.error)
      }
    }
  }, [client])

  // Handle clip playback with exact timestamp and no buffering
  useEffect(() => {
    if (!clipUrl || !clipVideoRef.current) return

    const video = clipVideoRef.current

    // Configure video element for optimal playback
    video.preload = 'auto'
    video.playsInline = true

    if (Hls.isSupported()) {
      const hls = new Hls({
        // Optimize for low latency and no buffering
        maxBufferLength: 10,
        maxMaxBufferLength: 30,
        maxBufferSize: 60 * 1000 * 1000,
        maxBufferHole: 0.5,
        lowLatencyMode: true,
        backBufferLength: 0,
        // Enable fast start
        startLevel: -1,
        autoStartLoad: true,
        // Reduce initial buffering
        liveSyncDurationCount: 3,
        liveMaxLatencyDurationCount: 10
      })
      
      hls.loadSource(clipUrl)
      hls.attachMedia(video)
      
      hls.on(Hls.Events.MANIFEST_PARSED, () => {
        // Start playback immediately at exact timestamp
        video.currentTime = 0
        const playPromise = video.play()
        
        if (playPromise !== undefined) {
          playPromise
            .then(() => {
              setActivePlayer('clip')
              console.log('Clip playback started at exact timestamp')
            })
            .catch(error => {
              console.error('Playback failed:', error)
            })
        }
      })

      hls.on(Hls.Events.ERROR, (_event, data) => {
        if (data.fatal) {
          console.error('Fatal HLS error:', data)
          switch (data.type) {
            case Hls.ErrorTypes.NETWORK_ERROR:
              console.log('Network error, attempting recovery...')
              hls.startLoad()
              break
            case Hls.ErrorTypes.MEDIA_ERROR:
              console.log('Media error, attempting recovery...')
              hls.recoverMediaError()
              break
            default:
              console.log('Unrecoverable error, destroying HLS instance')
              hls.destroy()
              break
          }
        }
      })

      return () => {
        hls.destroy()
      }
    } else if (video.canPlayType('application/vnd.apple.mpegurl')) {
      video.src = clipUrl
      video.addEventListener('loadedmetadata', () => {
        video.currentTime = 0
        video.play()
          .then(() => {
            setActivePlayer('clip')
            console.log('Clip playback started at exact timestamp')
          })
          .catch(error => {
            console.error('Playback failed:', error)
          })
      })
    }
  }, [clipUrl])

  return (
    <div className="video-player-container">
      <div className="video-wrapper">
        <div className={`video-canvas ${activePlayer === 'live' ? 'active' : ''}`}>
          {call && callJoined ? (
            <StreamCall call={call}>
              <LiveStreamView />
            </StreamCall>
          ) : (
            <div className="video-loading">Connecting to courtroom...</div>
          )}
          <div className="video-label">Live Stream</div>
        </div>

        <div className={`video-canvas ${activePlayer === 'clip' ? 'active' : ''}`}>
          <video
            ref={clipVideoRef}
            className="video-element"
            controls
            playsInline
          />
          <div className="video-label">Evidence Clip</div>
        </div>
      </div>

      <div className="video-controls">
        <button 
          className={`control-btn ${activePlayer === 'live' ? 'active' : ''}`}
          onClick={() => setActivePlayer('live')}
        >
          Live View
        </button>
        <button 
          className={`control-btn ${activePlayer === 'clip' ? 'active' : ''}`}
          onClick={() => setActivePlayer('clip')}
          disabled={!clipUrl}
        >
          Evidence Clip
        </button>
      </div>
    </div>
  )
}

// Component to render live stream participants
function LiveStreamView() {
  const { useParticipants } = useCallStateHooks()
  const participants = useParticipants()

  if (participants.length === 0) {
    return <div className="video-loading">Waiting for courtroom feed...</div>
  }

  return (
    <div className="participants-grid">
      {participants.map((participant) => (
        <ParticipantView
          key={participant.sessionId}
          participant={participant}
          className="participant-tile"
        />
      ))}
    </div>
  )
}
