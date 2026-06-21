import React from 'react';
import { motion } from 'framer-motion';
import { Cpu, BookOpen, MonitorPlay, Volume2 } from 'lucide-react';
import { useMagneticHover } from '../../../CoreMotion/useMagneticHover';

function MagneticSkillButton({ skill, onSkillTrigger }) {
  const { ref, x, y, handleMouseMove, handleMouseLeave } = useMagneticHover(0.15);

  return (
    <motion.button
      ref={ref}
      onMouseMove={handleMouseMove}
      onMouseLeave={handleMouseLeave}
      whileHover={{ scale: 1.05 }}
      whileTap={{ scale: 0.98 }}
      onClick={() => onSkillTrigger(skill.id)}
      className="glass-button"
      style={{
        x,
        y,
        padding: '24px',
        display: 'flex',
        flexDirection: 'column',
        alignItems: 'flex-start',
        gap: 16,
        border: `1px solid rgba(255,255,255,0.05)`,
        background: 'rgba(0,0,0,0.4)',
        textAlign: 'left',
        // Critical for the 3D physics feel
        transformStyle: 'preserve-3d',
        perspective: 1000
      }}
    >
      <div style={{ 
        background: `${skill.color}15`, 
        padding: 14, 
        borderRadius: 16,
        color: skill.color
      }}>
        {skill.icon}
      </div>
      <div>
        <div style={{ fontFamily: 'var(--font-serif)', fontWeight: 600, fontSize: 18, marginBottom: 6 }}>{skill.label}</div>
        <div style={{ fontSize: 13, color: 'var(--color-text-muted)', fontWeight: 300 }}>{skill.description}</div>
      </div>
    </motion.button>
  );
}

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
      initial={{ opacity: 0, y: 20 }}
      animate={{ opacity: 1, y: 0 }}
      transition={{ delay: 0.3, duration: 0.8, ease: [0.16, 1, 0.3, 1] }}
      className="glass-panel" 
      style={{ padding: 48, marginTop: 16 }}
    >
      <div style={{ display: 'flex', alignItems: 'center', gap: 16, marginBottom: 32 }}>
        <Cpu size={24} color="var(--color-accent)" />
        <h3 style={{ fontFamily: 'var(--font-serif)', fontSize: 24, fontWeight: 400, letterSpacing: '0.02em' }}>Core OS Automation</h3>
      </div>
      
      <div style={{ display: 'grid', gridTemplateColumns: 'repeat(auto-fit, minmax(240px, 1fr))', gap: 24 }}>
        {skills.map(skill => (
          <MagneticSkillButton key={skill.id} skill={skill} onSkillTrigger={onSkillTrigger} />
        ))}
      </div>
    </motion.div>
  );
}
