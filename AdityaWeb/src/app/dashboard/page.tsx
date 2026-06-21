'use client';

import { useState, useEffect } from 'react';
import { motion } from 'framer-motion';

export default function Dashboard() {
  const [isLoading, setIsLoading] = useState(true);
  const [actionState, setActionState] = useState<string | null>(null);
  const [toast, setToast] = useState<string | null>(null);

  const handleAction = (action: string) => {
    setActionState(action);
    setToast(null);
    setTimeout(() => {
      setActionState(null);
      setToast(action === 'ignition' ? 'V12 Engine Primed.' : 'Phantom Mode Armed.');
      setTimeout(() => setToast(null), 3000);
    }, 2000);
  };

  useEffect(() => {
    // Simulate loading data securely without real PC connection
    const timer = setTimeout(() => {
      setIsLoading(false);
    }, 2000);
    return () => clearTimeout(timer);
  }, []);

  return (
    <div className="min-h-screen w-full bg-[var(--color-midnight)] text-white p-8 font-sans">
      <header className="mb-12">
        <h1 className="text-4xl font-serif text-[var(--color-silver)]">Command Center</h1>
        <p className="text-gray-400 mt-2">Isolated Telemetry Interface.</p>
      </header>

      <main className="grid grid-cols-1 md:grid-cols-3 gap-8">
        
        {/* Stream Stats Card */}
        <div className="glass-panel p-6 h-64 flex flex-col justify-between">
          <h3 className="text-lg text-gray-300">Live Viewers</h3>
          {isLoading ? (
            <div className="w-full h-24 bg-white/5 rounded animate-pulse" />
          ) : (
            <motion.div 
              initial={{ opacity: 0 }} animate={{ opacity: 1 }}
              className="flex items-end h-24 space-x-2"
            >
              {/* Minimalist Sparkline Mock */}
              {[40, 60, 45, 80, 50, 90, 75].map((val, i) => (
                <div key={i} className="w-8 bg-blue-500 rounded-t-sm" style={{ height: `${val}%` }} />
              ))}
            </motion.div>
          )}
          <p className="text-3xl font-light">4,209</p>
        </div>

        {/* CPU Thermals Card */}
        <div className="glass-panel p-6 h-64 flex flex-col justify-between">
          <h3 className="text-lg text-gray-300">Thermal Core (Mocked)</h3>
          {isLoading ? (
            <div className="w-full h-24 bg-white/5 rounded animate-pulse" />
          ) : (
            <motion.div 
              initial={{ opacity: 0 }} animate={{ opacity: 1 }}
              className="flex items-center justify-center h-24"
            >
              <div className="w-32 h-32 border-4 border-red-500/30 rounded-full flex items-center justify-center">
                <span className="text-4xl">72°</span>
              </div>
            </motion.div>
          )}
          <p className="text-sm text-gray-400">Failsafe: Armed</p>
        </div>

        {/* Action Panel */}
        <div className="glass-panel p-6 h-64 flex flex-col justify-center items-center space-y-4 relative">
          {isLoading ? (
            <div className="w-full h-full bg-white/5 rounded animate-pulse" />
          ) : (
            <>
              {toast && (
                <motion.div 
                  initial={{ opacity: 0, y: -10 }} animate={{ opacity: 1, y: 0 }} exit={{ opacity: 0 }}
                  className="absolute top-2 text-sm text-green-400 bg-green-400/10 px-3 py-1 rounded-full border border-green-400/20"
                >
                  {toast}
                </motion.div>
              )}
              <button 
                onClick={() => handleAction('ignition')}
                disabled={actionState === 'ignition'}
                className="apple-hover w-full py-3 rounded-lg bg-white/10 text-white font-medium border border-white/20 flex justify-center items-center h-12"
              >
                {actionState === 'ignition' ? <div className="w-5 h-5 border-2 border-white/30 border-t-white rounded-full animate-spin" /> : 'Trigger V12 Ignition'}
              </button>
              <button 
                onClick={() => handleAction('phantom')}
                disabled={actionState === 'phantom'}
                className="apple-hover w-full py-3 rounded-lg bg-red-500/20 text-red-400 font-medium border border-red-500/30 flex justify-center items-center h-12"
              >
                {actionState === 'phantom' ? <div className="w-5 h-5 border-2 border-red-400/30 border-t-red-400 rounded-full animate-spin" /> : 'Engage Phantom Mode'}
              </button>
            </>
          )}
        </div>

      </main>
    </div>
  );
}
