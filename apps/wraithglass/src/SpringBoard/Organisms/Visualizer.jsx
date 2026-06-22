import { motion, useAnimation } from 'framer-motion';

// Particle dots for Researching state
const particles = Array.from({ length: 12 }, (_, i) => ({
  angle: (i / 12) * 360,
  delay: i * 0.08,
  size: 3 + (i % 4)
}));

export default function Visualizer({ aiState, statusMessage }) {
  const orbControls = useAnimation();
  const ring1Controls = useAnimation();
  const ring2Controls = useAnimation();

  const getStateConfig = () => {
    switch(aiState) {
      case 'listening':
        return {
          core: 'radial-gradient(circle at 35% 35%, #93C5FD, #3B82F6, #08090D 85%)',
          shadow: '0 0 80px rgba(59, 130, 246, 0.8)',
          ring1: 'rgba(59, 130, 246, 0.5)',
          ring2: 'rgba(59, 130, 246, 0.25)',
          label: 'Listening',
          pulse: [1, 1.12, 1],
          speed: 1.2,
        };
      case 'thinking':
        return {
          core: 'radial-gradient(circle at 35% 35%, #C4B5FD, #8B5CF6, #08090D 85%)',
          shadow: '0 0 80px rgba(139, 92, 246, 0.8)',
          ring1: 'rgba(139, 92, 246, 0.5)',
          ring2: 'rgba(139, 92, 246, 0.25)',
          label: 'Thinking',
          pulse: [1, 0.95, 1.05, 1],
          speed: 2,
        };
      case 'researching':
        return {
          core: 'radial-gradient(circle at 35% 35%, #FDE68A, #F59E0B, #08090D 85%)',
          shadow: '0 0 80px rgba(245, 158, 11, 0.8)',
          ring1: 'rgba(245, 158, 11, 0.5)',
          ring2: 'rgba(245, 158, 11, 0.25)',
          label: 'Researching',
          pulse: [1, 1.08, 0.98, 1.1, 1],
          speed: 1.8,
        };
      case 'speaking':
        return {
          core: 'radial-gradient(circle at 35% 35%, #86EFAC, #22C55E, #08090D 85%)',
          shadow: '0 0 80px rgba(34, 197, 94, 0.8)',
          ring1: 'rgba(34, 197, 94, 0.5)',
          ring2: 'rgba(34, 197, 94, 0.25)',
          label: 'Speaking',
          pulse: [1, 1.15, 1.05, 1.2, 1],
          speed: 1,
        };
      default: // idle
        return {
          core: 'radial-gradient(circle at 35% 35%, rgba(255,255,255,0.3), rgba(91, 140, 255, 0.4), #08090D 85%)',
          shadow: '0 0 30px rgba(91, 140, 255, 0.2)',
          ring1: 'rgba(91, 140, 255, 0.15)',
          ring2: 'rgba(91, 140, 255, 0.08)',
          label: aiState || 'Idle',
          pulse: [1, 1.02, 1],
          speed: 4,
        };
    }
  };

  const config = getStateConfig();

  return (
    <div style={{
      position: 'absolute', inset: 0,
      display: 'flex', flexDirection: 'column',
      alignItems: 'center', justifyContent: 'center',
      pointerEvents: 'none'
    }}>
      {/* Ambient Glow BG */}
      <motion.div
        animate={{ opacity: [0.3, 0.6, 0.3] }}
        transition={{ duration: config.speed * 1.5, repeat: Infinity, ease: 'easeInOut' }}
        style={{
          position: 'absolute',
          width: 500, height: 500,
          borderRadius: '50%',
          background: `radial-gradient(circle, ${config.ring1} 0%, transparent 70%)`,
          filter: 'blur(60px)',
        }}
      />

      {/* Orb Container */}
      <div style={{ position: 'relative', width: 300, height: 300, display: 'flex', alignItems: 'center', justifyContent: 'center' }}>

        {/* Outer Rotating Ring */}
        <motion.div
          animate={{ rotate: 360 }}
          transition={{ duration: aiState === 'thinking' ? 8 : 20, repeat: Infinity, ease: 'linear' }}
          style={{
            position: 'absolute', width: 280, height: 280,
            borderRadius: '50%',
            border: `1.5px solid ${config.ring1}`,
            borderRightColor: 'transparent',
            borderBottomColor: 'transparent',
            opacity: aiState && aiState !== 'idle' ? 1 : 0.3
          }}
        />

        {/* Inner Counter-Rotating Ring */}
        <motion.div
          animate={{ rotate: -360 }}
          transition={{ duration: aiState === 'listening' ? 6 : 12, repeat: Infinity, ease: 'linear' }}
          style={{
            position: 'absolute', width: 240, height: 240,
            borderRadius: '50%',
            border: `1px dashed ${config.ring2}`,
            borderTopColor: 'transparent',
            opacity: aiState && aiState !== 'idle' ? 1 : 0.2
          }}
        />

        {/* Golden Particles (Researching only) */}
        {aiState === 'researching' && particles.map((p, i) => (
          <motion.div
            key={i}
            animate={{
              x: [
                Math.cos((p.angle * Math.PI) / 180) * 120,
                Math.cos(((p.angle + 30) * Math.PI) / 180) * 140,
                Math.cos((p.angle * Math.PI) / 180) * 120,
              ],
              y: [
                Math.sin((p.angle * Math.PI) / 180) * 120,
                Math.sin(((p.angle + 30) * Math.PI) / 180) * 140,
                Math.sin((p.angle * Math.PI) / 180) * 120,
              ],
              opacity: [0.6, 1, 0.6],
            }}
            transition={{ duration: 2 + p.delay, repeat: Infinity, ease: 'easeInOut', delay: p.delay }}
            style={{
              position: 'absolute',
              width: p.size, height: p.size,
              borderRadius: '50%',
              background: '#F59E0B',
              boxShadow: `0 0 ${p.size * 2}px rgba(245, 158, 11, 0.8)`,
            }}
          />
        ))}

        {/* Core 3D Orb with Liquid Shader */}
        <motion.div
          animate={{ scale: config.pulse, boxShadow: [config.shadow, config.shadow.replace('0.8', '1'), config.shadow] }}
          transition={{ duration: config.speed, repeat: Infinity, ease: 'easeInOut' }}
          style={{
            width: 200, height: 200,
            borderRadius: '50%',
            background: config.core,
            border: '1px solid rgba(255,255,255,0.15)',
            display: 'flex',
            alignItems: 'center',
            justifyContent: 'center',
            overflow: 'hidden',
            position: 'relative',
            filter: 'url(#liquid-shader)'
          }}
        >
          {/* SVG liquid shader definitions */}
          <svg style={{ position: 'absolute', width: 0, height: 0 }}>
            <defs>
              <filter id="liquid-shader">
                <feTurbulence type="fractalNoise" baseFrequency="0.015" numOctaves="3" result="noise" />
                <feDisplacementMap in="SourceGraphic" in2="noise" scale="18" xChannelSelector="R" yChannelSelector="G" />
              </filter>
            </defs>
          </svg>

          {/* 3D Specular Highlight */}
          <div style={{
            position: 'absolute', top: '10%', left: '15%',
            width: '40%', height: '40%',
            background: 'radial-gradient(circle, rgba(255,255,255,0.5) 0%, transparent 70%)',
            borderRadius: '50%',
            transform: 'rotate(-45deg)'
          }} />

          {/* State Text */}
          <span style={{
            position: 'relative', zIndex: 10,
            fontSize: 12, fontWeight: 700,
            color: '#fff',
            textTransform: 'uppercase',
            letterSpacing: 3,
            textShadow: '0 2px 8px rgba(0,0,0,0.6)'
          }}>
            {config.label}
          </span>
        </motion.div>
      </div>

      {/* Status Message */}
      <motion.p
        initial={{ opacity: 0 }}
        animate={{ opacity: 1 }}
        transition={{ delay: 0.3 }}
        style={{
          marginTop: 48,
          fontSize: 16,
          color: 'var(--color-text-secondary)',
          fontWeight: 500,
          letterSpacing: 0.5,
          textAlign: 'center'
        }}
      >
        {statusMessage}
      </motion.p>
    </div>
  );
}
