import React from 'react';
import { motion } from 'framer-motion';
import { STAGGER } from '../../../constants';

const stagger = STAGGER;

export default function VoiceTab() {
  return (
    <motion.div variants={stagger} initial="hidden" animate="visible" className="flex flex-col gap-6">
      <h2 style={{ fontSize: 24, fontWeight: 600, marginBottom: 8 }}>Voice Engine</h2>
      <div className="glass-panel" style={{ padding: 24, display: 'flex', flexDirection: 'column', gap: 24 }}>
        <div>
          <h4 style={{ fontSize: 16, fontWeight: 500, marginBottom: 4 }}>Voice Selection</h4>
          <select className="glass-input" style={{ width: '100%', padding: '10px 16px' }}>
            <option>Aoede (Default)</option>
            <option>Kore</option>
            <option>Fenrir</option>
            <option>Charon</option>
            <option>Puck</option>
          </select>
        </div>
        <div>
          <h4 style={{ fontSize: 16, fontWeight: 500, marginBottom: 4 }}>Voice Sensitivity</h4>
          <input type="range" style={{ width: '100%', accentColor: 'var(--color-accent)' }} />
        </div>
      </div>
    </motion.div>
  );
}
