import React, { useState } from 'react';
import { motion, AnimatePresence } from 'framer-motion';
import { Target, Sparkles, Mic, ArrowRight } from 'lucide-react';
import StudentDashboard  from './StudentDashboard';
import GamerDashboard    from './GamerDashboard';
import StreamerDashboard from './StreamerDashboard';
import { PERSONAS, STAGGER, FADE_UP, AI_STATE_LABELS, AI_STATE_COLORS } from '../../../constants';
import { getGreeting, formatUptime } from '../../../utils';

const stagger = STAGGER;
const fadeUp  = FADE_UP;

export default function Home({
  status, memory, settings, onChat, chatHistory,
  aiState, setActivePage, isConnected,
  activePersona, setActivePersona,
  realtimeStats = {},
}) {
  const [commandText, setCommandText] = useState('');
  const isListening = aiState === 'listening';

  const username      = memory?.user_profile?.nickname || memory?.user_profile?.name || 'DarkNova';
  const aiStatusLabel = AI_STATE_LABELS[aiState] || `Online · ${status?.message || 'Ready to help'}`;
  const aiStatusColor = AI_STATE_COLORS[aiState]  || '#22C55E';

  const handleCommand = (e) => {
    e.preventDefault();
    if (commandText.trim()) { onChat(commandText); setCommandText(''); }
  };

  const currentFocus = { student: 'Mathematics Revision', gamer: 'Valorant Improvement', streamer: 'YouTube Growth' }[activePersona];
  const dailySummary = {
    student:  'You completed 3 study sessions today. Your Mathematics score improved by 8%. Your next exam is in 12 days — keep it up!',
    gamer:    'You played 4 matches today with a 62% win rate. Your aim accuracy improved by 3%. Keep grinding!',
    streamer: "You generated 5 content ideas today. Your latest video is trending. Tomorrow's stream schedule is ready.",
  }[activePersona];

  return (
    <div className="flex-1 overflow-y-auto" style={{ padding: '32px 40px 160px' }}>
      <motion.div variants={stagger} initial="hidden" animate="visible"
        style={{ maxWidth: 1000, margin: '0 auto', display: 'flex', flexDirection: 'column', gap: 32 }}>

        {/* ── Greeting + AI Status ── */}
        <motion.div variants={fadeUp} style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'flex-start', flexWrap: 'wrap', gap: 16 }}>
          <div>
            <h1 style={{ fontSize: 40, fontWeight: 700, letterSpacing: '-0.04em', marginBottom: 6 }}>
              {getGreeting()}, <span style={{ color: 'var(--color-accent)' }}>{username}</span>
            </h1>
            <p style={{ fontSize: 16, color: 'var(--color-text-secondary)' }}>Ready to continue your journey?</p>
          </div>
          <div className="glass-panel" style={{ padding: '12px 20px', display: 'flex', alignItems: 'center', gap: 10, borderRadius: 16 }}>
            <div style={{ width: 10, height: 10, borderRadius: '50%', background: aiStatusColor, boxShadow: `0 0 8px ${aiStatusColor}` }} />
            <span style={{ fontSize: 14, fontWeight: 500 }}>{aiStatusLabel}</span>
          </div>
        </motion.div>

        {/* ── Persona Switcher ── */}
        <motion.div variants={fadeUp} style={{ display: 'flex', gap: 8 }}>
          <span style={{ fontSize: 13, color: 'var(--color-text-muted)', alignSelf: 'center', marginRight: 8, fontWeight: 500 }}>Mode:</span>
          {PERSONAS.map(p => (
            <motion.button key={p.id} onClick={() => setActivePersona(p.id)} className="smooth-transition"
              whileHover={{ scale: 1.06, borderColor: 'var(--color-accent)' }}
              whileTap={{ scale: 0.95 }}
              style={{
                padding: '8px 20px', borderRadius: 20, cursor: 'pointer',
                fontSize: 13, fontWeight: 600, border: '1px solid',
                background:   activePersona === p.id ? 'var(--color-accent-glow)' : 'transparent',
                color:        activePersona === p.id ? 'var(--color-accent)'      : 'var(--color-text-muted)',
                borderColor:  activePersona === p.id ? 'var(--color-accent)'      : 'var(--color-border)',
              }}>
              {p.emoji} {p.label}
            </motion.button>
          ))}
        </motion.div>

        {/* ── Focus + Daily Summary ── */}
        <div style={{ display: 'grid', gridTemplateColumns: '1fr 1.4fr', gap: 20 }}>
          <motion.div variants={fadeUp} whileHover={{ y: -4, scale: 1.01 }} className="glass-panel" style={{ padding: 24 }}>
            <p style={{ fontSize: 12, color: 'var(--color-text-muted)', textTransform: 'uppercase', letterSpacing: 1, marginBottom: 12, fontWeight: 600 }}>Current Focus</p>
            <div style={{ display: 'flex', alignItems: 'center', gap: 12 }}>
              <div style={{ width: 48, height: 48, borderRadius: 14, background: 'var(--color-accent-glow)', display: 'flex', alignItems: 'center', justifyContent: 'center' }}>
                <Target size={24} color="var(--color-accent)" />
              </div>
              <div>
                <h3 style={{ fontSize: 18, fontWeight: 600 }}>{currentFocus}</h3>
                <p style={{ fontSize: 13, color: 'var(--color-text-secondary)' }}>Active goal</p>
              </div>
            </div>
          </motion.div>
          <motion.div variants={fadeUp} whileHover={{ y: -4, scale: 1.01 }} className="glass-panel" style={{ padding: 24 }}>
            <div style={{ display: 'flex', alignItems: 'center', gap: 10, marginBottom: 12 }}>
              <Sparkles size={16} color="var(--color-accent)" />
              <p style={{ fontSize: 12, color: 'var(--color-text-muted)', textTransform: 'uppercase', letterSpacing: 1, fontWeight: 600 }}>Daily Summary</p>
            </div>
            <p style={{ fontSize: 14, color: 'var(--color-text-secondary)', lineHeight: 1.7 }}>{dailySummary}</p>
          </motion.div>
        </div>

        {/* ── Dynamic Persona Dashboard ── */}
        <AnimatePresence mode="wait">
          <motion.div key={activePersona}
            initial={{ opacity: 0, y: 20 }} animate={{ opacity: 1, y: 0 }} exit={{ opacity: 0, y: -20 }}
            transition={{ duration: 0.35, ease: [0.16, 1, 0.3, 1] }}>
            {activePersona === 'student'  && <StudentDashboard  onAction={onChat} goals={memory?.goals || []} />}
            {activePersona === 'gamer'    && <GamerDashboard    onAction={onChat} />}
            {activePersona === 'streamer' && <StreamerDashboard onAction={onChat} />}
          </motion.div>
        </AnimatePresence>

      </motion.div>

      {/* ── Live Stats Widget ── */}
      <motion.div variants={fadeUp} style={{ maxWidth: 1000, margin: '32px auto 0', display: 'grid', gridTemplateColumns: 'repeat(3, 1fr)', gap: 12 }}>
        {[
          { label: 'Uptime',          value: formatUptime(realtimeStats?.uptime_seconds),                                                                  color: '#22C55E' },
          { label: 'Cache Hit Rate',  value: realtimeStats?.cache?.hit_rate_pct != null ? `${Math.round(realtimeStats.cache.hit_rate_pct)}%` : '—',        color: '#3B82F6' },
          { label: 'API Calls Saved', value: realtimeStats?.api_calls_saved != null ? String(realtimeStats.api_calls_saved) : '—',                          color: '#A855F7' },
        ].map((s, i) => (
          <motion.div key={i} whileHover={{ y: -3, scale: 1.02 }} className="glass-panel" style={{ padding: '14px 18px', display: 'flex', flexDirection: 'column', gap: 4 }}>
            <p style={{ fontSize: 11, color: 'var(--color-text-muted)', textTransform: 'uppercase', letterSpacing: 1, fontWeight: 600 }}>{s.label}</p>
            <p style={{ fontSize: 22, fontWeight: 700, color: s.color }}>{s.value}</p>
          </motion.div>
        ))}
      </motion.div>

      {/* ── Floating Command Bar ── */}
      <motion.div
        initial={{ y: 60, opacity: 0 }} animate={{ y: 0, opacity: 1 }}
        transition={{ delay: 0.5, type: 'spring', stiffness: 200, damping: 22 }}
        style={{ position: 'fixed', bottom: 40, left: '50%', transform: 'translateX(-50%)', width: '65%', maxWidth: 720, zIndex: 40 }}
      >
        <div style={{ textAlign: 'center', marginBottom: 8 }}>
          <span style={{ fontSize: 11, color: 'rgba(255,255,255,0.2)', letterSpacing: '0.08em', fontWeight: 500 }}>
            Press <kbd style={{ background: 'rgba(255,255,255,0.08)', border: '1px solid rgba(255,255,255,0.12)', borderRadius: 5, padding: '1px 6px', fontSize: 10, fontFamily: 'monospace' }}>Ctrl+Alt+J</kbd> to wake ADITYA
          </span>
        </div>
        <form onSubmit={handleCommand} className="glass-panel"
          style={{ display: 'flex', alignItems: 'center', padding: '10px 20px', borderRadius: 28, background: 'rgba(17,19,26,0.85)', backdropFilter: 'blur(24px)' }}>
          <motion.div
            animate={isListening ? { scale: [1, 1.3, 1], opacity: [1, 0.7, 1] } : { scale: 1, opacity: 1 }}
            transition={isListening ? { duration: 1, repeat: Infinity, ease: 'easeInOut' } : {}}
            style={{ marginRight: 12, flexShrink: 0, display: 'flex', alignItems: 'center', justifyContent: 'center',
              filter: isListening ? 'drop-shadow(0 0 6px var(--color-accent))' : 'none' }}>
            <Mic size={18} color={isListening ? 'var(--color-accent)' : 'var(--color-text-muted)'} />
          </motion.div>
          <input type="text"
            placeholder={isListening ? 'Listening...' : 'Ask Aditya anything...'}
            value={commandText} onChange={e => setCommandText(e.target.value)}
            style={{ flex: 1, background: 'transparent', border: 'none', color: '#fff', fontSize: 15, padding: '10px 0', outline: 'none' }}
          />
          <button type="submit" style={{ background: 'var(--color-accent)', border: 'none', borderRadius: '50%', width: 38, height: 38, display: 'flex', alignItems: 'center', justifyContent: 'center', cursor: 'pointer', flexShrink: 0, boxShadow: '0 4px 14px var(--color-accent-glow)' }}>
            <ArrowRight size={18} color="#fff" />
          </button>
        </form>
      </motion.div>
    </div>
  );
}
