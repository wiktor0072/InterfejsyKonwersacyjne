import { useState, useCallback, useEffect } from 'react'

export interface VoiceControlsProps {
  onStartRecording: () => void
  onStopRecording: () => void
  isRecording: boolean
  isProcessing: boolean
  isConnected: boolean
  errorMessage?: string | null
}

export function VoiceControls({
  onStartRecording,
  onStopRecording,
  isRecording,
  isProcessing,
  isConnected,
  errorMessage,
}: VoiceControlsProps) {
  const [continuousListening, setContinuousListening] = useState(false)
  const [isPressing, setIsPressing] = useState(false)

  // Handle push-to-talk (mouse)
  const handleMouseDown = useCallback(() => {
    if (continuousListening || isProcessing || !isConnected) return
    setIsPressing(true)
    onStartRecording()
  }, [continuousListening, isProcessing, isConnected, onStartRecording])

  const handleMouseUp = useCallback(() => {
    if (!isPressing) return
    setIsPressing(false)
    onStopRecording()
  }, [isPressing, onStopRecording])

  // Handle keyboard (Space key)
  useEffect(() => {
    const isInputFocused = () => {
      const tag = document.activeElement?.tagName.toLowerCase()
      return tag === 'input' || tag === 'textarea' || document.activeElement?.getAttribute('contenteditable') === 'true'
    }

    const handleKeyDown = (e: KeyboardEvent) => {
      if (e.code === 'Space' && !e.repeat && !continuousListening && isConnected && !isProcessing && !isInputFocused()) {
        e.preventDefault()
        setIsPressing(true)
        onStartRecording()
      }
    }

    const handleKeyUp = (e: KeyboardEvent) => {
      if (e.code === 'Space' && isPressing) {
        e.preventDefault()
        setIsPressing(false)
        onStopRecording()
      }
    }

    window.addEventListener('keydown', handleKeyDown)
    window.addEventListener('keyup', handleKeyUp)

    return () => {
      window.removeEventListener('keydown', handleKeyDown)
      window.removeEventListener('keyup', handleKeyUp)
    }
  }, [continuousListening, isConnected, isProcessing, isPressing, onStartRecording, onStopRecording])

  // Toggle continuous listening
  const handleToggleContinuous = useCallback(() => {
    if (continuousListening) {
      // Turning off
      setContinuousListening(false)
      if (isRecording) {
        onStopRecording()
      }
    } else {
      // Turning on
      setContinuousListening(true)
      onStartRecording()
    }
  }, [continuousListening, isRecording, onStartRecording, onStopRecording])

  // Determine button state and appearance
  const isActive = isRecording || isPressing
  const isDisabled = !isConnected || isProcessing

  return (
    <div className="flex flex-col items-center gap-4">
      {/* Error message */}
      {errorMessage && (
        <div className="text-red-400 text-sm bg-red-500/10 px-4 py-2 rounded-lg border border-red-500/20">
          {errorMessage}
        </div>
      )}

      {/* Connection status */}
      {!isConnected && (
        <div className="text-yellow-400 text-sm flex items-center gap-2">
          <span className="w-2 h-2 rounded-full bg-yellow-400 animate-pulse" />
          Łączenie z serwerem...
        </div>
      )}

      {/* Main controls row */}
      <div className="flex items-center gap-4">
        {/* Push-to-talk button */}
        <button
          onMouseDown={handleMouseDown}
          onMouseUp={handleMouseUp}
          onMouseLeave={handleMouseUp}
          onTouchStart={handleMouseDown}
          onTouchEnd={handleMouseUp}
          disabled={isDisabled || continuousListening}
          className={`
            w-16 h-16 rounded-full flex items-center justify-center
            transition-all duration-200 ease-out
            ${isDisabled || continuousListening
              ? 'bg-gray-600 cursor-not-allowed opacity-50'
              : isActive
                ? 'bg-gradient-to-br from-red-500 to-pink-600 scale-110 shadow-lg shadow-red-500/40'
                : 'bg-gradient-to-br from-cyan-500 to-purple-600 shadow-lg shadow-purple-500/25 hover:shadow-purple-500/40 hover:scale-105'
            }
            ${isActive ? 'animate-pulse' : ''}
          `}
          title="Przytrzymaj, aby nagrywać (lub użyj Spacji)"
        >
          {/* Microphone icon */}
          <svg 
            className={`w-7 h-7 text-white transition-transform ${isActive ? 'scale-110' : ''}`} 
            fill="none" 
            stroke="currentColor" 
            viewBox="0 0 24 24"
          >
            <path 
              strokeLinecap="round" 
              strokeLinejoin="round" 
              strokeWidth={2} 
              d="M19 11a7 7 0 01-7 7m0 0a7 7 0 01-7-7m7 7v4m0 0H8m4 0h4m-4-8a3 3 0 01-3-3V5a3 3 0 116 0v6a3 3 0 01-3 3z" 
            />
          </svg>
        </button>

        {/* Continuous listening toggle */}
        <button
          onClick={handleToggleContinuous}
          disabled={isDisabled}
          className={`
            px-4 py-2 rounded-lg text-sm font-medium
            transition-all duration-200
            ${isDisabled
              ? 'bg-gray-600 text-gray-400 cursor-not-allowed'
              : continuousListening
                ? 'bg-green-500/20 text-green-400 border border-green-500/40 hover:bg-green-500/30'
                : 'bg-white/10 text-white/70 border border-white/20 hover:bg-white/20 hover:text-white'
            }
          `}
          title="Włącz ciągłe słuchanie"
        >
          <div className="flex items-center gap-2">
            {/* Wave icon or indicator */}
            {continuousListening ? (
              <span className="flex gap-0.5">
                <span className="w-1 h-3 bg-green-400 rounded-full animate-pulse" style={{ animationDelay: '0ms' }} />
                <span className="w-1 h-4 bg-green-400 rounded-full animate-pulse" style={{ animationDelay: '150ms' }} />
                <span className="w-1 h-3 bg-green-400 rounded-full animate-pulse" style={{ animationDelay: '300ms' }} />
              </span>
            ) : (
              <svg className="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M15.536 8.464a5 5 0 010 7.072m2.828-9.9a9 9 0 010 12.728M5.586 15.536a5 5 0 001.414 1.414m2.828-9.9a9 9 0 0112.728 0" />
              </svg>
            )}
            <span>{continuousListening ? 'Słucham...' : 'Ciągłe słuchanie'}</span>
          </div>
        </button>
      </div>

      {/* Status text */}
      <div className="text-white/40 text-xs text-center">
        {isProcessing ? (
          <span className="text-purple-400">Przetwarzanie...</span>
        ) : isActive ? (
          <span className="text-cyan-400">Nagrywanie... (puść, aby wysłać)</span>
        ) : continuousListening ? (
          <span className="text-green-400">Mów teraz...</span>
        ) : (
          <span>Przytrzymaj przycisk lub Spację, aby mówić</span>
        )}
      </div>
    </div>
  )
}
