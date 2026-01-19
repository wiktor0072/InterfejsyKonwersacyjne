function App() {
  return (
    <div className="relative min-h-screen bg-gradient-to-br from-slate-900 via-purple-900 to-slate-900">
      <div className="absolute inset-0 bg-[radial-gradient(ellipse_at_top,_var(--tw-gradient-stops))] from-purple-900/20 via-transparent to-transparent" />
      
      <div className="relative z-10 flex flex-col h-screen">
        <header className="flex items-center justify-center py-6">
          <h1 className="text-3xl font-bold text-white/90 tracking-tight">
            Hotel Aurora
          </h1>
        </header>

        <main className="flex-1 flex flex-col items-center justify-center p-8">
          <div className="w-full max-w-2xl bg-white/5 backdrop-blur-sm rounded-2xl border border-white/10 p-6">
            <div className="text-center text-white/60">
              <p className="text-lg">Witaj w Hotelu Aurora</p>
              <p className="text-sm mt-2">Naciśnij przycisk mikrofonu, aby rozpocząć rozmowę</p>
            </div>
          </div>

          <div className="mt-8">
            <button className="w-20 h-20 rounded-full bg-gradient-to-br from-cyan-500 to-purple-600 flex items-center justify-center shadow-lg shadow-purple-500/25 hover:shadow-purple-500/40 transition-shadow">
              <svg className="w-8 h-8 text-white" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M19 11a7 7 0 01-7 7m0 0a7 7 0 01-7-7m7 7v4m0 0H8m4 0h4m-4-8a3 3 0 01-3-3V5a3 3 0 116 0v6a3 3 0 01-3 3z" />
              </svg>
            </button>
          </div>
        </main>
      </div>
    </div>
  )
}

export default App
