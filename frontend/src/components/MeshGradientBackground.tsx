import { useEffect, useRef } from 'react'

export function MeshGradientBackground() {
  const canvasRef = useRef<HTMLCanvasElement>(null)

  useEffect(() => {
    const canvas = canvasRef.current
    if (!canvas) return

    const ctx = canvas.getContext('2d')
    if (!ctx) return

    let animationId: number
    let time = 0

    const resize = () => {
      canvas.width = window.innerWidth
      canvas.height = window.innerHeight
    }

    const colors = [
      { r: 88, g: 28, b: 135 },   // purple-900
      { r: 30, g: 27, b: 75 },    // indigo-950
      { r: 15, g: 23, b: 42 },    // slate-900
      { r: 59, g: 7, b: 100 },    // purple-950
    ]

    const blobs = colors.map((color) => ({
      x: Math.random() * 0.8 + 0.1,
      y: Math.random() * 0.8 + 0.1,
      vx: (Math.random() - 0.5) * 0.0003,
      vy: (Math.random() - 0.5) * 0.0003,
      color,
      radius: 0.4 + Math.random() * 0.3,
    }))

    const animate = () => {
      time += 0.016
      
      blobs.forEach(blob => {
        blob.x += blob.vx + Math.sin(time * 0.5 + blob.y * 10) * 0.0001
        blob.y += blob.vy + Math.cos(time * 0.3 + blob.x * 10) * 0.0001
        
        if (blob.x < 0.1 || blob.x > 0.9) blob.vx *= -1
        if (blob.y < 0.1 || blob.y > 0.9) blob.vy *= -1
        
        blob.x = Math.max(0.1, Math.min(0.9, blob.x))
        blob.y = Math.max(0.1, Math.min(0.9, blob.y))
      })

      ctx.fillStyle = '#0a0a0f'
      ctx.fillRect(0, 0, canvas.width, canvas.height)

      blobs.forEach(blob => {
        const gradient = ctx.createRadialGradient(
          blob.x * canvas.width,
          blob.y * canvas.height,
          0,
          blob.x * canvas.width,
          blob.y * canvas.height,
          blob.radius * Math.min(canvas.width, canvas.height)
        )
        
        const { r, g, b } = blob.color
        gradient.addColorStop(0, `rgba(${r}, ${g}, ${b}, 0.8)`)
        gradient.addColorStop(0.5, `rgba(${r}, ${g}, ${b}, 0.3)`)
        gradient.addColorStop(1, `rgba(${r}, ${g}, ${b}, 0)`)
        
        ctx.fillStyle = gradient
        ctx.fillRect(0, 0, canvas.width, canvas.height)
      })

      animationId = requestAnimationFrame(animate)
    }

    resize()
    window.addEventListener('resize', resize)
    animate()

    return () => {
      window.removeEventListener('resize', resize)
      cancelAnimationFrame(animationId)
    }
  }, [])

  return (
    <canvas
      ref={canvasRef}
      className="fixed inset-0 -z-10"
      style={{ background: '#0a0a0f' }}
    />
  )
}
