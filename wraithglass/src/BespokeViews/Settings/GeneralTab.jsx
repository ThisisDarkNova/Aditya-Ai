import React from 'react';
import { motion } from 'framer-motion';
import { STAGGER } from '../../../constants';

const stagger = STAGGER;

export default function GeneralTab({ settings, handleToggle }) {
  return (
    <motion.div variants={stagger} initial="hidden" animate="visible" className="flex flex-col gap-6">
      <h2 style={{ fontSize: 24, fontWeight: 600, marginBottom: 8 }}>General Settings</h2>

      <div className="glass-panel" style={{ padding: 24 }}>
        {/* Language */}
        <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: 20 }}>
          <div>
            <h4 style={{ fontSize: 16, fontWeight: 500 }}>System Language</h4>
            <p style={{ fontSize: 13, color: 'var(--color-text-secondary)' }}>Wraithglass's primary communication language.</p>
          </div>
          <select className="glass-input" style={{ padding: '8px 16px', cursor: 'pointer' }}>
            <option value="en">English (US)</option>
            <option value="uk">English (UK)</option>
            <option value="es">Spanish</option>
            <option value="fr">French</option>
            <option value="jp">Japanese</option>
          </select>
        </div>

        {/* Startup */}
        <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: 20 }}>
          <div>
            <h4 style={{ fontSize: 16, fontWeight: 500 }}>Startup Behavior</h4>
            <p style={{ fontSize: 13, color: 'var(--color-text-secondary)' }}>Launch Wraithglass automatically on boot.</p>
          </div>
          <div
            onClick={() => handleToggle('launch_on_startup')}
            style={{ width: 44, height: 24, background: settings?.launch_on_startup ? 'var(--color-accent)' : 'var(--color-glass)', border: '1px solid var(--color-border)', borderRadius: 12, position: 'relative', cursor: 'pointer', transition: 'background 0.2s' }}
          >
            <div style={{ width: 20, height: 20, background: '#fff', borderRadius: '50%', position: 'absolute', top: 2, left: settings?.launch_on_startup ? 22 : 2, transition: 'left 0.2s' }} />
          </div>
        </div>

        {/* Notifications */}
        <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center' }}>
          <div>
            <h4 style={{ fontSize: 16, fontWeight: 500 }}>Notifications</h4>
            <p style={{ fontSize: 13, color: 'var(--color-text-secondary)' }}>Allow ambient alerts and reminders.</p>
          </div>
          <div
            onClick={() => handleToggle('notifications_enabled')}
            style={{ width: 44, height: 24, background: settings?.notifications_enabled ? 'var(--color-accent)' : 'var(--color-glass)', border: '1px solid var(--color-border)', borderRadius: 12, position: 'relative', cursor: 'pointer', transition: 'background 0.2s' }}
          >
            <div style={{ width: 20, height: 20, background: '#fff', borderRadius: '50%', position: 'absolute', top: 2, left: settings?.notifications_enabled ? 22 : 2, transition: 'left 0.2s' }} />
          </div>
        </div>
      </div>
    </motion.div>
  );
}
