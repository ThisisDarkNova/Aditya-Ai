import React, { useState, lazy, Suspense, useCallback, useEffect, useRef } from 'react';
import Sidebar from './components/Sidebar';
import StatusBar from './components/StatusBar';
import Visualizer from './components/Visualizer';
import BottomControls from './components/BottomControls';
import Startup from './components/Startup';
import { useBackend } from './hooks/useBackend';
import { AnimatePresence, motion } from 'framer-motion';

// Lazy load pages
const Home     = lazy(() => import('./components/pages/Home/index'));
const Profile = lazy(() => import('./components/pages/Profile/index'));
const Settings = lazy(() => import('./components/pages/Settings/index'));

/* ─── Connection Toast ─────────────────────────────────────────────────── */
function ConnectionToast({ isConnected, consecutiveErrors }) {
  const [visible, setVisible] = useState(false);
  const [msg, setMsg] = useState('');
  const [type, setType] = useState('error'); // 'error' | 'ok'
  const prevConnected = useRef(isConnected);
  const hideTimeout = useRef(null);

  useEffect(() => {
    const wasConnected = prevConnected.current;
    prevConnected.current = isConnected;

    if (!isConnected && wasConnected) {
      // Just disconnected
      setMsg('ADITYA lost connection to Gemini');
      setType('error');
      setVisible(true);
      if (hideTimeout.current) clearTimeout(hideTimeout.current);
    } else if (isConnected && !wasConnected) {
      // Just reconnected
      setMsg('ADITYA reconnected ✓');
      setType('ok');
      setVisible(true);
      hideTimeout.current = setTimeout(() => setVisible(false), 3000);
    }
  }, [isConnected]);

  return (
    <AnimatePresence>
      {visible && (
        <motion.div
          key="toast"
          initial={{ y: -60, opacity: 0 }}
          animate={{ y: 0, opacity: 1 }}
          exit={{ y: -60, opacity: 0 }}
          transition={{ type: 'spring', stiffness: 280, damping: 24 }}
          style={{
            position: 'fixed', top: 44, left: '50%', transform: 'translateX(-50%)',
            zIndex: 99998, display: 'flex', alignItems: 'center', gap: 10,
            padding: '10px 20px', borderRadius: 24,
            background: type === 'error'
              ? 'rgba(239,68,68,0.15)' : 'rgba(34,197,94,0.15)',
            border: `1px solid ${type === 'error' ? 'rgba(239,68,68,0.4)' : 'rgba(34,197,94,0.4)'}`,
            backdropFilter: 'blur(20px)',
            boxShadow: `0 8px 32px ${type === 'error' ? 'rgba(239,68,68,0.2)' : 'rgba(34,197,94,0.2)'}`,
          }}
        >
          {/* Dot */}
          <motion.div
            animate={{ opacity: type === 'error' ? [1, 0.3, 1] : 1 }}
            transition={{ duration: 1.2, repeat: type === 'error' ? Infinity : 0 }}
            style={{
              width: 8, height: 8, borderRadius: '50%',
              background: type === 'error' ? '#EF4444' : '#22C55E',
              flexShrink: 0,
            }}
          />
          <span style={{
            fontSize: 13, fontWeight: 500,
            color: type === 'error' ? '#FCA5A5' : '#86EFAC',
            fontFamily: 'Inter, sans-serif',
          }}>
            {msg}
          </span>
          {type === 'error' && (
            <button
              onClick={() => setVisible(false)}
              style={{ background: 'none', border: 'none', color: 'rgba(255,255,255,0.4)', cursor: 'pointer', padding: '0 4px', fontSize: 16, lineHeight: 1 }}
            >×</button>
          )}
        </motion.div>
      )}
    </AnimatePresence>
  );
}

import AmbientCanvas from './components/AmbientCanvas';

