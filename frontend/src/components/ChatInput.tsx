import { useState } from 'react'
import type { FormEvent, KeyboardEvent } from 'react'

interface ChatInputProps {
  onSendMessage: (text: string) => void
  disabled?: boolean
  placeholder?: string
}

export function ChatInput({ onSendMessage, disabled, placeholder = "Wpisz wiadomość..." }: ChatInputProps) {
  const [message, setMessage] = useState('')

  const handleSubmit = (e?: FormEvent) => {
    e?.preventDefault()
    if (message.trim() && !disabled) {
      onSendMessage(message.trim())
      setMessage('')
    }
  }

  const handleKeyDown = (e: KeyboardEvent<HTMLInputElement>) => {
    if (e.key === 'Enter' && !e.shiftKey) {
      e.preventDefault()
      handleSubmit()
    }
  }

  return (
    <form onSubmit={handleSubmit} className="w-full max-w-2xl mx-auto mt-4">
      <div className="relative flex items-center gap-2">
        <input
          type="text"
          value={message}
          onChange={(e) => setMessage(e.target.value)}
          onKeyDown={handleKeyDown}
          disabled={disabled}
          placeholder={placeholder}
          className="w-full bg-white/5 border border-white/10 rounded-xl px-4 py-3 pr-12 
                     text-white placeholder-white/30 focus:outline-none focus:ring-2 focus:ring-cyan-500/50 
                     focus:border-transparent backdrop-blur-sm transition-all
                     disabled:opacity-50 disabled:cursor-not-allowed"
        />
        <button
          type="submit"
          disabled={!message.trim() || disabled}
          className="absolute right-2 p-2 rounded-lg bg-white/10 hover:bg-white/20 
                     text-white/80 hover:text-white transition-all disabled:opacity-30 
                     disabled:cursor-not-allowed disabled:hover:bg-white/10"
          title="Wyślij wiadomość"
        >
          <svg 
            className="w-5 h-5 transform rotate-90" 
            fill="none" 
            stroke="currentColor" 
            viewBox="0 0 24 24"
          >
            <path 
              strokeLinecap="round" 
              strokeLinejoin="round" 
              strokeWidth={2} 
              d="M12 19l9 2-9-18-9 18 9-2zm0 0v-8" 
            />
          </svg>
        </button>
      </div>
    </form>
  )
}
