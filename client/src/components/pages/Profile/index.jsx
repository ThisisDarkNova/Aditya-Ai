import React from 'react';
import { motion } from 'framer-motion';
import {
  BookOpen, Gamepad2, Video, Trophy, Star, Zap,
  Target, Brain, TrendingUp, Clock, Heart, Flame
} from 'lucide-react';

const stagger = { hidden: {}, visible: { transition: { staggerChildren: 0.07 } } };
const fadeUp = { hidden: { opacity: 0, y: 20 }, visible: { opacity: 1, y: 0, transition: { duration: 0.45, ease: [0.16, 1, 0.3, 1] } } };

function ProgressBar({ value, color = 'var(--color-accent)' }) {
  return (
    <div style={{ height: 6, background: 'rgba(255,255,255,0.08)', borderRadius: 3, overflow: 'hidden' }}>
      <motion.div
        initial={{ width: 0 }}
        animate={{ width: `${value}%` }}
        transition={{ duration: 1.2, ease: [0.16, 1, 0.3, 1] }}
        style={{ height: '100%', background: color, borderRadius: 3 }}
      />
    </div>
  );
}

export default function Profile({ memory, saveAdityaMemoryEngine, chatHistory = [], realtimeStats = {} }) {
  const profile = memory?.user_profile || {};
  const username = profile.nickname || profile.name || 'DarkNova';
  const initial = username.charAt(0).toUpperCase();

  const totalInteractions = chatHistory.length || 24;
  const uptimeSecs = realtimeStats?.uptime_seconds ?? 3600;
  const hoursWithAditya = `${Math.max(1, Math.round(uptimeSecs / 3600))}h`;
  const goalsCount = memory?.goals?.length ?? 6;
  const relationshipAge = '2d';

  const achievements = [
    { icon: Flame, label: 'Valorant Streamer', desc: 'Active YouTube gaming streams', color: '#F59E0B' },
    { icon: Star, label: 'DPL Organizer', desc: 'Dominastra Premier League head', color: '#A855F7' },
    { icon: Zap, label: 'Virtech Founder', desc: 'Virtech Global concept lead', color: '#3B82F6' },
    { icon: Trophy, label: 'Class 10 HBSE', desc: 'Science & Math scholar target', color: '#22C55E' },
    { icon: Target, label: 'Pro Cricketer Goal', desc: '#1 primary career ambition', color: '#EF4444' },
    { icon: Heart, label: 'AI Partner', desc: 'Deep conversation connection', color: '#EC4899' },
  ];

  const personaProgress = [
    { label: 'Cricket & Athletic Training', icon: Target, pct: 85, color: '#3B82F6' },
    { label: 'Gaming Performance (Valorant)', icon: Gamepad2, pct: 95, color: '#A855F7' },
    { label: 'Python & Web Development', icon: Brain, pct: 35, color: '#F59E0B' },
  ];

  const interests = [
    'Valorant', 'Cricket', 'Virtech Global', 'Dominastra', 'DPL', 'Python Coding', 'YouTube Streaming'
  ];

  const stats = [
    { label: 'Total Interactions', value: String(totalInteractions), icon: Brain, color: '#5B8CFF' },
    { label: 'Hours with Aditya', value: hoursWithAditya, icon: Clock, color: '#22C55E' },
    { label: 'Goals Tracked', value: String(goalsCount), icon: Target, color: '#F59E0B' },
    { label: 'Relationship Age', value: relationshipAge, icon: Heart, color: '#EC4899' },
  ];

  return (
    <div className="flex-1 overflow-y-auto" style={{ padding: '40px 40px 120px' }}>
      <motion.div variants={stagger} initial="hidden" animate="visible"
        style={{ maxWidth: 1000, margin: '0 auto', display: 'flex', flexDirection: 'column', gap: 32 }}>

        <motion.div variants={fadeUp} className="glass-panel"
          style={{ padding: 40, position: 'relative', overflow: 'hidden' }}>

          <div style={{
            position: 'absolute', top: -60, left: -60,
            width: 220, height: 220,
            background: 'var(--color-accent-glow)',
            borderRadius: '50%', filter: 'blur(80px)',
            pointerEvents: 'none'
          }} />

          <div style={{
            position: 'absolute', top: 0, left: 0, right: 0, height: '2px',
            background: 'linear-gradient(90deg, transparent, var(--color-accent), transparent)',
            opacity: 0.8
          }} />

          <div style={{ display: 'flex', alignItems: 'center', gap: 32, position: 'relative' }}>
            <motion.div
              whileHover={{ scale: 1.05, rotate: 5 }}
              style={{
                width: 100, height: 100, borderRadius: '50%',
                background: 'linear-gradient(135deg, var(--color-accent), #8B5CF6)',
                display: 'flex', alignItems: 'center', justifyContent: 'center',
                boxShadow: '0 8px 32px var(--color-accent-glow)',
                flexShrink: 0, cursor: 'default'
              }}
            >
              <span style={{ fontSize: 42, fontWeight: 700, color: '#fff', textShadow: '0 2px 10px rgba(0,0,0,0.3)' }}>{initial}</span>
            </motion.div>

            <div style={{ flex: 1 }}>
              <h1 style={{ fontSize: 30, fontWeight: 700, marginBottom: 4, letterSpacing: '-0.5px' }}>{username}</h1>
              <p style={{ fontSize: 15, color: 'var(--color-text-secondary)', marginBottom: 20 }}>
                AI Companion · Active Partner
              </p>
              <div style={{ display: 'flex', flexWrap: 'wrap', gap: 10 }}>
                {interests.map((tag, i) => (
                  <motion.span 
                    key={i} 
                    whileHover={{ scale: 1.05, borderColor: 'var(--color-accent)' }}
                    style={{
                      padding: '5px 14px', borderRadius: 20,
                      background: 'var(--color-glass)',
                      border: '1px solid var(--color-border)',
                      fontSize: 12, fontWeight: 500, color: 'var(--color-text-secondary)',
                      cursor: 'default',
                      transition: 'border-color 0.2s'
                    }}
                  >{tag}</motion.span>
                ))}
              </div>
            </div>
          </div>
        </motion.div>

        <div style={{ display: 'grid', gridTemplateColumns: 'repeat(4, 1fr)', gap: 16 }}>
          {stats.map((s, i) => (
            <motion.div key={i} variants={fadeUp} className="glass-panel"
              style={{ padding: 20, display: 'flex', flexDirection: 'column', gap: 12 }}>
              <div style={{
                width: 40, height: 40, borderRadius: 12,
                background: `${s.color}20`,
                display: 'flex', alignItems: 'center', justifyContent: 'center'
              }}>
                <s.icon size={20} color={s.color} />
              </div>
              <div>
                <p style={{ fontSize: 22, fontWeight: 700, color: '#fff' }}>{s.value}</p>
                <p style={{ fontSize: 12, color: 'var(--color-text-muted)', marginTop: 2 }}>{s.label}</p>
              </div>
            </motion.div>
          ))}
        </div>

        <motion.div variants={fadeUp} className="glass-panel" style={{ padding: 28 }}>
          <div style={{ display: 'flex', alignItems: 'center', gap: 10, marginBottom: 24 }}>
            <TrendingUp size={18} color="var(--color-accent)" />
            <h3 style={{ fontSize: 17, fontWeight: 600 }}>Your Journey Progress</h3>
          </div>
          <div style={{ display: 'flex', flexDirection: 'column', gap: 22 }}>
            {personaProgress.map((item, i) => (
              <div key={i}>
                <div style={{ display: 'flex', alignItems: 'center', justifycontent: 'space-between', marginBottom: 10 }}>
                  <div style={{ display: 'flex', alignItems: 'center', gap: 10 }}>
                    <div style={{ width: 32, height: 32, borderRadius: 10, background: `${item.color}20`, display: 'flex', alignItems: 'center', justifyContent: 'center' }}>
                      <item.icon size={16} color={item.color} />
                    </div>
                    <span style={{ fontSize: 14, fontWeight: 500 }}>{item.label}</span>
                  </div>
                  <span style={{ fontSize: 14, fontWeight: 700, color: item.color }}>{item.pct}%</span>
                </div>
                <ProgressBar value={item.pct} color={item.color} />
              </div>
            ))}
          </div>
        </motion.div>

        <motion.div variants={fadeUp}>
          <h3 style={{ fontSize: 17, fontWeight: 600, marginBottom: 16 }}>Achievements</h3>
          <div style={{ display: 'grid', gridTemplateColumns: 'repeat(3, 1fr)', gap: 14 }}>
            {achievements.map((ach, i) => (
              <motion.div key={i} variants={fadeUp} className="glass-panel"
                style={{ padding: 20, display: 'flex', alignItems: 'flex-start', gap: 14 }}
                whileHover={{ scale: 1.02 }}
                transition={{ type: 'spring', stiffness: 300, damping: 20 }}
              >
                <div style={{
                  width: 44, height: 44, borderRadius: 14, flexShrink: 0,
                  background: `${ach.color}20`,
                  border: `1px solid ${ach.color}40`,
                  display: 'flex', alignItems: 'center', justifyContent: 'center'
                }}>
                  <ach.icon size={22} color={ach.color} />
                </div>
                <div>
                  <p style={{ fontSize: 14, fontWeight: 600, marginBottom: 3 }}>{ach.label}</p>
                  <p style={{ fontSize: 12, color: 'var(--color-text-muted)', lineHeight: 1.4 }}>{ach.desc}</p>
                </div>
              </motion.div>
            ))}
          </div>
        </motion.div>

      </motion.div>
    </div>
  );
}
