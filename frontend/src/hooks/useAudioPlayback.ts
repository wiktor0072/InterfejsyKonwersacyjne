import { useState, useCallback, useRef, useEffect } from 'react'

export type PlaybackStatus = 'idle' | 'loading' | 'playing' | 'error'

export interface UseAudioPlaybackReturn {
  playAudio: (base64Audio: string) => void
  stopAudio: () => void
  playbackStatus: PlaybackStatus
  errorMessage: string | null
  audioElement: HTMLAudioElement | null
}

// ===== Main Hook =====

export function useAudioPlayback(): UseAudioPlaybackReturn {
  const [playbackStatus, setPlaybackStatus] = useState<PlaybackStatus>('idle')
  const [errorMessage, setErrorMessage] = useState<string | null>(null)
  const [audioElement, setAudioElement] = useState<HTMLAudioElement | null>(null)

  const audioRef = useRef<HTMLAudioElement | null>(null)
  const audioQueueRef = useRef<string[]>([])
  const isPlayingRef = useRef(false)

  // Process audio queue
  const processQueue = useCallback(() => {
    if (isPlayingRef.current || audioQueueRef.current.length === 0) {
      return
    }

    const base64Audio = audioQueueRef.current.shift()
    if (!base64Audio) return

    isPlayingRef.current = true
    setPlaybackStatus('loading')
    setErrorMessage(null)

    try {
      // Convert base64 to blob
      const binaryString = atob(base64Audio)
      const bytes = new Uint8Array(binaryString.length)
      for (let i = 0; i < binaryString.length; i++) {
        bytes[i] = binaryString.charCodeAt(i)
      }
      const audioBlob = new Blob([bytes], { type: 'audio/mp3' })
      const audioUrl = URL.createObjectURL(audioBlob)

      console.log('[AudioPlayback] Przygotowanie audio:', audioBlob.size, 'bytes')

      // Create and configure audio element
      const audio = new Audio(audioUrl)
      audioRef.current = audio
      setAudioElement(audio)

      audio.oncanplaythrough = () => {
        console.log('[AudioPlayback] Audio gotowe do odtwarzania')
        setPlaybackStatus('playing')
        audio.play().catch(error => {
          console.error('[AudioPlayback] Błąd odtwarzania:', error)
          setPlaybackStatus('error')
          setErrorMessage('Błąd odtwarzania audio')
          isPlayingRef.current = false
          processQueue()
        })
      }

      audio.onended = () => {
        console.log('[AudioPlayback] Audio zakończone')
        URL.revokeObjectURL(audioUrl)
        setPlaybackStatus('idle')
        setAudioElement(null)
        audioRef.current = null
        isPlayingRef.current = false
        processQueue() // Play next in queue
      }

      audio.onerror = (event) => {
        console.error('[AudioPlayback] Błąd audio:', event)
        URL.revokeObjectURL(audioUrl)
        setPlaybackStatus('error')
        setErrorMessage('Błąd ładowania audio')
        setAudioElement(null)
        audioRef.current = null
        isPlayingRef.current = false
        processQueue()
      }

    } catch (error) {
      console.error('[AudioPlayback] Błąd dekodowania base64:', error)
      setPlaybackStatus('error')
      setErrorMessage('Błąd dekodowania audio')
      isPlayingRef.current = false
      processQueue()
    }
  }, [])

  // Add audio to queue and start processing
  const playAudio = useCallback((base64Audio: string) => {
    console.log('[AudioPlayback] Dodawanie do kolejki, długość:', base64Audio.length)
    audioQueueRef.current.push(base64Audio)
    processQueue()
  }, [processQueue])

  // Stop current audio and clear queue
  const stopAudio = useCallback(() => {
    console.log('[AudioPlayback] Zatrzymywanie audio')
    
    // Clear queue
    audioQueueRef.current = []
    
    // Stop current audio
    if (audioRef.current) {
      audioRef.current.pause()
      audioRef.current.currentTime = 0
      audioRef.current = null
    }
    
    setPlaybackStatus('idle')
    setAudioElement(null)
    isPlayingRef.current = false
  }, [])

  // Cleanup on unmount
  useEffect(() => {
    return () => {
      if (audioRef.current) {
        audioRef.current.pause()
        audioRef.current = null
      }
      audioQueueRef.current = []
    }
  }, [])

  return {
    playAudio,
    stopAudio,
    playbackStatus,
    errorMessage,
    audioElement,
  }
}
