import React from 'react';
import { motion } from 'framer-motion';
import { Cpu, BookOpen, MonitorPlay, Volume2 } from 'lucide-react';

export default function SystemSkillsWidget({ onSkillTrigger }) {
  const skills = [
    {
      id: 'pc_optimize',
      label: 'Boost PC Performance',
      icon: <Cpu size={20} />,
      color: '#0F52BA',
      description: 'Flush RAM & Temps'
    },
    {
      id: 'study_notes',
      label: 'Generate Study Notes',
      icon: <BookOpen size={20} />,
      color: '#22C55E',
      description: 'Auto-format markdown'
    },
    {
      id: 'ide_launch',
      label: 'Launch Workspace',
      icon: <MonitorPlay size={20} />,
      color: '#A855F7',
      description: 'Open VSCode / WT'
    },
    {
      id: 'media_mute',
      label: 'Toggle System Mute',
      icon: <Volume2 size={20} />,
      color: '#F59E0B',
      description: 'Physical audio control'
    }
  ];

  return (
    <motion.div 
      initial={{ opacity: 0, y: 10 }}
      animate={{ opacity: 1, y: 0 }}
      transition={{ delay: 0.2 }}
      className="glass-panel" 
      style={{ padding: 24, marginTop: 24 }}
    >
      <div style={{ display: 'flex', alignItems: 'center', gap: 10, marginBottom: 16 }}>
        <Cpu size={18} color="var(--color-accent)" />
        <h3 style={{ fontSize: 16, fontWeight: 600, letterSpacing: 0.5, textTransform: 'uppercase' }}>Core OS Automation Skills</h3>
      </div>
      
      <div style={{ display: 'grid', gridTemplateColumns: 'repeat(auto-fit, minmax(200px, 1fr))', gap: 12 }}>
        {skills.map(skill => (
          <motion.button
            key={skill.id}
            whileHover={{ scale: 1.02, y: -2 }}
            whileTap={{ scale: 0.98 }}
            onClick={() => onSkillTrigger(skill.id)}
            className="glass-button"
            style={{
              padding: '16px',
              display: 'flex',
              flexDirection: 'column',
              alignItems: 'flex-start',
              gap: 12,
              border: `1px solid rgba(255,255,255,0.05)`,
              background: 'rgba(0,0,0,0.4)',
              textAlign: 'left'
            }}
          >
            <div style={{ 
              background: `${skill.color}20`, 
              padding: 10, 
              borderRadius: 12,
              color: skill.color
            }}>
              {skill.icon}
            </div>
            <div>
              <div style={{ fontWeight: 600, fontSize: 14, marginBottom: 4 }}>{skill.label}</div>
              <div style={{ fontSize: 12, color: 'var(--color-text-muted)' }}>{skill.description}</div>
            </div>
          </motion.button>
        ))}
      </div>
    </motion.div>
  );
}
