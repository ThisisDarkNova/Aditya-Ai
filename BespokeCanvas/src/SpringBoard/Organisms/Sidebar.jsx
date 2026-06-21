import React, { useState } from 'react';
import { Home, User, Settings, Mic, Wifi, Shield, MessageCircle, ChevronRight, ChevronLeft, GitMerge } from 'lucide-react';
import { motion, AnimatePresence } from 'framer-motion';
import Tooltip from './Atoms/Tooltip';

const navItems = [
  { id: 'Home', icon: Home, label: 'Home' },
  { id: 'Profile', icon: User, label: 'Profile' },
  { id: 'Settings', icon: Settings, label: 'Settings' },
  { id: 'SkillTree', icon: GitMerge, label: 'Skill Tree' },
];

export default function Sidebar({ activePage, setActivePage, status, isConnected, aiState }) {
  const [pinned, setPinned] = useState(false); // locked open
  const [hovered, setHovered] = useState(false);

  const expanded = pinned || hovered;

  return (
    <motion.aside
      className="glass-panel"
      animate={{ width: expanded ? 220 : 72 }}
      transition={{ type: 'spring', stiffness: 320, damping: 32 }}
      onMouseEnter={() => setHovered(true)}
      onMouseLeave={() => setHovered(false)}
      style={{
        display: 'flex',
        flexDirection: 'column',
        height: '100%',
        overflow: 'hidden',
        position: 'relative',
      }}
    >
      {/* Top: Logo + pin toggle */}
      <div style={{ padding: '20px 0 16px', display: 'flex', flexDirection: 'column', alignItems: 'center', gap: 8 }}>
        <motion.div
          animate={
            aiState === 'listening' ? { scale: [1, 1.1, 1], borderRadius: ['25%', '40%', '25%'] } :
            aiState === 'thinking' ? { rotate: [0, 180, 360], borderRadius: ['25%', '50%', '25%'] } :
            aiState === 'speaking' ? { scale: [1, 1.05, 1], filter: ['hue-rotate(0deg)', 'hue-rotate(30deg)', 'hue-rotate(0deg)'] } :
            { scale: 1, rotate: 0, borderRadius: '35%' }
          }
          transition={{ 
            duration: aiState === 'thinking' ? 3 : aiState === 'listening' ? 1.5 : 2, 
            repeat: Infinity, 
            ease: 'easeInOut' 
          }}
          style={{
            width: 40, height: 40,
            background: 'linear-gradient(135deg, var(--color-accent), #4F35B5)',
            display: 'flex', alignItems: 'center', justifyContent: 'center',
            boxShadow: '0 4px 16px var(--color-accent-glow)',
            flexShrink: 0,
          }}
        >
          <motion.span 
            animate={{ opacity: aiState === 'thinking' ? [1, 0.5, 1] : 1 }}
            transition={{ duration: 1.5, repeat: Infinity }}
            style={{ color: '#fff', fontSize: 16, fontWeight: 700 }}
          >
            Æ
          </motion.span>
        </motion.div>

        {/* Collapse/expand pin button — only visible when expanded */}
        <AnimatePresence>
          {expanded && (
            <motion.button
              initial={{ opacity: 0, scale: 0.8 }}
              animate={{ opacity: 1, scale: 1 }}
              exit={{ opacity: 0, scale: 0.8 }}
              transition={{ duration: 0.15 }}
              onClick={() => setPinned(p => !p)}
              title={pinned ? 'Unpin sidebar' : 'Pin sidebar open'}
              style={{
                width: 28, height: 28, borderRadius: 8,
                background: pinned ? 'var(--color-accent-glow)' : 'var(--color-glass)',
                border: `1px solid ${pinned ? 'var(--color-accent)' : 'var(--color-border)'}`,
                color: pinned ? 'var(--color-accent)' : 'var(--color-text-muted)',
                cursor: 'pointer',
                display: 'flex', alignItems: 'center', justifyContent: 'center',
                transition: 'all 0.2s',
              }}
            >
              {pinned ? <ChevronLeft size={14} /> : <ChevronRight size={14} />}
            </motion.button>
          )}
        </AnimatePresence>
      </div>

      {/* Divider */}
      <div style={{ height: 1, background: 'var(--color-border)', margin: '0 12px 12px' }} />

      {/* Middle: Navigation */}
      <nav style={{ flex: 1, display: 'flex', flexDirection: 'column', gap: 4, padding: '0 10px' }}>
        {navItems.map(({ id, icon: Icon, label }) => {
          const isActive = activePage === id;
          return (
            <motion.button
              key={id}
              whileHover={{
                scale: 1.04,
                backgroundColor: isActive ? 'var(--color-glass-hover)' : 'var(--color-glass)',
                color: 'var(--color-text-primary)',
              }}
              whileTap={{ scale: 0.97 }}
              onClick={() => setActivePage(id)}
              className="smooth-transition"
              style={{
                position: 'relative',
                display: 'flex',
                alignItems: 'center',
                height: 48,
                borderRadius: 14,
                border: 'none',
                cursor: 'pointer',
                background: isActive ? 'var(--color-glass-hover)' : 'transparent',
                padding: '0 13px',
                color: isActive ? 'var(--color-text-primary)' : 'var(--color-text-secondary)',
                overflow: 'hidden',
                boxShadow: isActive ? '0 0 15px rgba(91, 140, 255, 0.08)' : 'none'
              }}
            >
              {/* Active indicator bar */}
              {isActive && (
                <motion.div
                  layoutId="activeTabSidebar"
                  style={{
                    position: 'absolute',
                    left: 0, top: '20%', bottom: '20%',
                    width: 3, borderRadius: 4,
                    background: 'var(--color-accent)',
                    boxShadow: '0 0 10px var(--color-accent-glow)',
                  }}
                />
              )}
              <Icon size={20} style={{ flexShrink: 0 }} />
              <AnimatePresence>
                {expanded && (
                  <motion.span
                    initial={{ opacity: 0, x: -8 }}
                    animate={{ opacity: 1, x: 0 }}
                    exit={{ opacity: 0, x: -8 }}
                    transition={{ duration: 0.18 }}
                    style={{ marginLeft: 14, fontSize: 14, fontWeight: 500, whiteSpace: 'nowrap' }}
                  >
                    {label}
                  </motion.span>
                )}
              </AnimatePresence>
            </motion.button>
          );
        })}
      </nav>

      {/* Bottom: Status Indicators */}
      <div style={{ padding: '16px 10px', borderTop: '1px solid var(--color-border)', display: 'flex', flexDirection: 'column', gap: 10 }}>
        {[
          { icon: Wifi, color: isConnected ? 'var(--color-success)' : 'var(--color-danger)', label: isConnected ? 'Connected' : 'Offline' },
          { icon: Mic, color: 'var(--color-accent)', label: 'Voice Ready' },
          { icon: Shield, color: 'var(--color-text-muted)', label: 'ADITYA OS v1.0' },
        ].map(({ icon: Icon, color, label }, i) => (
          <div key={i} style={{ display: 'flex', alignItems: 'center', padding: '0 3px' }}>
            <Icon size={17} color={color} style={{ flexShrink: 0 }} />
            <AnimatePresence>
              {expanded && (
                <motion.span
                  initial={{ opacity: 0 }} animate={{ opacity: 1 }} exit={{ opacity: 0 }}
                  transition={{ duration: 0.15 }}
                  style={{ marginLeft: 10, fontSize: 11, fontWeight: 500, color: 'var(--color-text-muted)', whiteSpace: 'nowrap' }}
                >
                  {label}
                </motion.span>
              )}
            </AnimatePresence>
          </div>
        ))}
      </div>
    </motion.aside>
  );
}
