import { useState, useEffect, useCallback, useRef } from 'react'

// ===== WebSocket Message Types =====

export interface TextMessage {
  type: 'text'
  content: string
}

export interface AudioMessage {
  type: 'audio'
  data: string // base64 encoded for outgoing, ArrayBuffer handled separately
}

export interface TranscriptionMessage {
  type: 'transcription'
  text: string
}

export interface ResponseMessage {
  type: 'response'
  text: string
  sentiment?: string
}

export interface AudioResponseMessage {
  type: 'audio'
  data: string // base64 encoded MP3
}

export interface ErrorMessage {
  type: 'error'
  message: string
}

export interface HistoryMessage {
  type: 'history'
  messages: Array<{
    role: string
    content: string
    timestamp: string
    sentiment?: string
  }>
}

export type OutgoingMessage = TextMessage | AudioMessage
export type IncomingMessage = TranscriptionMessage | ResponseMessage | AudioResponseMessage | ErrorMessage | HistoryMessage

export type ConnectionStatus = 'connecting' | 'connected' | 'disconnected' | 'error'

// ===== Hook Return Type =====

export interface UseWebSocketReturn {
  sendMessage: (message: OutgoingMessage) => void
  sendAudio: (audioBlob: Blob) => void
  lastMessage: IncomingMessage | null
  connectionStatus: ConnectionStatus
  sessionId: string
}

// ===== Constants =====

const WS_URL = 'ws://localhost:8000/ws'
const SESSION_STORAGE_KEY = 'hotel-aurora-session-id'
const MAX_RECONNECT_ATTEMPTS = 3
const BASE_RECONNECT_DELAY = 1000 // 1 second

// ===== Helper Functions =====

function getOrCreateSessionId(): string {
  let sessionId = sessionStorage.getItem(SESSION_STORAGE_KEY)
  if (!sessionId) {
    sessionId = crypto.randomUUID()
    sessionStorage.setItem(SESSION_STORAGE_KEY, sessionId)
    console.log('[WebSocket] Utworzono nowy session_id:', sessionId)
  } else {
    console.log('[WebSocket] Odczytano istniejący session_id:', sessionId)
  }
  return sessionId
}

// ===== Main Hook =====

export function useWebSocket(): UseWebSocketReturn {
  const [connectionStatus, setConnectionStatus] = useState<ConnectionStatus>('disconnected')
  const [lastMessage, setLastMessage] = useState<IncomingMessage | null>(null)
  const [sessionId] = useState<string>(getOrCreateSessionId)
  
  const wsRef = useRef<WebSocket | null>(null)
  const reconnectAttemptRef = useRef(0)
  const reconnectTimeoutRef = useRef<ReturnType<typeof setTimeout> | null>(null)

  const connect = useCallback(() => {
    // Cleanup existing connection
    if (wsRef.current) {
      wsRef.current.close()
    }

    const url = `${WS_URL}?session_id=${sessionId}`
    console.log('[WebSocket] Łączenie z:', url)
    setConnectionStatus('connecting')

    const ws = new WebSocket(url)
    wsRef.current = ws

    ws.onopen = () => {
      console.log('[WebSocket] Połączono')
      setConnectionStatus('connected')
      reconnectAttemptRef.current = 0 // Reset reconnect counter on successful connection
    }

    ws.onclose = (event) => {
      console.log('[WebSocket] Rozłączono:', event.code, event.reason)
      setConnectionStatus('disconnected')
      wsRef.current = null

      // Auto-reconnect with exponential backoff
      if (reconnectAttemptRef.current < MAX_RECONNECT_ATTEMPTS) {
        const delay = BASE_RECONNECT_DELAY * Math.pow(2, reconnectAttemptRef.current)
        console.log(`[WebSocket] Ponowna próba za ${delay}ms (próba ${reconnectAttemptRef.current + 1}/${MAX_RECONNECT_ATTEMPTS})`)
        
        reconnectTimeoutRef.current = setTimeout(() => {
          reconnectAttemptRef.current++
          connect()
        }, delay)
      } else {
        console.log('[WebSocket] Maksymalna liczba prób połączenia osiągnięta')
        setConnectionStatus('error')
      }
    }

    ws.onerror = (error) => {
      console.error('[WebSocket] Błąd:', error)
      setConnectionStatus('error')
    }

    ws.onmessage = (event) => {
      try {
        const message = JSON.parse(event.data) as IncomingMessage
        console.log('[WebSocket] Odebrano:', message.type, message)
        setLastMessage(message)
      } catch (error) {
        console.error('[WebSocket] Błąd parsowania wiadomości:', error, event.data)
      }
    }
  }, [sessionId])

  // Connect on mount, cleanup on unmount
  useEffect(() => {
    connect()

    return () => {
      console.log('[WebSocket] Czyszczenie połączenia')
      if (reconnectTimeoutRef.current) {
        clearTimeout(reconnectTimeoutRef.current)
      }
      if (wsRef.current) {
        wsRef.current.close()
      }
    }
  }, [connect])

  // Send JSON message
  const sendMessage = useCallback((message: OutgoingMessage) => {
    if (wsRef.current?.readyState === WebSocket.OPEN) {
      console.log('[WebSocket] Wysyłanie:', message.type, message)
      wsRef.current.send(JSON.stringify(message))
    } else {
      console.warn('[WebSocket] Nie można wysłać - połączenie nieaktywne')
    }
  }, [])

  // Send binary audio data
  const sendAudio = useCallback((audioBlob: Blob) => {
    if (wsRef.current?.readyState === WebSocket.OPEN) {
      console.log('[WebSocket] Wysyłanie audio:', audioBlob.size, 'bytes')
      audioBlob.arrayBuffer().then(buffer => {
        wsRef.current?.send(buffer)
      })
    } else {
      console.warn('[WebSocket] Nie można wysłać audio - połączenie nieaktywne')
    }
  }, [])

  return {
    sendMessage,
    sendAudio,
    lastMessage,
    connectionStatus,
    sessionId,
  }
}
