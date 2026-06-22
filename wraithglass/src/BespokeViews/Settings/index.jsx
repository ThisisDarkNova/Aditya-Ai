import React, { useState } from 'react';
import { motion, AnimatePresence } from 'framer-motion';
import { 
  Settings as SettingsIcon, Mic, Palette, Brain, 
  Shield, Code, Info
} from 'lucide-react';

import GeneralTab from './GeneralTab';
import AppearanceTab from './AppearanceTab';
import VoiceTab from './VoiceTab';
import WraithglassMemoryEngineTab from './WraithglassMemoryEngineTab';

const stagger = { hidden: {}, visible: { transition: { staggerChildren: 0.05 } } };

function ActivityIcon(props) {
  return <svg {...props} xmlns="http://www.w3.org/2000/svg" width="24" height="24" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round"><polyline points="22 12 18 12 15 21 9 3 6 12 2 12"></polyline></svg>;
}

export default function Settings({ settings, saveSettings, setActivePage, activePersona, onSelectPersona }) {
  const [activeTab, setActiveTab] = useState('General');
  const [debugMode, setDebugMode] = useState(false);

  const tabs = [
    { id: 'General', icon: SettingsIcon },
    { id: 'Voice', icon: Mic },
    { id: 'Appearance', icon: Palette },
    { id: 'WraithglassMemoryEngine', icon: Brain },
    { id: 'AI Behavior', icon: ActivityIcon },
    { id: 'Privacy', icon: Shield },
    ...(debugMode ? [{ id: 'Developer', icon: Code }] : []),
    { id: 'About', icon: Info },
  ];

  const handleToggle = (key) => {
    if (!settings || !saveSettings) return;
    saveSettings({ ...settings, [key]: !settings[key] });
  };

  const handleSelect = (key, value) => {
    if (!settings || !saveSettings) return;
    saveSettings({ ...settings, [key]: value });
  };

  const renderContent = () => {
    switch(activeTab) {
      case 'General':
        return <GeneralTab settings={settings} handleToggle={handleToggle} />;
      
      case 'Appearance':
        return <AppearanceTab activePersona={activePersona} onSelectPersona={onSelectPersona} />;

      case 'Voice':
        return <VoiceTab />;

      case 'WraithglassMemoryEngine':
        return <WraithglassMemoryEngineTab />;

      case 'About':
        return (
          <motion.div variants={stagger} initial="hidden" animate="visible" className="flex flex-col gap-6">
            <h2 style={{ fontSize: 24, fontWeight: 600, marginBottom: 8 }}>About Wraithglass</h2>
            <div className="glass-panel" style={{ padding: 32, textAlign: 'center' }}>
              <div style={{ width: 64, height: 64, background: 'var(--color-accent)', borderRadius: 20, margin: '0 auto 16px', display: 'flex', alignItems: 'center', justifyContent: 'center', boxShadow: '0 8px 32px var(--color-accent-glow)' }}>
                <span style={{ color: '#fff', fontSize: 24, fontWeight: 700 }}>Ae</span>
              </div>
              <h3 style={{ fontSize: 20, fontWeight: 600 }}>VESPERA OS</h3>
              <p style={{ color: 'var(--color-text-secondary)', cursor: 'pointer' }} onClick={() => setDebugMode(true)}>Version 1.0.0 (Build 2026.04)</p>
              
              <div style={{ marginTop: 32, paddingTop: 32, borderTop: '1px solid var(--color-border)', display: 'grid', gridTemplateColumns: '1fr 1fr', gap: 16 }}>
                <div>
                  <p style={{ fontSize: 12, color: 'var(--color-text-muted)', textTransform: 'uppercase' }}>Backend</p>
                  <p style={{ fontSize: 14, fontWeight: 500 }}>Gemini Core (Active)</p>
                </div>
                <div>
                  <p style={{ fontSize: 12, color: 'var(--color-text-muted)', textTransform: 'uppercase' }}>Updates</p>
                  <p style={{ fontSize: 14, fontWeight: 500, color: 'var(--color-success)' }}>Up to date</p>
                </div>
              </div>
            </div>
          </motion.div>
        );

      default:
        return <div style={{ color: 'var(--color-text-muted)' }}>Panel under construction in new UI.</div>;
    }
  };

  return (
    <div className="flex-1 overflow-hidden" style={{ padding: '40px', display: 'flex', justifyContent: 'center' }}>
      <div className="glass-panel" style={{ width: '100%', maxWidth: 1000, height: '100%', display: 'flex', overflow: 'hidden' }}>
        
        <div style={{ width: 260, borderRight: '1px solid var(--color-border)', background: 'rgba(0,0,0,0.2)', padding: 24, display: 'flex', flexDirection: 'column', gap: 8, overflowY: 'auto' }}>
          <h3 style={{ fontSize: 13, color: 'var(--color-text-muted)', textTransform: 'uppercase', letterSpacing: 1, fontWeight: 600, marginBottom: 12, paddingLeft: 12 }}>Settings</h3>
          
          {tabs.map((tab) => (
            <button
              key={tab.id}
              onClick={() => setActiveTab(tab.id)}
              className="smooth-transition"
              style={{
                display: 'flex', alignItems: 'center', gap: 12,
                width: '100%', padding: '12px 16px',
                borderRadius: 12, border: 'none', cursor: 'pointer',
                background: activeTab === tab.id ? 'var(--color-glass)' : 'transparent',
                color: activeTab === tab.id ? 'var(--color-text-primary)' : 'var(--color-text-secondary)',
                textAlign: 'left'
              }}
            >
              <tab.icon size={18} />
              <span style={{ fontSize: 14, fontWeight: 500 }}>{tab.id}</span>
            </button>
          ))}
        </div>

        <div style={{ flex: 1, padding: 40, overflowY: 'auto' }}>
          <AnimatePresence mode="wait">
            <motion.div
              key={activeTab}
              initial={{ opacity: 0, x: 10 }}
              animate={{ opacity: 1, x: 0 }}
              exit={{ opacity: 0, x: -10 }}
              transition={{ duration: 0.2 }}
            >
              {renderContent()}
            </motion.div>
          </AnimatePresence>
        </div>

      </div>
    </div>
  );
}
