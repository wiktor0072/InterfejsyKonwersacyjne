import { useState, useCallback, useRef, useEffect } from 'react'

export interface AudioAnalyserData {
  frequency: Uint8Array
  volume: number // 0-1 normalized
  intensity: number // 0-1, smoothed for visualization
}

export interface UseAudioAnalyserReturn {
  analyserData: AudioAnalyserData
  connectStream: (stream: MediaStream) => void
  connectAudioElement: (audio: HTMLAudioElement) => void
  disconnect: () => void
  isConnected: boolean
}

// ===== Constants =====

const FFT_SIZE = 256
const SMOOTHING_TIME_CONSTANT = 0.8
const VOLUME_SMOOTHING = 0.3 // Lower = smoother

// ===== Main Hook =====

export function useAudioAnalyser(): UseAudioAnalyserReturn {
  const [isConnected, setIsConnected] = useState(false)
  const [analyserData, setAnalyserData] = useState<AudioAnalyserData>({
    frequency: new Uint8Array(FFT_SIZE / 2),
    volume: 0,
    intensity: 0,
  })

  const audioContextRef = useRef<AudioContext | null>(null)
  const analyserRef = useRef<AnalyserNode | null>(null)
  const sourceRef = useRef<MediaStreamAudioSourceNode | MediaElementAudioSourceNode | null>(null)
  const animationFrameRef = useRef<number | null>(null)
  const previousIntensityRef = useRef(0)

  // Cleanup function
  const cleanup = useCallback(() => {
    if (animationFrameRef.current) {
      cancelAnimationFrame(animationFrameRef.current)
      animationFrameRef.current = null
    }

    if (sourceRef.current) {
      sourceRef.current.disconnect()
      sourceRef.current = null
    }

    // Don't close AudioContext - it can be reused
    analyserRef.current = null
    setIsConnected(false)
    
    // Reset to idle state
    setAnalyserData({
      frequency: new Uint8Array(FFT_SIZE / 2),
      volume: 0,
      intensity: 0,
    })
    previousIntensityRef.current = 0
  }, [])

  // Initialize or get AudioContext and AnalyserNode
  const getOrCreateAnalyser = useCallback(() => {
    if (!audioContextRef.current) {
      audioContextRef.current = new AudioContext()
      console.log('[AudioAnalyser] AudioContext utworzony')
    }

    if (audioContextRef.current.state === 'suspended') {
      audioContextRef.current.resume()
    }

    if (!analyserRef.current) {
      analyserRef.current = audioContextRef.current.createAnalyser()
      analyserRef.current.fftSize = FFT_SIZE
      analyserRef.current.smoothingTimeConstant = SMOOTHING_TIME_CONSTANT
      console.log('[AudioAnalyser] AnalyserNode utworzony')
    }

    return { audioContext: audioContextRef.current, analyser: analyserRef.current }
  }, [])

  // Animation loop to read frequency data
  const startAnalysis = useCallback(() => {
    const analyser = analyserRef.current
    if (!analyser) return

    const dataArray = new Uint8Array(analyser.frequencyBinCount)

    const analyze = () => {
      analyser.getByteFrequencyData(dataArray)

      // Calculate volume (average of all frequencies)
      let sum = 0
      for (let i = 0; i < dataArray.length; i++) {
        sum += dataArray[i]
      }
      const avgVolume = sum / dataArray.length / 255 // Normalize to 0-1

      // Smooth intensity for visualization
      const targetIntensity = Math.min(avgVolume * 2, 1) // Amplify a bit
      const smoothedIntensity = previousIntensityRef.current + 
        (targetIntensity - previousIntensityRef.current) * VOLUME_SMOOTHING
      previousIntensityRef.current = smoothedIntensity

      setAnalyserData({
        frequency: new Uint8Array(dataArray),
        volume: avgVolume,
        intensity: smoothedIntensity,
      })

      animationFrameRef.current = requestAnimationFrame(analyze)
    }

    analyze()
  }, [])

  // Connect to MediaStream (microphone)
  const connectStream = useCallback((stream: MediaStream) => {
    cleanup()
    
    const { audioContext, analyser } = getOrCreateAnalyser()

    try {
      const source = audioContext.createMediaStreamSource(stream)
      source.connect(analyser)
      sourceRef.current = source
      
      console.log('[AudioAnalyser] Podłączono do strumienia mikrofonu')
      setIsConnected(true)
      startAnalysis()
    } catch (error) {
      console.error('[AudioAnalyser] Błąd podłączania strumienia:', error)
    }
  }, [cleanup, getOrCreateAnalyser, startAnalysis])

  // Connect to HTMLAudioElement (TTS playback)
  const connectAudioElement = useCallback((audio: HTMLAudioElement) => {
    cleanup()
    
    const { audioContext, analyser } = getOrCreateAnalyser()

    try {
      const source = audioContext.createMediaElementSource(audio)
      source.connect(analyser)
      // Also connect to destination so audio is still audible
      analyser.connect(audioContext.destination)
      sourceRef.current = source
      
      console.log('[AudioAnalyser] Podłączono do elementu audio')
      setIsConnected(true)
      startAnalysis()
    } catch (error) {
      console.error('[AudioAnalyser] Błąd podłączania elementu audio:', error)
    }
  }, [cleanup, getOrCreateAnalyser, startAnalysis])

  // Manual disconnect
  const disconnect = useCallback(() => {
    console.log('[AudioAnalyser] Rozłączanie')
    cleanup()
  }, [cleanup])

  // Cleanup on unmount
  useEffect(() => {
    return () => {
      cleanup()
      if (audioContextRef.current) {
        audioContextRef.current.close()
        audioContextRef.current = null
      }
    }
  }, [cleanup])

  return {
    analyserData,
    connectStream,
    connectAudioElement,
    disconnect,
    isConnected,
  }
}
