import React from 'react';
import { motion } from 'framer-motion';
import { Video, Edit3, Calendar, Star, Users, Lightbulb } from 'lucide-react';
import { STAGGER, FADE_UP } from '../../../constants';

const stagger = STAGGER;
const fadeUp  = FADE_UP;

const CONTENT_CALENDAR = [
  { day: 'Today',    title: 'Live Reaction Stream',   status: 'scheduled', color: '#22C55E' },
  { day: 'Tomorrow', title: 'Tutorial: Editing Tips', status: 'draft',     color: '#F59E0B' },
  { day: 'Saturday', title: 'Gaming Marathon',         status: 'idea',      color: '#A855F7' },
];

export default function StreamerDashboard({ onAction }) {
  const quickActions = [
    { icon: Lightbulb, label: 'Video Ideas',    desc: 'Trending content concepts', action: 'generate video ideas for me'         },
    { icon: Edit3,     label: 'Write Titles',   desc: 'Click-worthy titles',        action: 'write video titles for me'           },
    { icon: Calendar,  label: 'Build Schedule', desc: 'Weekly content plan',        action: 'create a content schedule'           },
    { icon: Star,      label: 'Trend Analysis', desc: "What's going viral",         action: 'analyze trending topics for my niche'},
  ];

  return (
    <motion.div variants={stagger} initial="hidden" animate="visible" style={{ display: 'flex', flexDirection: 'column', gap: 32 }}>

      {/* Stats Row */}
      <div style={{ display: 'grid', gridTemplateColumns: 'repeat(3, 1fr)', gap: 16 }}>
        {[
          { label: 'Upcoming Streams', value: '2 This Week', icon: Video,     color: '#F59E0B' },
          { label: 'Content Ideas',    value: '14 Saved',    icon: Lightbulb, color: '#A855F7' },
          { label: 'Audience Growth',  value: '+12% ↑',      icon: Users,     color: '#22C55E' },
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

      {/* Content Calendar */}
      <motion.div variants={fadeUp} className="glass-panel" style={{ padding: 24 }}>
        <h3 style={{ fontSize: 15, fontWeight: 600, marginBottom: 16 }}>Content Calendar</h3>
        <div style={{ display: 'flex', flexDirection: 'column', gap: 12 }}>
          {CONTENT_CALENDAR.map((item, i) => (
            <div key={i} style={{ display: 'flex', alignItems: 'center', gap: 14, padding: '10px 12px', background: 'rgba(255,255,255,0.03)', borderRadius: 12, border: '1px solid var(--color-border)' }}>
              <div style={{ width: 8, height: 8, borderRadius: '50%', background: item.color, flexShrink: 0 }} />
              <div style={{ flex: 1 }}>
                <p style={{ fontSize: 14, fontWeight: 500 }}>{item.title}</p>
                <p style={{ fontSize: 12, color: 'var(--color-text-muted)' }}>{item.day}</p>
              </div>
              <span style={{ fontSize: 11, padding: '4px 10px', borderRadius: 10, background: `${item.color}20`, color: item.color, fontWeight: 600, textTransform: 'uppercase', letterSpacing: 0.5 }}>{item.status}</span>
            </div>
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
