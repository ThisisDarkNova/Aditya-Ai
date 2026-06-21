import React from 'react';
import { motion } from 'framer-motion';
import { PERSONAS, STAGGER } from '../../../constants';

const stagger = STAGGER;

export default function AppearanceTab({ activePersona, onSelectPersona }) {
  return (
    <motion.div variants={stagger} initial="hidden" animate="visible" className="flex flex-col gap-6">
      <div>
        <h2 style={{ fontSize: 24, fontWeight: 600, marginBottom: 4 }}>Appearance</h2>
        <p style={{ fontSize: 14, color: 'var(--color-text-secondary)' }}>Choose your ADITYA persona theme. Changes apply instantly.</p>
      </div>

      <div style={{ display: 'grid', gridTemplateColumns: '1fr 1fr 1fr', gap: 14 }}>
        {PERSONAS.map(theme => {
          const isActive = activePersona === theme.id;
          return (
            <motion.div
              key={theme.id}
              whileHover={{ scale: 1.03 }}
              whileTap={{ scale: 0.97 }}
              onClick={() => onSelectPersona?.(theme.id)}
              className="glass-panel"
              style={{
                padding: 20, cursor: 'pointer',
                position: 'relative',
                border: '1px solid var(--color-border)',
                transition: 'border-color 0.3s',
              }}
            >
              {isActive && (
                <motion.div
                  layoutId="activeThemeOutline"
                  style={{
                    position: 'absolute',
                    inset: 0,
                    border: `2px solid ${theme.accent}`,
                    boxShadow: `0 0 25px ${theme.accent}35`,
                    borderRadius: 24,
                    pointerEvents: 'none',
                    zIndex: 10,
                  }}
                  transition={{ type: 'spring', stiffness: 350, damping: 26 }}
                />
              )}
              <div style={{
                height: 72, borderRadius: 10,
                background: `radial-gradient(circle at 30% 30%, ${theme.accent}60, ${theme.bg})`,
                marginBottom: 14,
                display: 'flex', alignItems: 'center', justifyContent: 'center',
                fontSize: 28,
              }}>
                {theme.emoji}
              </div>
              <div style={{ display: 'flex', alignItems: 'center', justifyContent: 'space-between' }}>
                <div>
                  <h4 style={{ fontSize: 15, fontWeight: 600, color: isActive ? theme.accent : '#fff' }}>{theme.label}</h4>
                  <p style={{ fontSize: 12, color: 'var(--color-text-muted)', marginTop: 2 }}>{theme.desc}</p>
                </div>
                {isActive && (
                  <div style={{ width: 20, height: 20, borderRadius: '50%', background: theme.accent, display: 'flex', alignItems: 'center', justifyContent: 'center', zIndex: 11 }}>
                    <svg width="10" height="10" viewBox="0 0 10 10" fill="none">
                      <path d="M2 5l2 2 4-4" stroke="#fff" strokeWidth="1.5" strokeLinecap="round" strokeLinejoin="round" />
                    </svg>
                  </div>
                )}
              </div>
            </motion.div>
          );
        })}
      </div>

      <div className="glass-panel" style={{ padding: 20 }}>
        <p style={{ fontSize: 13, color: 'var(--color-text-muted)', lineHeight: 1.6 }}>
          💡 <strong style={{ color: 'var(--color-text-secondary)' }}>Tip:</strong> You can also switch persona from the Home page using the mode switcher at the top.
        </p>
      </div>
    </motion.div>
  );
}
