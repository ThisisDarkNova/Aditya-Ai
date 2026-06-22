import React from 'react';
import { motion } from 'framer-motion';
import { BookOpen, Edit3, Target, Zap, Clock, CheckCircle, Brain } from 'lucide-react';
import { STAGGER, FADE_UP } from '../../../constants';
import { extractGoalText } from '../../../utils';

const stagger = STAGGER;
const fadeUp = FADE_UP;

export default function StudentDashboard({ onAction, goals = [] }) {
  const quickActions = [
    { icon: BookOpen, label: 'Generate Notes', desc: 'From any topic or chapter', action: 'generate notes for me' },
    { icon: Edit3,    label: 'Create Quiz',    desc: 'Test your knowledge',       action: 'create a quiz for me' },
    { icon: Brain,    label: 'Explain Concept',desc: 'Visual explanations',       action: 'explain a concept for me' },
    { icon: Target,   label: 'Revision Planner',desc:'Build a study plan',        action: 'create a revision plan' },
  ];

  const reminders = goals.length > 0
    ? goals.slice(0, 4).map(g => ({
        text: extractGoalText(g),
        done: g.done ?? g.completed ?? false,
        priority: g.priority || 'normal',
      }))
    : [
        { text: 'Submit Math assignment by 5 PM',  done: false, priority: 'high'   },
        { text: 'Read Chapter 4 of Physics',        done: true,  priority: 'normal' },
        { text: 'Watch CS lecture recording',       done: false, priority: 'normal' },
        { text: 'Revise Trigonometry formulas',     done: false, priority: 'low'    },
      ];

  return (
    <motion.div variants={stagger} initial="hidden" animate="visible" style={{ display: 'flex', flexDirection: 'column', gap: 32 }}>

      {/* Stats Row */}
      <div style={{ display: 'grid', gridTemplateColumns: 'repeat(3, 1fr)', gap: 16 }}>
        {[
          { label: 'Study Streak',    value: '7 days 🔥',     icon: Zap,         color: '#3B82F6' },
          { label: 'Sessions Today',  value: '3 completed',    icon: CheckCircle, color: '#22C55E' },
          { label: 'Next Exam',       value: '12 days',        icon: Clock,       color: '#F59E0B' },
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

      {/* WraithglassKnowledge Progress */}
      <motion.div variants={fadeUp} className="glass-panel" style={{ padding: 24 }}>
        <h3 style={{ fontSize: 15, fontWeight: 600, marginBottom: 20 }}>WraithglassKnowledge Progress</h3>
        <div style={{ display: 'flex', flexDirection: 'column', gap: 14 }}>
          {[
            { subject: 'Mathematics',      pct: 82 },
            { subject: 'Physics',          pct: 65 },
            { subject: 'Computer Science', pct: 91 },
          ].map((s, i) => (
            <div key={i}>
              <div style={{ display: 'flex', justifyContent: 'space-between', marginBottom: 6 }}>
                <span style={{ fontSize: 13, color: 'var(--color-text-secondary)' }}>{s.subject}</span>
                <span style={{ fontSize: 13, color: 'var(--color-accent)', fontWeight: 600 }}>{s.pct}%</span>
              </div>
              <div style={{ height: 6, background: 'rgba(255,255,255,0.08)', borderRadius: 3, overflow: 'hidden' }}>
                <motion.div
                  initial={{ width: 0 }}
                  animate={{ width: `${s.pct}%` }}
                  transition={{ duration: 1, delay: i * 0.15, ease: [0.16, 1, 0.3, 1] }}
                  style={{ height: '100%', background: 'var(--color-accent)', borderRadius: 3 }}
                />
              </div>
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

      {/* Reminders / Goals */}
      <motion.div variants={fadeUp} className="glass-panel" style={{ padding: 24 }}>
        <div style={{ display: 'flex', alignItems: 'center', justifyContent: 'space-between', marginBottom: 16 }}>
          <div style={{ display: 'flex', alignItems: 'center', gap: 10 }}>
            <Clock size={16} color="var(--color-accent)" />
            <h3 style={{ fontSize: 15, fontWeight: 600 }}>{goals.length > 0 ? 'Active Goals' : 'Reminders'}</h3>
          </div>
          <span style={{ fontSize: 11, color: 'var(--color-text-muted)', background: 'var(--color-glass)', padding: '3px 10px', borderRadius: 20, border: '1px solid var(--color-border)' }}>
            {reminders.filter(r => !r.done).length} pending
          </span>
        </div>
        <div style={{ display: 'flex', flexDirection: 'column', gap: 10 }}>
          {reminders.map((r, i) => {
            const priorityColor = { high: '#EF4444', normal: 'var(--color-accent)', low: 'var(--color-text-muted)' }[r.priority] || 'var(--color-accent)';
            return (
              <motion.div key={i} initial={{ opacity: 0, x: -10 }} animate={{ opacity: 1, x: 0 }} transition={{ delay: i * 0.06 }}
                style={{ display: 'flex', alignItems: 'center', gap: 12, padding: '10px 14px', borderRadius: 12,
                  background: r.done ? 'rgba(255,255,255,0.03)' : 'var(--color-glass)',
                  border: '1px solid var(--color-border)', opacity: r.done ? 0.5 : 1 }}>
                <div style={{ width: 8, height: 8, borderRadius: '50%', background: r.done ? 'var(--color-text-muted)' : priorityColor, flexShrink: 0, boxShadow: r.done ? 'none' : `0 0 6px ${priorityColor}80` }} />
                <span style={{ flex: 1, fontSize: 13, color: r.done ? 'var(--color-text-muted)' : 'var(--color-text-secondary)', textDecoration: r.done ? 'line-through' : 'none' }}>
                  {r.text}
                </span>
                {r.done && <CheckCircle size={14} color="var(--color-success)" />}
              </motion.div>
            );
          })}
        </div>
      </motion.div>

    </motion.div>
  );
}
