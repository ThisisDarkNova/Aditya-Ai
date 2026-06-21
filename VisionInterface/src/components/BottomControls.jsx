import React, { useState } from 'react';
import { Mic, Terminal, Zap, Settings, X, Power, MessageCircle } from 'lucide-react';
import { motion, AnimatePresence } from 'framer-motion';

export default function BottomControls({ backend, onChat, aiState, setActivePage }) {
  const [hoveredBtn, setHoveredBtn] = useState(null);

   const controls = [
     { id: 'voice', icon: Mic, label: 'Voice', color: 'var(--color-accent)', action: () => backend.toggleVoice() },
     { id: 'command', icon: Terminal, label: 'Command', color: 'var(--color-success)', action: () => setActivePage('Home') },
     { id: 'quick', icon: Zap, label: 'Quick Action', color: 'var(--color-warning)', action: () => {} },
     { id: 'settings', icon: Settings, label: 'Settings', color: 'var(--color-text-secondary)', action: () => setActivePage('Settings') },
   ];

  return (
    <div style={{ position: 'absolute', bottom: 40, left: '50%', transform: 'translateX(-50%)', zIndex: 100, display: 'flex', flexDirection: 'column', alignItems: 'center' }}>
      
      {/* Premium Floating Dock */}
      <motion.div 
        className="glass-panel"
        initial={{ y: 50, opacity: 0 }}
        animate={{ y: 0, opacity: 1 }}
        transition={{ type: 'spring', stiffness: 300, damping: 25 }}
        style={{
          display: 'flex',
          alignItems: 'center',
          gap: 16,
          padding: '12px 24px',
          borderRadius: 32,
          background: 'rgba(17, 19, 26, 0.7)',
          boxShadow: '0 16px 40px rgba(0,0,0,0.4), inset 0 1px 0 rgba(255,255,255,0.1)'
        }}
      >
        {controls.map((btn) => (
          <div key={btn.id} style={{ position: 'relative' }} onMouseEnter={() => setHoveredBtn(btn.id)} onMouseLeave={() => setHoveredBtn(null)}>
            
            {/* Tooltip */}
            <AnimatePresence>
              {hoveredBtn === btn.id && (
                <motion.div
                  initial={{ opacity: 0, y: 10, scale: 0.9 }}
                  animate={{ opacity: 1, y: -45, scale: 1 }}
                  exit={{ opacity: 0, y: 0, scale: 0.9 }}
                  transition={{ duration: 0.2 }}
                  style={{
                    position: 'absolute',
                    top: 0,
                    left: '50%',
                    transform: 'translateX(-50%)',
                    background: 'rgba(0,0,0,0.8)',
                    backdropFilter: 'blur(10px)',
                    padding: '6px 12px',
                    borderRadius: 8,
                    fontSize: 12,
                    fontWeight: 600,
                    color: '#fff',
                    whiteSpace: 'nowrap',
                    pointerEvents: 'none'
                  }}
                >
                  {btn.label}
                </motion.div>
              )}
            </AnimatePresence>

            <motion.button
              whileHover={{ scale: 1.15, y: -4 }}
              whileTap={{ scale: 0.9 }}
              transition={{ type: 'spring', stiffness: 400, damping: 15 }}
              onClick={btn.action}
              style={{
                width: 48,
                height: 48,
                borderRadius: '50%',
                border: 'none',
                background: hoveredBtn === btn.id ? `var(--color-glass)` : 'transparent',
                display: 'flex',
                alignItems: 'center',
                justifyContent: 'center',
                cursor: 'pointer',
                boxShadow: hoveredBtn === btn.id ? `0 8px 20px ${btn.color}40, inset 0 0 0 1px ${btn.color}60` : 'none',
              }}
            >
              <btn.icon size={22} color={hoveredBtn === btn.id ? btn.color : 'var(--color-text-primary)'} />
            </motion.button>
          </div>
        ))}

        {/* Separator */}
        <div style={{ width: 1, height: 24, background: 'var(--color-border)', margin: '0 8px' }} />

        {/* Power Button */}
        <motion.button
          whileHover={{ scale: 1.1, background: 'rgba(239, 68, 68, 0.2)', boxShadow: '0 0 20px rgba(239, 68, 68, 0.4)' }}
          whileTap={{ scale: 0.9 }}
          onClick={() => backend.close()}
          style={{
            width: 40, height: 40, borderRadius: '50%', border: '1px solid rgba(239, 68, 68, 0.3)',
            background: 'transparent', display: 'flex', alignItems: 'center', justifyContent: 'center', cursor: 'pointer'
          }}
        >
          <Power size={18} color="var(--color-danger)" />
        </motion.button>

      </motion.div>
    </div>
  );
}
