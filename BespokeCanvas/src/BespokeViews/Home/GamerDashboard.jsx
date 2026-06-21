import React from 'react';
import { motion } from 'framer-motion';
import { Gamepad2, Activity, Trophy, Monitor, Cpu, TrendingUp, Target } from 'lucide-react';
import { STAGGER, FADE_UP } from '../../../constants';

const stagger = STAGGER;
const fadeUp  = FADE_UP;

const GAMES = ['Valorant', 'CS2', 'Fortnite', 'Minecraft', 'Roblox', 'GTA V', 'CoD', 'LoL'];

export default function GamerDashboard({ onAction }) {
  const quickActions = [
    { icon: Cpu,      label: 'Compute Reserve',      desc: 'Reallocate Power',   action: 'optimize my PC for gaming'  },
    { icon: Activity, label: 'Analyze Match',     desc: 'Review your gameplay',      action: 'analyze my last match'      },
    { icon: Target,   label: 'Practice Routine',  desc: 'Aim & mechanics drills',    action: 'create a practice routine'  },
    { icon: Gamepad2, label: 'Game Mode',          desc: 'Activate full performance', action: 'activate gaming mode'       },
  ];

  return (
    <motion.div variants={stagger} initial="hidden" animate="visible" style={{ display: 'flex', flexDirection: 'column', gap: 32 }}>

      {/* Stats Row */}
      <div style={{ display: 'grid', gridTemplateColumns: 'repeat(3, 1fr)', gap: 16 }}>
        {[
          { label: 'Current Rank', value: 'Platinum II', icon: Trophy,    color: '#A855F7' },
          { label: 'Avg FPS',      value: '165 FPS',     icon: Monitor,   color: '#22C55E' },
          { label: 'Win Rate',     value: '58%',          icon: TrendingUp,color: '#F59E0B' },
        ].map((stat, i) => (
          <motion.div key={i} variants={fadeUp} className="glass-panel" style={{ padding: 20, display: 'flex', alignItems: 'center', gap: 14 }}>
            <div style={{ width: 44, height: 44, borderRadius: 14, background: `${stat.color}20`, display: 'flex', alignItems: 'center', justifyContent: 'center', flexShrink: 0 }}>
              <stat.icon size={22} color={stat.color} />
            </div>
            <div>
              <p style={{ fontSize: 12, color: 'var(--color-text-muted)', marginBottom: 2, textTransform: 'uppercase', letterSpacing: 1 }}>{stat.label}</p>
              <p style={{ fontSize: 16, fontWeight: 600, color: '#fff' }}>{stat.value}</p>
            </div>
          </motion.div>
        ))}
      </div>

      {/* Game Optimizer */}
      <motion.div variants={fadeUp} className="glass-panel" style={{ padding: 24 }}>
        <h3 style={{ fontSize: 15, fontWeight: 600, marginBottom: 16 }}>Optimize for Game</h3>
        <div style={{ display: 'flex', flexWrap: 'wrap', gap: 10 }}>
          {GAMES.map((g, i) => (
            <button key={i} onClick={() => onAction(`optimize my PC for ${g}`)}
              className="smooth-transition"
              style={{ padding: '8px 16px', borderRadius: 20, background: 'var(--color-glass)', border: '1px solid var(--color-border)', color: 'var(--color-text-secondary)', fontSize: 13, fontWeight: 500, cursor: 'pointer' }}
              onMouseEnter={e => { e.currentTarget.style.background = 'var(--color-accent-glow)'; e.currentTarget.style.color = 'var(--color-accent)'; e.currentTarget.style.borderColor = 'var(--color-accent)'; }}
              onMouseLeave={e => { e.currentTarget.style.background = 'var(--color-glass)'; e.currentTarget.style.color = 'var(--color-text-secondary)'; e.currentTarget.style.borderColor = 'var(--color-border)'; }}
            >{g}</button>
          ))}
        </div>
      </motion.div>

      {/* Quick Actions */}
      <motion.div variants={fadeUp}>
        <h3 style={{ fontSize: 15, fontWeight: 600, marginBottom: 14 }}>Quick Actions</h3>
        <div style={{ display: 'grid', gridTemplateColumns: 'repeat(2, 1fr)', gap: 12 }}>
          {quickActions.map((a, i) => (
            <button key={i} onClick={() => onAction(a.action)} className="glass-button smooth-transition"
              style={{ padding: '18px 16px', justifyContent: 'flex-start', gap: 14, textAlign: 'left' }}>
              <div style={{ width: 36, height: 36, borderRadius: 10, background: 'var(--color-accent-glow)', display: 'flex', alignItems: 'center', justifyContent: 'center', flexShrink: 0 }}>
                <a.icon size={18} color="var(--color-accent)" />
              </div>
              <div>
                <p style={{ fontSize: 14, fontWeight: 600, marginBottom: 2 }}>{a.label}</p>
                <p style={{ fontSize: 12, color: 'var(--color-text-muted)' }}>{a.desc}</p>
              </div>
            </button>
          ))}
        </div>
      </motion.div>

    </motion.div>
  );
}
