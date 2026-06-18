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
      <div className="glass-panel" style={{ display: 'flex', alignItems: 'center', gap: 8, padding: '8px 16px', borderRadius: 20 }}>
        <div style={{ width: 8, height: 8, borderRadius: '50%', background: getAiStateColor(), boxShadow: `0 0 8px ${getAiStateColor()}` }} />
        <span style={{ fontSize: 13, fontWeight: 500 }}>{getAiStateLabel()}</span>
      </div>

      {/* Voice State Pill */}
      <div className="glass-panel" style={{ display: 'flex', alignItems: 'center', gap: 8, padding: '8px 16px', borderRadius: 20 }}>
        <Mic size={14} color="var(--color-text-secondary)" />
        <span style={{ fontSize: 13, fontWeight: 500, color: 'var(--color-text-secondary)' }}>Voice Ready</span>
      </div>

      {/* Connection State Pill */}
      <div className="glass-panel" style={{ display: 'flex', alignItems: 'center', gap: 8, padding: '8px 16px', borderRadius: 20 }}>
        <Wifi size={14} color={isConnected ? 'var(--color-success)' : 'var(--color-danger)'} />
        <span style={{ fontSize: 13, fontWeight: 500, color: isConnected ? 'var(--color-success)' : 'var(--color-danger)' }}>
          {isConnected ? 'Online' : 'Offline'}
        </span>
      </div>

      {/* Time */}
      <div className="glass-panel" style={{ display: 'flex', alignItems: 'center', gap: 8, padding: '8px 16px', borderRadius: 20 }}>
        <Clock size={14} color="var(--color-text-secondary)" />
        <span style={{ fontSize: 13, fontWeight: 500, color: 'var(--color-text-secondary)' }}>{formatTime(time)}</span>
      </div>
    </motion.div>
  );
}
