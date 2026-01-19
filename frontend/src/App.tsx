import { useState } from 'react'
import { MeshGradientBackground } from './components/MeshGradientBackground'
import { ChatHistory } from './components/ChatHistory'
import type { Message } from './components/MessageBubble'

function App() {
  const [messages, setMessages] = useState<Message[]>([])

  const addMessage = (role: 'user' | 'assistant', content: string) => {
    const newMessage: Message = {
      id: crypto.randomUUID(),
      role,
      content,
      timestamp: new Date(),
    }
    setMessages(prev => [...prev, newMessage])
  }

  const handleMicClick = () => {
    addMessage('user', 'Czy macie wolne pokoje na weekend?')
    setTimeout(() => {
      addMessage('assistant', 'Dzień dobry! Tak, mamy wolne pokoje na weekend. Dysponujemy pokojami dwuosobowymi za 240 PLN za noc oraz czteroosobowymi za 400 PLN. Jakiego typu pokoju Pan/Pani szuka?')
    }, 1500)
  }

  return (
    <div className="relative min-h-screen">
      <MeshGradientBackground />
      
      <div className="relative z-10 flex flex-col h-screen">
        <header className="flex items-center justify-center py-4 border-b border-white/10">
          <h1 className="text-2xl font-bold text-white/90 tracking-tight">
            Hotel Aurora
          </h1>
        </header>

        <div className="flex-1 flex flex-col max-w-3xl mx-auto w-full">
          <ChatHistory messages={messages} />
          
          <div className="p-6 flex justify-center">
            <button 
              onClick={handleMicClick}
              className="w-16 h-16 rounded-full bg-gradient-to-br from-cyan-500 to-purple-600 flex items-center justify-center shadow-lg shadow-purple-500/25 hover:shadow-purple-500/40 hover:scale-105 transition-all"
            >
              <svg className="w-7 h-7 text-white" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M19 11a7 7 0 01-7 7m0 0a7 7 0 01-7-7m7 7v4m0 0H8m4 0h4m-4-8a3 3 0 01-3-3V5a3 3 0 116 0v6a3 3 0 01-3 3z" />
              </svg>
            </button>
          </div>
        </div>
      </div>
    </div>
  )
}

export default App
