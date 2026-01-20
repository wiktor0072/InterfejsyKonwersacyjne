import { useState, useEffect, useCallback, useRef } from 'react'
import { MeshGradientBackground } from './components/MeshGradientBackground'
import { ParticlesBackground } from './components/ParticlesBackground'
import { ChatHistory } from './components/ChatHistory'
import { VoiceControls } from './components/VoiceControls'
import { ChatInput } from './components/ChatInput'
import { ToastContainer, useToast } from './components/Toast'
import { ThinkingIndicator, SpeakingIndicator, ListeningIndicator } from './components/TypingIndicator'
import { useWebSocket } from './hooks/useWebSocket'
import { useAudioRecorder } from './hooks/useAudioRecorder'
import { useAudioPlayback } from './hooks/useAudioPlayback'
import { useAudioAnalyser } from './hooks/useAudioAnalyser'
import type { Message } from './components/MessageBubble'
import type { IncomingMessage } from './hooks/useWebSocket'

const VOLUME_SMOOTHING = 0.3

function App() {
  const [messages, setMessages] = useState<Message[]>([])
  const [isProcessing, setIsProcessing] = useState(false)
  const [activeAudioSource, setActiveAudioSource] = useState<'user' | 'assistant' | null>(null)
  const [assistantIntensity, setAssistantIntensity] = useState(0)

  const assistantAnimationRef = useRef<number | null>(null)
  const assistantPrevIntensityRef = useRef(0)

  // Hooks
  const { toasts, addToast, removeToast } = useToast()
  const { sendAudio, sendMessage, lastMessage, connectionStatus } = useWebSocket()
  const { startRecording, stopRecording, recordingStatus, errorMessage: recorderError, audioStream } = useAudioRecorder()
  const { playAudio, playbackStatus, analyserNode } = useAudioPlayback()
  const userAnalyser = useAudioAnalyser()

  // Add message to chat
  const addMessage = useCallback((role: 'user' | 'assistant', content: string) => {
    const newMessage: Message = {
      id: crypto.randomUUID(),
      role,
      content,
      timestamp: new Date(),
    }
    setMessages(prev => [...prev, newMessage])
  }, [])

  // Handle incoming WebSocket messages
  useEffect(() => {
    if (!lastMessage) return

    const message = lastMessage as IncomingMessage

    switch (message.type) {
      case 'transcription':
        // User's speech was transcribed
        addMessage('user', message.text)
        setIsProcessing(true)
        break

      case 'response':
        // LLM response received
        addMessage('assistant', message.text)
        setIsProcessing(false)
        break

      case 'audio':
        // TTS audio received - play it
        playAudio(message.data)
        break

      case 'error':
        // Error from backend
        addToast('error', message.message)
        setIsProcessing(false)
        break

      case 'history':
        // Load conversation history from server
        const loadedMessages: Message[] = message.messages.map((msg, idx) => ({
          id: `loaded-${idx}`,
          role: msg.role as 'user' | 'assistant',
          content: msg.content,
          timestamp: new Date(msg.timestamp),
        }))
        setMessages(loadedMessages)
        break
    }
  }, [lastMessage, addMessage, playAudio, addToast])

  // Handle recorder errors
  useEffect(() => {
    if (recorderError) {
      addToast('error', recorderError)
    }
  }, [recorderError, addToast])

  // Handle connection status changes
  useEffect(() => {
    if (connectionStatus === 'connected') {
      addToast('success', 'Połączono z serwerem')
    } else if (connectionStatus === 'error') {
      addToast('error', 'Nie można połączyć z serwerem. Sprawdź czy backend działa.')
    }
  }, [connectionStatus, addToast])

  // Connect user audio stream to analyser when recording
  useEffect(() => {
    if (audioStream && recordingStatus === 'recording') {
      userAnalyser.connectStream(audioStream)
      setActiveAudioSource('user')
    } else if (recordingStatus !== 'recording') {
      userAnalyser.disconnect()
      if (playbackStatus !== 'playing') {
        setActiveAudioSource(null)
      }
    }
  }, [audioStream, recordingStatus, playbackStatus, userAnalyser.connectStream, userAnalyser.disconnect])

  // Analyze TTS audio when playing using analyserNode from useAudioPlayback
  useEffect(() => {
    if (analyserNode && playbackStatus === 'playing') {
      setActiveAudioSource('assistant')
      
      const dataArray = new Uint8Array(analyserNode.frequencyBinCount)
      
      const analyze = () => {
        analyserNode.getByteFrequencyData(dataArray)
        
        let sum = 0
        for (let i = 0; i < dataArray.length; i++) {
          sum += dataArray[i]
        }
        const avgVolume = sum / dataArray.length / 255
        
        const targetIntensity = Math.min(avgVolume * 2, 1)
        const smoothedIntensity = assistantPrevIntensityRef.current + 
          (targetIntensity - assistantPrevIntensityRef.current) * VOLUME_SMOOTHING
        assistantPrevIntensityRef.current = smoothedIntensity
        
        setAssistantIntensity(smoothedIntensity)
        assistantAnimationRef.current = requestAnimationFrame(analyze)
      }
      
      analyze()
      
      return () => {
        if (assistantAnimationRef.current) {
          cancelAnimationFrame(assistantAnimationRef.current)
          assistantAnimationRef.current = null
        }
      }
    } else if (playbackStatus !== 'playing') {
      if (assistantAnimationRef.current) {
        cancelAnimationFrame(assistantAnimationRef.current)
        assistantAnimationRef.current = null
      }
      setAssistantIntensity(0)
      assistantPrevIntensityRef.current = 0
      if (recordingStatus !== 'recording') {
        setActiveAudioSource(null)
      }
    }
  }, [analyserNode, playbackStatus, recordingStatus])

  // Handle recording start/stop
  const handleStartRecording = useCallback(async () => {
    if (connectionStatus !== 'connected') {
      addToast('warning', 'Poczekaj na połączenie z serwerem')
      return
    }
    await startRecording()
  }, [connectionStatus, startRecording, addToast])

  const handleStopRecording = useCallback(async () => {
    const audioBlob = await stopRecording()
    if (audioBlob && audioBlob.size > 0) {
      console.log('[App] Wysyłanie audio:', audioBlob.size, 'bytes')
      sendAudio(audioBlob)
      setIsProcessing(true)
    }
  }, [stopRecording, sendAudio])

  const handleSendMessage = useCallback((text: string) => {
    if (connectionStatus !== 'connected') {
      addToast('warning', 'Poczekaj na połączenie z serwerem')
      return
    }
    
    // Add user message immediately
    addMessage('user', text)
    setIsProcessing(true)
    
    sendMessage({ type: 'text', content: text })
  }, [connectionStatus, sendMessage, addMessage, addToast])

  // Calculate audio intensity for particles
  const audioIntensity = activeAudioSource === 'user' 
    ? userAnalyser.analyserData.intensity 
    : activeAudioSource === 'assistant'
      ? assistantIntensity
      : 0

  const isRecording = recordingStatus === 'recording'
  const isPlaying = playbackStatus === 'playing'
  const isConnected = connectionStatus === 'connected'

  return (
    <div className="relative min-h-screen overflow-hidden">
      {/* Background layers */}
      <MeshGradientBackground />
      <ParticlesBackground 
        audioIntensity={audioIntensity} 
        activeSource={activeAudioSource}
      />
      
      {/* Toast notifications */}
      <ToastContainer toasts={toasts} onRemove={removeToast} />

      {/* Status indicators */}
      <SpeakingIndicator isVisible={isPlaying} />
      <ListeningIndicator isVisible={isRecording} />

      {/* Main content */}
      <div className="relative z-10 flex flex-col h-screen">
        {/* Header */}
        <header className="flex items-center justify-between px-6 py-4 border-b border-white/10">
          <h1 className="text-2xl font-bold text-white/90 tracking-tight">
            Hotel Aurora
          </h1>
          
          {/* Connection status indicator */}
          <div className="flex items-center gap-2">
            <span className={`w-2 h-2 rounded-full ${
              isConnected ? 'bg-green-400' : 
              connectionStatus === 'connecting' ? 'bg-yellow-400 animate-pulse' : 
              'bg-red-400'
            }`} />
            <span className="text-xs text-white/40">
              {isConnected ? 'Połączono' : 
               connectionStatus === 'connecting' ? 'Łączenie...' : 
               'Rozłączono'}
            </span>
          </div>
        </header>

        {/* Chat area */}
        <div className="flex-1 flex flex-col max-w-3xl mx-auto w-full overflow-hidden">
          <ChatHistory messages={messages} />
          
          {/* Thinking indicator */}
          {isProcessing && !isPlaying && (
            <div className="px-4 pb-2">
              <ThinkingIndicator />
            </div>
          )}
          
          {/* Voice controls and Chat Input */}
          <div className="p-6 flex flex-col gap-4">
            <VoiceControls
              onStartRecording={handleStartRecording}
              onStopRecording={handleStopRecording}
              isRecording={isRecording}
              isProcessing={isProcessing}
              isConnected={isConnected}
              errorMessage={recorderError}
            />
            
            <ChatInput 
              onSendMessage={handleSendMessage}
              disabled={!isConnected || isProcessing}
            />
          </div>
        </div>
      </div>
    </div>
  )
}

export default App
