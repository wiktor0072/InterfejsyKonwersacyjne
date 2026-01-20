import { useEffect, useRef } from 'react'

export interface ParticlesBackgroundProps {
  audioIntensity?: number // 0-1
  activeSource?: 'user' | 'assistant' | null
}

interface Particle {
  x: number
  y: number
  baseSize: number
  currentSize: number
  targetX: number
  targetY: number
  idleX: number
  idleY: number
  idleVx: number
  idleVy: number
  color: { r: number; g: number; b: number }
  targetColor: { r: number; g: number; b: number }
  alpha: number
  targetAlpha: number
  // Organic movement properties
  angleOffset: number
  radiusOffset: number
  isDust: boolean
  phase: number
}

const HEX_COLORS = {
  user: ['#06b6d4', '#22d3ee', '#67e8f9'],     // Cyan
  assistant: ['#a855f7', '#c084fc', '#d8b4fe'], // Purple
  idle: ['#6366f1', '#818cf8', '#a5b4fc'],      // Indigo
}

// Helper to convert hex to rgb
const hexToRgb = (hex: string) => {
  const result = /^#?([a-f\d]{2})([a-f\d]{2})([a-f\d]{2})$/i.exec(hex)
  return result ? {
    r: parseInt(result[1], 16),
    g: parseInt(result[2], 16),
    b: parseInt(result[3], 16)
  } : { r: 255, g: 255, b: 255 }
}

// Precompute palettes
const PALETTES = {
  user: HEX_COLORS.user.map(hexToRgb),
  assistant: HEX_COLORS.assistant.map(hexToRgb),
  idle: HEX_COLORS.idle.map(hexToRgb),
}