export default function App() {
  const backend = useBackend();
  const [activePage, setActivePage] = useState('Visualizer');
  const [showStartup, setShowStartup] = useState(true);
  const [activePersona, setActivePersona] = useState('student');
  const [hudAiState, setHudAiState] = useState(null);
  const [hudNetworkMode, setHudNetworkMode] = useState(null);

  useEffect(() => {
    // Run defensive local storage check on app initialization
    import('./utils/stateManager').then(({ initializeAndVerifyStorage }) => {
      initializeAndVerifyStorage();
    });
  }, []);

  const handleStartupComplete = useCallback(() => {
    setShowStartup(false);
  }, []);

  const resolvedAiState = hudAiState !== null ? hudAiState : backend.aiState;
  const resolvedNetworkMode = hudNetworkMode !== null ? hudNetworkMode : backend.networkMode;

  return (
    <div className={`theme-${activePersona}`} style={{ display: 'flex', flexDirection: 'column', width: '100%', height: '100%', background: 'var(--color-background)', overflow: 'hidden' }}>

      {/* GPU-Accelerated Dynamic Ambient Background Canvas */}
      <AmbientCanvas activePersona={activePersona} />

      {/* Global connection status toast */}
      <ConnectionToast isConnected={backend.isConnected} consecutiveErrors={backend.consecutiveErrors} />

      <AnimatePresence>
        {showStartup && (
          <motion.div key="startup" exit={{ opacity: 0 }} transition={{ duration: 0.8 }} style={{ position: 'absolute', inset: 0, zIndex: 99999 }}>
            <Startup onComplete={handleStartupComplete} />
          </motion.div>
        )}
      </AnimatePresence>

      {/* Draggable Frameless Titlebar */}
      <div className="titlebar" style={{ width: '100%', height: 32, flexShrink: 0, zIndex: 100, position: 'absolute', top: 0, left: 0 }} />

      {!showStartup && (
        <div className="flex w-full h-full relative" style={{ paddingTop: 32 }}>
          {/* Floating Glass Sidebar */}
          <div className="absolute left-4 top-10 bottom-4 z-50">
            <Sidebar setActivePage={setActivePage} activePage={activePage} status={backend.status} />
          </div>

          <main className="flex flex-col flex-1 min-w-0 relative overflow-hidden ml-[96px]">
            {/* Background: Voice Mode Visualizer & HUD */}
            <div className="absolute inset-0 flex flex-col z-0">
              <StatusBar
                isConnected={backend.isConnected}
                aiState={resolvedAiState}
                networkMode={resolvedNetworkMode}
              />
              <Visualizer
                aiState={resolvedAiState}
                statusMessage={backend.status.message}
              />
            </div>

            {/* Foreground: Page Overlays */}
            <div className="absolute inset-0 z-10 pointer-events-none">
              <Suspense fallback={<div className="w-full h-full bg-[var(--color-background)]/80 backdrop-blur-md" />}>
                <AnimatePresence mode="wait">
                  {activePage && activePage !== 'Visualizer' && (
                    <motion.div
                      key={activePage}
                      initial={{ opacity: 0, y: 10, filter: 'blur(10px)' }}
                      animate={{ opacity: 1, y: 0, filter: 'blur(0px)' }}
                      exit={{ opacity: 0, y: -10, filter: 'blur(10px)' }}
                      transition={{ duration: 0.4, ease: [0.16, 1, 0.3, 1] }}
                      className="absolute inset-0 pointer-events-auto flex flex-col overflow-y-auto"
                    >
                      {activePage === 'Home' && <Home status={backend.status} memory={backend.memory} settings={backend.settings} onChat={backend.chat} chatHistory={backend.chatHistory} aiState={resolvedAiState} setActivePage={setActivePage} isConnected={backend.isConnected} activePersona={activePersona} setActivePersona={setActivePersona} realtimeStats={backend.realtimeStats} />}
                      {activePage === 'Profile' && <Profile memory={backend.memory} saveAdityaMemoryEngine={backend.saveAdityaMemoryEngine} chatHistory={backend.chatHistory} realtimeStats={backend.realtimeStats} />}
                      {activePage === 'Settings' && <Settings settings={backend.settings} saveSettings={backend.saveSettings} setActivePage={setActivePage} activePersona={activePersona} onSelectPersona={setActivePersona} />}
                    </motion.div>
                  )}
                </AnimatePresence>
              </Suspense>
            </div>

            {/* Floating Bottom Dock */}
            {activePage !== 'Chat' && (
              <BottomControls
                backend={backend}
                onChat={backend.chat}
                aiState={resolvedAiState}
                setActivePage={setActivePage}
              />
            )}
          </main>
        </div>
      )}
    </div>
  );
}
