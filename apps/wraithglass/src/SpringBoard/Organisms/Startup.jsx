import React, { useState, useEffect, useRef } from 'react';
import { motion, AnimatePresence } from 'framer-motion';

const VERSION = '1.0.0';

const STEPS = [
  { text: 'Initializing Cognitive Systems...', pct: 20 },
  { text: 'Loading WraithglassMemoryEngine...', pct: 50 },
  { text: 'Connecting Intelligence Layer...', pct: 80 },
  { text: 'Voice Ready ✓', pct: 100 },
];

export default function Startup({ onComplete }) {
  const [step, setStep] = useState(0);
  const onCompleteRef = useRef(onComplete);

  useEffect(() => { onCompleteRef.current = onComplete; }, [onComplete]);

  useEffect(() => {
    let timeout;
    if (step < STEPS.length - 1) {
      timeout = setTimeout(() => setStep(prev => prev + 1), 1100);
    } else {
      timeout = setTimeout(() => onCompleteRef.current(), 900);
    }
    return () => clearTimeout(timeout);
  }, [step]);

  const current = STEPS[step];

  return (
    <div style={{
      position: 'absolute', inset: 0,
      background: 'radial-gradient(ellipse at 50% 40%, #0d1020 0%, #050508 100%)',
      display: 'flex', flexDirection: 'column',
      alignItems: 'center', justifyContent: 'center',
      zIndex: 9999, gap: 0,
    }}>

      {/* Logo Orb */}
      <div style={{ position: 'relative', width: 100, height: 100, marginBottom: 36 }}>
        {/* Outer spinning ring */}
        <motion.div
          animate={{ rotate: 360 }}
          transition={{ duration: 6, repeat: Infinity, ease: 'linear' }}
          style={{
            position: 'absolute', inset: -8,
            border: '1.5px solid transparent',
            borderTopColor: '#5B8CFF',
            borderRightColor: 'rgba(91,140,255,0.3)',
            borderRadius: '50%',
          }}
        />
        {/* Inner pulsing orb */}
        <motion.div
          animate={{ scale: [1, 1.08, 1], opacity: [0.9, 1, 0.9] }}
          transition={{ duration: 2.5, repeat: Infinity, ease: 'easeInOut' }}
          style={{
            width: 100, height: 100, borderRadius: '50%',
            background: 'radial-gradient(circle at 35% 30%, #5B8CFF 0%, #3366cc 40%, #050508 100%)',
            boxShadow: '0 0 60px rgba(91,140,255,0.45), 0 0 120px rgba(91,140,255,0.15)',
            display: 'flex', alignItems: 'center', justifyContent: 'center',
          }}
        >
          <span style={{ fontSize: 28, fontWeight: 800, color: '#fff', letterSpacing: 2, fontFamily: 'Inter, sans-serif' }}>Æ</span>
        </motion.div>
      </div>

      {/* Brand name */}
      <motion.h1
        initial={{ opacity: 0, y: 8 }}
        animate={{ opacity: 1, y: 0 }}
        transition={{ duration: 0.6, delay: 0.1 }}
        style={{
          fontSize: 36, fontWeight: 800,
          letterSpacing: '0.18em', color: '#fff',
          fontFamily: 'Inter, sans-serif',
          marginBottom: 4,
        }}
      >
        VESPERA
      </motion.h1>

      {/* Version */}
      <motion.p
        initial={{ opacity: 0 }}
        animate={{ opacity: 1 }}
        transition={{ delay: 0.3 }}
        style={{ fontSize: 11, color: 'rgba(255,255,255,0.3)', letterSpacing: '0.12em', marginBottom: 48, fontFamily: 'Inter, sans-serif' }}
      >
        VERSION {VERSION} · COGNITIVE CORE
      </motion.p>

      {/* Progress bar */}
      <div style={{ width: 280, display: 'flex', flexDirection: 'column', alignItems: 'center', gap: 14 }}>
        <div style={{ width: '100%', height: 2, background: 'rgba(255,255,255,0.07)', borderRadius: 2, overflow: 'hidden' }}>
          <motion.div
            animate={{ width: `${current.pct}%` }}
            transition={{ duration: 0.8, ease: [0.16, 1, 0.3, 1] }}
            style={{ height: '100%', background: 'linear-gradient(90deg, #3366cc, #5B8CFF)', borderRadius: 2 }}
          />
        </div>

        {/* Step text */}
        <div style={{ height: 20, position: 'relative', width: '100%', display: 'flex', justifyContent: 'center' }}>
          <AnimatePresence mode="wait">
            <motion.p
              key={step}
              initial={{ opacity: 0, y: 6 }}
              animate={{ opacity: 1, y: 0 }}
              exit={{ opacity: 0, y: -6 }}
              transition={{ duration: 0.25 }}
              style={{
                position: 'absolute',
                fontSize: 12, color: 'rgba(255,255,255,0.45)',
                fontWeight: 500, letterSpacing: '0.06em',
                textTransform: 'uppercase',
                fontFamily: 'Inter, sans-serif',
              }}
            >
              {current.text}
            </motion.p>
          </AnimatePresence>
        </div>
      </div>

    </div>
  );
}
