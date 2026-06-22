import React, { useEffect, useState } from 'react';
import { motion, AnimatePresence } from 'framer-motion';

export default function BootSequence({ onComplete }) {
  const [stage, setStage] = useState('blackout');

  useEffect(() => {
    // Stage 1: Absolute darkness
    const t1 = setTimeout(() => {
      // Stage 2: Fast logo fade-in
      const audio = new Audio('/sounds/bass_swell.wav');
      audio.volume = 0.3; // Subtle acoustic feedback
      audio.play().catch(() => {});
      setStage('reveal');
    }, 200);

    // Stage 3: Fast Diagnostics check
    const t2 = setTimeout(() => {
      setStage('diagnostics');
    }, 500);

    // Stage 4: Fade out and hand off to main OS
    const t3 = setTimeout(() => {
      setStage('complete');
      setTimeout(onComplete, 400);
    }, 1000);

    return () => {
      clearTimeout(t1);
      clearTimeout(t2);
      clearTimeout(t3);
    };
  }, [onComplete]);

  return (
    <AnimatePresence>
      {stage !== 'complete' && (
        <motion.div
          initial={{ opacity: 1 }}
          exit={{ opacity: 0, filter: 'blur(10px)' }}
          transition={{ duration: 0.4, ease: 'easeInOut' }}
          style={{
            position: 'fixed',
            inset: 0,
            background: '#050B14',
            zIndex: 9999,
            display: 'flex',
            flexDirection: 'column',
            alignItems: 'center',
            justifyContent: 'center',
            color: '#F8F9FA'
          }}
        >
          {/* Logo Reveal */}
          <motion.div
            initial={{ opacity: 0, scale: 0.98, filter: 'blur(5px)' }}
            animate={stage === 'blackout' ? {} : { opacity: 1, scale: 1, filter: 'blur(0px)' }}
            transition={{ duration: 0.6, ease: 'easeOut' }}
            style={{ textAlign: 'center' }}
          >
            <h1 style={{ fontFamily: 'var(--font-serif)', fontSize: 72, fontWeight: 400, letterSpacing: '0.1em' }}>
              VESPERA
            </h1>
            <p style={{ fontFamily: 'var(--font-sans)', fontSize: 14, letterSpacing: '0.4em', color: 'rgba(255,255,255,0.4)', marginTop: 8 }}>
              SENTIENT COGNITIVE OS
            </p>
          </motion.div>

          {/* Diagnostics Reveal */}
          <motion.div
            initial={{ opacity: 0, y: 20 }}
            animate={stage === 'diagnostics' ? { opacity: 1, y: 0 } : {}}
            transition={{ duration: 1 }}
            style={{
              position: 'absolute',
              bottom: 80,
              fontFamily: 'var(--font-mono)',
              fontSize: 12,
              color: 'var(--color-accent)',
              opacity: 0.6,
              textAlign: 'center',
              textTransform: 'uppercase',
              letterSpacing: 2
            }}
          >
            <p>Initializing Neural Subsystems...</p>
            <p style={{ opacity: 0.5, marginTop: 4 }}>Engine Online</p>
          </motion.div>
        </motion.div>
      )}
    </AnimatePresence>
  );
}
