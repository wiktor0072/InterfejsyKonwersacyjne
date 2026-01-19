import { useState, useCallback, useRef } from 'react'

export type RecordingStatus = 'idle' | 'requesting' | 'recording' | 'error'

export interface UseAudioRecorderReturn {
  startRecording: () => Promise<void>
  stopRecording: () => Promise<Blob | null>
  recordingStatus: RecordingStatus
  errorMessage: string | null
  audioStream: MediaStream | null
}

// ===== Constants =====

const AUDIO_CONSTRAINTS: MediaTrackConstraints = {
  echoCancellation: true,
  noiseSuppression: true,
  sampleRate: 16000,
}

const MIME_TYPE = 'audio/webm;codecs=opus'

// ===== Main Hook =====

export function useAudioRecorder(): UseAudioRecorderReturn {
  const [recordingStatus, setRecordingStatus] = useState<RecordingStatus>('idle')
  const [errorMessage, setErrorMessage] = useState<string | null>(null)
  const [audioStream, setAudioStream] = useState<MediaStream | null>(null)

  const mediaRecorderRef = useRef<MediaRecorder | null>(null)
  const audioChunksRef = useRef<Blob[]>([])

  const startRecording = useCallback(async (): Promise<void> => {
    // Reset state
    setErrorMessage(null)
    audioChunksRef.current = []
    
    setRecordingStatus('requesting')
    console.log('[AudioRecorder] Proszenie o dostęp do mikrofonu...')

    try {
      // Request microphone access
      const stream = await navigator.mediaDevices.getUserMedia({
        audio: AUDIO_CONSTRAINTS,
        video: false,
      })

      console.log('[AudioRecorder] Dostęp do mikrofonu uzyskany')
      setAudioStream(stream)

      // Check for supported MIME type
      const mimeType = MediaRecorder.isTypeSupported(MIME_TYPE) 
        ? MIME_TYPE 
        : 'audio/webm'
      
      console.log('[AudioRecorder] Używany format:', mimeType)

      // Create MediaRecorder
      const mediaRecorder = new MediaRecorder(stream, { mimeType })
      mediaRecorderRef.current = mediaRecorder

      // Handle data available
      mediaRecorder.ondataavailable = (event) => {
        if (event.data.size > 0) {
          audioChunksRef.current.push(event.data)
          console.log('[AudioRecorder] Chunk nagrany:', event.data.size, 'bytes')
        }
      }

      // Handle errors
      mediaRecorder.onerror = (event) => {
        console.error('[AudioRecorder] Błąd MediaRecorder:', event)
        setRecordingStatus('error')
        setErrorMessage('Błąd podczas nagrywania')
      }

      // Start recording
      mediaRecorder.start(100) // Collect data every 100ms
      setRecordingStatus('recording')
      console.log('[AudioRecorder] Nagrywanie rozpoczęte')

    } catch (error) {
      console.error('[AudioRecorder] Błąd dostępu do mikrofonu:', error)
      setRecordingStatus('error')

      if (error instanceof DOMException) {
        switch (error.name) {
          case 'NotAllowedError':
            setErrorMessage('Brak uprawnień do mikrofonu. Proszę zezwolić na dostęp.')
            break
          case 'NotFoundError':
            setErrorMessage('Nie znaleziono mikrofonu.')
            break
          case 'NotReadableError':
            setErrorMessage('Mikrofon jest używany przez inną aplikację.')
            break
          default:
            setErrorMessage(`Błąd mikrofonu: ${error.message}`)
        }
      } else {
        setErrorMessage('Nieznany błąd podczas nagrywania')
      }
    }
  }, [])

  const stopRecording = useCallback(async (): Promise<Blob | null> => {
    return new Promise((resolve) => {
      const mediaRecorder = mediaRecorderRef.current

      if (!mediaRecorder || mediaRecorder.state === 'inactive') {
        console.warn('[AudioRecorder] Brak aktywnego nagrywania do zatrzymania')
        resolve(null)
        return
      }

      console.log('[AudioRecorder] Zatrzymywanie nagrywania...')

      mediaRecorder.onstop = () => {
        console.log('[AudioRecorder] Nagrywanie zatrzymane, chunks:', audioChunksRef.current.length)

        // Create blob from chunks
        const audioBlob = new Blob(audioChunksRef.current, { type: mediaRecorder.mimeType })
        console.log('[AudioRecorder] Audio blob utworzony:', audioBlob.size, 'bytes')

        // Stop all tracks to release microphone
        if (audioStream) {
          audioStream.getTracks().forEach(track => {
            track.stop()
            console.log('[AudioRecorder] Track zatrzymany:', track.kind)
          })
        }

        setAudioStream(null)
        setRecordingStatus('idle')
        mediaRecorderRef.current = null

        resolve(audioBlob)
      }

      mediaRecorder.stop()
    })
  }, [audioStream])

  return {
    startRecording,
    stopRecording,
    recordingStatus,
    errorMessage,
    audioStream,
  }
}
