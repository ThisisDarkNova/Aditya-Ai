import React, { useState, useEffect } from 'react';
import { Wifi, Mic, Clock } from 'lucide-react';
import { motion } from 'framer-motion';

export default function StatusBar({ isConnected, aiState }) {
  const [time, setTime] = useState(new Date());

  useEffect(() => {
    const timer = setInterval(() => setTime(new Date()), 1000);
    return () => clearInterval(timer);
  }, []);

  const formatTime = (date) => {
    return date.toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' });
  };

  const getAiStateLabel = () => {
    switch(aiState) {
      case 'listening': return 'Listening';
      case 'thinking': return 'Thinking';
      case 'speaking': return 'Speaking';
      case 'tool': return 'Working';
      case 'offline': return 'Offline';
      default: return 'Ready';
    }
  };

  const getAiStateColor = () => {
    switch(aiState) {
      case 'listening': return 'var(--color-danger)';
      case 'thinking': return 'var(--color-warning)';
      case 'speaking': return 'var(--color-accent)';
      case 'offline': return 'var(--color-text-muted)';
      default: return 'var(--color-success)';
    }
  };

  return (
    <motion.div 
      initial={{ opacity: 0, y: -20 }}
      animate={{ opacity: 1, y: 0 }}
      transition={{ duration: 0.5 }}
      style={{
        position: 'absolute',
        top: 24,
        right: 40,
        display: 'flex',
        alignItems: 'center',
        gap: 16,
        zIndex: 50,
      }}
    >
      {/* AI State Pill */}
      <motion.div 
        whileHover={{ scale: 1.05, borderColor: getAiStateColor(), boxShadow: `0 0 15px ${getAiStateColor()}22` }}
        className="glass-panel" 
        style={{ display: 'flex', alignItems: 'center', gap: 8, padding: '8px 16px', borderRadius: 20, cursor: 'default' }}
      >
        <div style={{ position: 'relative', width: 8, height: 8, display: 'flex', alignItems: 'center', justifyContent: 'center' }}>
          {/* Pulsing glow ring */}
          <motion.div
            animate={{ scale: [1, 2.4, 1], opacity: [0.6, 0, 0.6] }}
            transition={{ duration: 2, repeat: Infinity, ease: 'easeInOut' }}
            style={{
              position: 'absolute',
              width: 8,
              height: 8,
              borderRadius: '50%',
              background: getAiStateColor(),
              boxShadow: `0 0 6px ${getAiStateColor()}`,
            }}
          />
          {/* Core dot */}
          <div style={{ width: 6, height: 6, borderRadius: '50%', background: getAiStateColor(), zIndex: 2 }} />
        </div>
        <span style={{ fontSize: 13, fontWeight: 500 }}>{getAiStateLabel()}</span>
      </motion.div>

      {/* Voice State Pill */}
      <motion.div 
        whileHover={{ scale: 1.05, borderColor: 'var(--color-accent)', boxShadow: '0 0 15px var(--color-accent-glow)' }}
        className="glass-panel" 
        style={{ display: 'flex', alignItems: 'center', gap: 8, padding: '8px 16px', borderRadius: 20, cursor: 'default' }}
      >
        <Mic size={14} color="var(--color-text-secondary)" />
        <span style={{ fontSize: 13, fontWeight: 500, color: 'var(--color-text-secondary)' }}>Voice Ready</span>
      </motion.div>

      {/* Connection State Pill */}
      <motion.div 
        whileHover={{ scale: 1.05, borderColor: isConnected ? 'var(--color-success)' : 'var(--color-danger)', boxShadow: `0 0 15px ${isConnected ? 'var(--color-success)' : 'var(--color-danger)'}22` }}
        className="glass-panel" 
        style={{ display: 'flex', alignItems: 'center', gap: 8, padding: '8px 16px', borderRadius: 20, cursor: 'default' }}
      >
        <Wifi size={14} color={isConnected ? 'var(--color-success)' : 'var(--color-danger)'} />
        <span style={{ fontSize: 13, fontWeight: 500, color: isConnected ? 'var(--color-success)' : 'var(--color-danger)' }}>
          {isConnected ? 'Online' : 'Offline'}
        </span>
      </motion.div>

      {/* Time */}
      <motion.div 
        whileHover={{ scale: 1.05, borderColor: 'rgba(255, 255, 255, 0.2)' }}
        className="glass-panel" 
        style={{ display: 'flex', alignItems: 'center', gap: 8, padding: '8px 16px', borderRadius: 20, cursor: 'default' }}
      >
        <Clock size={14} color="var(--color-text-secondary)" />
        <span style={{ fontSize: 13, fontWeight: 500, color: 'var(--color-text-secondary)' }}>{formatTime(time)}</span>
      </motion.div>
    </motion.div>
  );
}
