// ─── constants/index.js ───────────────────────────────────────────────────
// Single source of truth for all shared app constants.

// Navigation items used by Sidebar
export const NAV_ITEMS = [
  { id: 'Home',     label: 'Home' },
  { id: 'Profile',  label: 'Profile' },
  { id: 'Chat',     label: 'Chat' },
  { id: 'Settings', label: 'Settings' },
];

// Persona definitions used by Home, Settings, App
export const PERSONAS = [
  { id: 'student',  label: 'Student',  emoji: '📚', desc: 'Focus & Study',       accent: '#3B82F6', bg: '#060b19' },
  { id: 'gamer',    label: 'Gamer',    emoji: '🎮', desc: 'Performance Mode',    accent: '#A855F7', bg: '#0a0514' },
  { id: 'streamer', label: 'Streamer', emoji: '🎥', desc: 'Content Creator',     accent: '#F59E0B', bg: '#140d04' },
];

// AI state labels shown in status bar and home HUD
export const AI_STATE_LABELS = {
  listening:   'Listening · Voice Active',
  speaking:    'Speaking · Aditya is talking',
  thinking:    'Thinking · Processing request',
  researching: 'Researching · Gathering info',
  offline:     'Offline · Core disconnected',
};

// AI state accent colors
export const AI_STATE_COLORS = {
  listening:   '#3B82F6',
  speaking:    '#22C55E',
  thinking:    '#8B5CF6',
  researching: '#F59E0B',
  offline:     '#6B7280',
};

// Shared framer-motion variants
export const STAGGER = { hidden: {}, visible: { transition: { staggerChildren: 0.07 } } };
export const FADE_UP = { hidden: { opacity: 0, y: 20 }, visible: { opacity: 1, y: 0, transition: { duration: 0.4, ease: [0.16, 1, 0.3, 1] } } };
export const FADE_IN = { hidden: { opacity: 0 }, visible: { opacity: 1, transition: { duration: 0.3 } } };
