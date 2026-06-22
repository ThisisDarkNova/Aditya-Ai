import React from 'react';
import { motion } from 'framer-motion';
import { HardDrive, Download, Upload, Trash2 } from 'lucide-react';
import { STAGGER } from '../../../constants';

const stagger = STAGGER;

export default function WraithglassMemoryEngineTab() {
  return (
    <motion.div variants={stagger} initial="hidden" animate="visible" className="flex flex-col gap-6">
      <h2 style={{ fontSize: 24, fontWeight: 600, marginBottom: 8 }}>WraithglassMemoryEngine Management</h2>
      <div className="glass-panel" style={{ padding: 24, display: 'flex', flexDirection: 'column', gap: 16 }}>
        <div style={{ display: 'flex', alignItems: 'center', justifyContent: 'space-between', paddingBottom: 16, borderBottom: '1px solid var(--color-border)' }}>
          <div style={{ display: 'flex', alignItems: 'center', gap: 12 }}>
            <HardDrive size={20} color="var(--color-accent)" />
            <div>
              <h4 style={{ fontSize: 15, fontWeight: 500 }}>Local Storage Usage</h4>
              <p style={{ fontSize: 12, color: 'var(--color-text-secondary)' }}>24.5 MB used</p>
            </div>
          </div>
        </div>
        <div style={{ display: 'flex', gap: 12 }}>
          <button className="glass-button" style={{ flex: 1, padding: '12px 0', gap: 8 }}><Download size={16} /> Export</button>
          <button className="glass-button" style={{ flex: 1, padding: '12px 0', gap: 8 }}><Upload size={16} /> Import</button>
          <button className="glass-button" style={{ flex: 1, padding: '12px 0', gap: 8, color: 'var(--color-danger)' }}><Trash2 size={16} /> Wipe</button>
        </div>
      </div>
    </motion.div>
  );
}