export function ParticlesBackground({ 
  audioIntensity = 0,
  activeSource = null,
}: ParticlesBackgroundProps) {
  const canvasRef = useRef<HTMLCanvasElement>(null)
  const requestRef = useRef<number>(0)
  
  // Store props in refs to access in animation loop without dependencies
  const intensityRef = useRef(audioIntensity)
  const sourceRef = useRef(activeSource)

  useEffect(() => {
    intensityRef.current = audioIntensity
  }, [audioIntensity])

  useEffect(() => {
    sourceRef.current = activeSource
  }, [activeSource])

  useEffect(() => {
    const canvas = canvasRef.current
    if (!canvas) return

    const ctx = canvas.getContext('2d')
    if (!ctx) return

    // Initialize particles
    const particleCount = 200
    const particles: Particle[] = []

    const initParticles = () => {
      particles.length = 0
      for (let i = 0; i < particleCount; i++) {
        const x = Math.random() * canvas.width
        const y = Math.random() * canvas.height
        const colorIndex = Math.floor(Math.random() * 3)
        const isDust = Math.random() > 0.4
        
        particles.push({
          x,
          y,
          baseSize: isDust ? (Math.random() * 1.5 + 0.5) : (Math.random() * 2.5 + 1.5),
          currentSize: 0,
          targetX: x,
          targetY: y,
          idleX: x,
          idleY: y,
          idleVx: (Math.random() - 0.5) * (isDust ? 0.3 : 0.5),
          idleVy: (Math.random() - 0.5) * (isDust ? 0.3 : 0.5),
          color: { ...PALETTES.idle[colorIndex] },
          targetColor: { ...PALETTES.idle[colorIndex] },
          alpha: 0,
          targetAlpha: isDust ? 0.3 : 0.5,
          angleOffset: (Math.random() - 0.5) * 0.8,
          radiusOffset: (Math.random() - 0.5) * 120,
          isDust,
          phase: Math.random() * Math.PI * 2
        })
      }
    }

    const resize = () => {
      canvas.width = window.innerWidth
      canvas.height = window.innerHeight
      // Re-init particles on drastic resize to avoid off-screen
      initParticles()
    }

    window.addEventListener('resize', resize)
    resize() // Initial sizing

    // Animation Loop
    let time = 0
    const animate = () => {
      time += 0.01
      const width = canvas.width
      const height = canvas.height
      const intensity = intensityRef.current
      const source = sourceRef.current

      ctx.clearRect(0, 0, width, height)

      // Base radius for the formation
      const baseRadius = height * 0.35
      const centerY = height / 2

      particles.forEach((p, i) => {
        if (source !== null) {
          p.idleX = p.x
          p.idleY = p.y
        }

        // 1. Determine Targets based on State
        if (source === 'user') {
          // Right Semicircle (Input)
          const angleSpread = Math.PI
          const baseAngle = (Math.PI / 2) + ((i / particleCount) * angleSpread)
          const angle = baseAngle + p.angleOffset * 0.5
          
          const r = baseRadius + p.radiusOffset
          const expansion = intensity * 50
          
          p.targetX = width - 50 + Math.cos(angle) * (r + expansion)
          p.targetY = centerY + Math.sin(angle) * (r + expansion)
          
          p.targetColor = PALETTES.user[i % 3]
          p.targetAlpha = p.isDust ? 0.5 : 1.0

        } else if (source === 'assistant') {
          // Left Semicircle (Output)
          const angleSpread = Math.PI
          const baseAngle = -(Math.PI / 2) + ((i / particleCount) * angleSpread)
          const angle = baseAngle + p.angleOffset * 0.5
          
          const r = baseRadius + p.radiusOffset
          const expansion = intensity * 50

          p.targetX = 50 + Math.cos(angle) * (r + expansion)
          p.targetY = centerY + Math.sin(angle) * (r + expansion)
          
          p.targetColor = PALETTES.assistant[i % 3]
          p.targetAlpha = p.isDust ? 0.5 : 1.0

        } else {
          // Idle - Drift
          p.idleX += p.idleVx
          p.idleY += p.idleVy
          
          if (p.idleX < 0 || p.idleX > width) p.idleVx *= -1
          if (p.idleY < 0 || p.idleY > height) p.idleVy *= -1

          p.targetX = p.idleX
          p.targetY = p.idleY
          
          p.targetColor = PALETTES.idle[i % 3]
          p.targetAlpha = p.isDust ? 0.15 : 0.3
        }

        // 2. Audio Reactivity (Jitter)
        let jitterX = 0
        let jitterY = 0
        if (intensity > 0.01) {
           const shake = intensity * (p.isDust ? 30 : 60)
           jitterX = (Math.random() - 0.5) * shake
           jitterY = (Math.random() - 0.5) * shake
        }

        // 3. Move Particle (Lerp)
        const moveEasing = source ? 0.08 : 0.02
        p.x += (p.targetX + jitterX - p.x) * moveEasing
        p.y += (p.targetY + jitterY - p.y) * moveEasing

        // 4. Color & Alpha Lerp
        p.color.r += (p.targetColor.r - p.color.r) * 0.05
        p.color.g += (p.targetColor.g - p.color.g) * 0.05
        p.color.b += (p.targetColor.b - p.color.b) * 0.05
        p.alpha += (p.targetAlpha - p.alpha) * 0.05

        // 5. Size Pulse
        let targetSize = p.baseSize
        if (source === null) {
          targetSize = p.baseSize * 0.7
        } else {
          targetSize = p.baseSize + (intensity * (p.isDust ? 4 : 8))
        }
        p.currentSize += (targetSize - p.currentSize) * 0.1

        // 6. Draw
        if (p.alpha > 0.01) {
          ctx.beginPath()
          ctx.arc(p.x, p.y, Math.max(0, p.currentSize), 0, Math.PI * 2)
          
          const { r, g, b } = p.color
          const twinkle = p.isDust ? Math.sin(time * 2 + p.phase) * 0.1 : 0
          const finalAlpha = Math.max(0, Math.min(1, p.alpha + twinkle))
          
          ctx.fillStyle = `rgba(${Math.round(r)}, ${Math.round(g)}, ${Math.round(b)}, ${finalAlpha})`
          
          if (source && intensity > 0.1 && !p.isDust) {
            ctx.shadowBlur = 15 * intensity
            ctx.shadowColor = ctx.fillStyle
          } else {
            ctx.shadowBlur = 0
          }
          
          ctx.fill()
          ctx.shadowBlur = 0
        }
      })
      
      requestRef.current = requestAnimationFrame(animate)
    }

    requestRef.current = requestAnimationFrame(animate)

    return () => {
      window.removeEventListener('resize', resize)
      if (requestRef.current) cancelAnimationFrame(requestRef.current)
    }
  }, []) // Empty deps - refs handle updates

  return (
    <div className="absolute inset-0 pointer-events-none" style={{ zIndex: 0 }}>
      <canvas 
        ref={canvasRef}
        className="block w-full h-full"
      />
    </div>
  )
}
