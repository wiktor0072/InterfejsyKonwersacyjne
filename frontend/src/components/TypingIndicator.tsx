export interface TypingIndicatorProps {
  className?: string
}

export function TypingIndicator({ className = '' }: TypingIndicatorProps) {
  return (
    <div className={`flex items-center gap-1.5 ${className}`}>
      <span 
        className="w-2 h-2 bg-white/50 rounded-full animate-bounce"
        style={{ animationDelay: '0ms', animationDuration: '0.6s' }}
      />
      <span 
        className="w-2 h-2 bg-white/50 rounded-full animate-bounce"
        style={{ animationDelay: '150ms', animationDuration: '0.6s' }}
      />
      <span 
        className="w-2 h-2 bg-white/50 rounded-full animate-bounce"
        style={{ animationDelay: '300ms', animationDuration: '0.6s' }}
      />
    </div>
  )
}

// Assistant is thinking/processing indicator
export interface ThinkingIndicatorProps {
  text?: string
}

export function ThinkingIndicator({ text = 'Asystent myśli' }: ThinkingIndicatorProps) {
  return (
    <div className="flex items-start animate-fadeIn">
      <div className="bg-white/10 text-white/70 px-4 py-3 rounded-2xl rounded-bl-md">
        <div className="flex items-center gap-3">
          <TypingIndicator />
          <span className="text-sm text-white/40">{text}...</span>
        </div>
      </div>
    </div>
  )
}

// Processing overlay
export interface ProcessingOverlayProps {
  isVisible: boolean
  text?: string
}

export function ProcessingOverlay({ isVisible, text = 'Przetwarzanie' }: ProcessingOverlayProps) {
  if (!isVisible) return null

  return (
    <div className="fixed inset-0 z-40 flex items-center justify-center bg-black/20 backdrop-blur-sm animate-fadeIn">
      <div className="bg-white/10 rounded-2xl px-8 py-6 flex flex-col items-center gap-4">
        {/* Spinner */}
        <div className="w-10 h-10 border-3 border-white/20 border-t-purple-500 rounded-full animate-spin" />
        <span className="text-white/70 text-sm">{text}...</span>
      </div>
    </div>
  )
}

// Speaking indicator (when TTS is playing)
export interface SpeakingIndicatorProps {
  isVisible: boolean
}

export function SpeakingIndicator({ isVisible }: SpeakingIndicatorProps) {
  if (!isVisible) return null

  return (
    <div className="fixed bottom-24 left-1/2 -translate-x-1/2 z-30">
      <div className="bg-purple-500/20 border border-purple-500/30 rounded-full px-4 py-2 flex items-center gap-2 animate-fadeIn">
        {/* Sound wave animation */}
        <span className="flex gap-0.5 items-center h-4">
          {[1, 2, 3, 4, 5].map((i) => (
            <span 
              key={i}
              className="w-0.5 bg-purple-400 rounded-full animate-pulse"
              style={{ 
                height: `${8 + Math.random() * 8}px`,
                animationDelay: `${i * 100}ms`,
                animationDuration: '0.5s'
              }}
            />
          ))}
        </span>
        <span className="text-purple-300 text-xs font-medium">Asystent mówi</span>
      </div>
    </div>
  )
}

// Listening indicator (when recording)
export interface ListeningIndicatorProps {
  isVisible: boolean
}

export function ListeningIndicator({ isVisible }: ListeningIndicatorProps) {
  if (!isVisible) return null

  return (
    <div className="fixed bottom-24 left-1/2 -translate-x-1/2 z-30">
      <div className="bg-cyan-500/20 border border-cyan-500/30 rounded-full px-4 py-2 flex items-center gap-2 animate-pulse">
        {/* Recording dot */}
        <span className="w-2 h-2 bg-red-500 rounded-full animate-pulse" />
        <span className="text-cyan-300 text-xs font-medium">Nagrywanie...</span>
      </div>
    </div>
  )
}
