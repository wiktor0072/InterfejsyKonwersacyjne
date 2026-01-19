import { useCallback, useState, useEffect } from 'react'
import Particles, { initParticlesEngine } from '@tsparticles/react'
import type { Container, ISourceOptions } from '@tsparticles/engine'
import { loadSlim } from '@tsparticles/slim'

export interface ParticlesBackgroundProps {
  audioIntensity?: number // 0-1, affects particle behavior
  activeSource?: 'user' | 'assistant' | null
}

// ===== Particle Configurations =====

const getParticlesConfig = (
  audioIntensity: number,
  activeSource: 'user' | 'assistant' | null
): ISourceOptions => {
  // Base particle count and speed, modified by audio intensity
  const baseCount = 50
  const count = Math.floor(baseCount + audioIntensity * 50) // 50-100 particles
  const baseSpeed = 0.5
  const speed = baseSpeed + audioIntensity * 2 // 0.5-2.5 speed

  // Color based on active source
  let particleColors: string[]
  if (activeSource === 'user') {
    particleColors = ['#06b6d4', '#22d3ee', '#67e8f9'] // Cyan shades
  } else if (activeSource === 'assistant') {
    particleColors = ['#a855f7', '#c084fc', '#d8b4fe'] // Purple shades
  } else {
    particleColors = ['#6366f1', '#818cf8', '#a5b4fc'] // Indigo shades (idle)
  }

  // Particle size varies with intensity
  const baseSize = 2
  const sizeMax = baseSize + audioIntensity * 4 // 2-6

  return {
    fullScreen: false,
    background: {
      color: 'transparent',
    },
    fpsLimit: 60,
    particles: {
      number: {
        value: count,
        density: {
          enable: true,
        },
      },
      color: {
        value: particleColors,
      },
      shape: {
        type: 'circle',
      },
      opacity: {
        value: { min: 0.1, max: 0.5 + audioIntensity * 0.3 },
        animation: {
          enable: true,
          speed: 0.5 + audioIntensity,
          sync: false,
        },
      },
      size: {
        value: { min: 1, max: sizeMax },
        animation: {
          enable: true,
          speed: 2 + audioIntensity * 3,
          sync: false,
        },
      },
      move: {
        enable: true,
        speed: speed,
        direction: 'none',
        random: true,
        straight: false,
        outModes: {
          default: 'bounce',
        },
        attract: {
          enable: audioIntensity > 0.3,
          rotate: {
            x: 600,
            y: 1200,
          },
        },
      },
      links: {
        enable: true,
        distance: 100 + audioIntensity * 50,
        color: particleColors[0],
        opacity: 0.2 + audioIntensity * 0.2,
        width: 1,
      },
    },
    interactivity: {
      events: {
        onHover: {
          enable: true,
          mode: 'grab',
        },
      },
      modes: {
        grab: {
          distance: 150,
          links: {
            opacity: 0.4,
          },
        },
      },
    },
    detectRetina: true,
  }
}

// ===== Main Component =====

export function ParticlesBackground({ 
  audioIntensity = 0,
  activeSource = null,
}: ParticlesBackgroundProps) {
  const [engineReady, setEngineReady] = useState(false)

  // Initialize particles engine once on mount
  useEffect(() => {
    console.log('[Particles] Inicjalizacja silnika tsParticles')
    initParticlesEngine(async (engine) => {
      await loadSlim(engine)
    }).then(() => {
      console.log('[Particles] Silnik gotowy')
      setEngineReady(true)
    })
  }, [])

  const particlesLoadedCallback = useCallback(async (container?: Container) => {
    if (container) {
      console.log('[Particles] Kontener załadowany')
    }
  }, [])

  const config = getParticlesConfig(audioIntensity, activeSource)

  if (!engineReady) {
    return (
      <div className="absolute inset-0 pointer-events-none" style={{ zIndex: 1 }}>
        <div className="absolute inset-0 flex items-center justify-center">
          <div className="text-white/20 text-sm">Ładowanie efektów...</div>
        </div>
      </div>
    )
  }

  return (
    <div className="absolute inset-0 pointer-events-none" style={{ zIndex: 1 }}>
      <Particles
        id="tsparticles"
        particlesLoaded={particlesLoadedCallback}
        options={config}
        className="w-full h-full"
      />
    </div>
  )
}
