import React from 'react';
import { motion } from 'framer-motion';

export default function TelemetryWidget() {
  // Purely transparent widget using Apple-style glassmorphism
  return (
    <div style={{ width: '100vw', height: '100vh', background: 'transparent', display: 'flex', alignItems: 'flex-start', justifyContent: 'flex-end', padding: '40px' }}>
      <motion.div
        initial={{ opacity: 0, scale: 0.9 }}
        animate={{ opacity: 1, scale: 1 }}
        style={{
          width: '200px',
          padding: '20px',
          background: 'rgba(0,0,0,0.3)',
          backdropFilter: 'blur(16px)',
          borderRadius: '16px',
          border: '1px solid rgba(255,255,255,0.1)',
          color: 'white',
          fontFamily: '"Inter", sans-serif'
        }}
      >
        <div style={{ display: 'flex', justifyContent: 'space-between', marginBottom: '12px' }}>
          <span style={{ opacity: 0.6, fontSize: '12px', textTransform: 'uppercase', letterSpacing: '0.1em' }}>Core Temp</span>
          <span style={{ fontWeight: 600 }}>45°C</span>
        </div>
        <div style={{ display: 'flex', justifyContent: 'space-between' }}>
          <span style={{ opacity: 0.6, fontSize: '12px', textTransform: 'uppercase', letterSpacing: '0.1em' }}>Heart Rate</span>
          <span style={{ fontWeight: 600, color: '#ff4d4d' }}>82 BPM</span>
        </div>
      </motion.div>
    </div>
  );
}
