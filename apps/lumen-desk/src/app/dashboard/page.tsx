'use client';

import { useState, useEffect } from 'react';
import { motion, AnimatePresence } from 'framer-motion';

interface TelemetryData {
  status: string;
  custom_color: string | null;
  particle_count: number | null;
  message: string | null;
  rgb_mode: boolean | null;
  speed: number | null;
  particle_size: number | null;
  chat_history: Array<{ role: string; text: string }>;
  active_workspace: string;
  metrics: {
    cpu: number;
    ram: number;
    gpu: string;
  };
}

export default function Dashboard() {
  const [data, setData] = useState<TelemetryData | null>(null);
  const [isOffline, setIsOffline] = useState(true);
  const [isMuted, setIsMuted] = useState(false);
  const [visionActive, setVisionActive] = useState(false);
  const [actionState, setActionState] = useState<string | null>(null);
  const [toast, setToast] = useState<{ type: 'success' | 'error'; message: string } | null>(null);

  const API_BASE = 'http://127.0.0.1:7865';

  const showToast = (message: string, type: 'success' | 'error' = 'success') => {
    setToast({ type, message });
    setTimeout(() => setToast(null), 3000);
  };

  const fetchStatus = async () => {
    try {
      const res = await fetch(`${API_BASE}/api/status`);
      if (res.ok) {
        const json = await res.json();
        setData(json);
        setIsOffline(false);
      } else {
        setIsOffline(true);
      }
    } catch {
      setIsOffline(true);
    }
  };

  useEffect(() => {
    // Initial fetch
    fetchStatus();
    // Poll every 2 seconds
    const interval = setInterval(fetchStatus, 2000);
    return () => clearInterval(interval);
  }, []);

  const triggerAction = async (endpoint: string, payload?: any, actionName?: string) => {
    if (actionName) setActionState(actionName);
    try {
      const options: RequestInit = {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
      };
      if (payload !== undefined) {
        options.body = JSON.stringify(payload);
      }
      const res = await fetch(`${API_BASE}/api/${endpoint}`, options);
      if (res.ok) {
        showToast(`${actionName || endpoint} successfully executed.`);
        if (endpoint === 'mute') setIsMuted(payload.muted);
        if (endpoint === 'vision') setVisionActive(payload.active);
      } else {
        showToast(`Failed to execute ${actionName || endpoint}`, 'error');
      }
    } catch {
      showToast(`Connection error to ${actionName || endpoint}`, 'error');
    } finally {
      if (actionName) setActionState(null);
      fetchStatus();
    }
  };

  return (
    <div className="min-h-screen w-full bg-[#0A0D14] text-white p-6 md:p-12 font-sans selection:bg-blue-500/30 selection:text-blue-200">
      <header className="mb-10 flex flex-col md:flex-row md:items-center md:justify-between gap-4 border-b border-white/5 pb-6">
        <div>
          <h1 className="text-4xl font-serif tracking-tight bg-gradient-to-r from-white via-slate-200 to-slate-400 bg-clip-text text-transparent">
            Vespera Command Center
          </h1>
          <p className="text-slate-400 mt-2 text-sm md:text-base flex items-center gap-2">
            <span className={`w-2.5 h-2.5 rounded-full ${isOffline ? 'bg-red-500 shadow-[0_0_8px_rgba(239,68,68,0.5)]' : 'bg-emerald-500 shadow-[0_0_8px_rgba(16,185,129,0.5)]'}`} />
            {isOffline ? 'Offline - Awaiting Core Connection' : `Core Active • Mode: ${data?.status.toUpperCase()}`}
          </p>
        </div>
        <div className="flex items-center gap-3">
          <span className="text-xs tracking-wider text-slate-500 uppercase font-mono">Workspace</span>
          <span className="px-3 py-1 bg-white/5 border border-white/10 rounded-full text-xs font-mono text-blue-400">
            {isOffline ? 'N/A' : data?.active_workspace || 'general'}
          </span>
        </div>
      </header>

      {/* Toast Notification */}
      <AnimatePresence>
        {toast && (
          <motion.div
            initial={{ opacity: 0, y: -20 }}
            animate={{ opacity: 1, y: 0 }}
            exit={{ opacity: 0, y: -20 }}
            className={`fixed top-6 right-6 z-50 px-4 py-3 rounded-xl border text-sm font-medium shadow-lg backdrop-blur-md flex items-center gap-2 ${
              toast.type === 'success'
                ? 'bg-emerald-950/80 text-emerald-400 border-emerald-500/30'
                : 'bg-red-950/80 text-red-400 border-red-500/30'
            }`}
          >
            <span>{toast.message}</span>
          </motion.div>
        )}
      </AnimatePresence>

      <main className="grid grid-cols-1 lg:grid-cols-3 gap-8">
        
        {/* Real-time System Metrics */}
        <section className="glass-panel p-6 flex flex-col justify-between border border-white/5 rounded-2xl bg-white/[0.02] backdrop-blur-xl h-80">
          <div>
            <h3 className="text-sm font-semibold tracking-wider text-slate-400 uppercase font-mono mb-6">System Telemetry</h3>
            <div className="space-y-6">
              {/* CPU Progress Bar */}
              <div>
                <div className="flex justify-between text-xs font-mono text-slate-400 mb-2">
                  <span>CPU Load</span>
                  <span>{isOffline ? '0%' : `${data?.metrics.cpu}%`}</span>
                </div>
                <div className="w-full h-2 bg-white/5 rounded-full overflow-hidden">
                  <motion.div
                    className="h-full bg-gradient-to-r from-blue-500 to-indigo-500"
                    animate={{ width: isOffline ? '0%' : `${data?.metrics.cpu}%` }}
                    transition={{ duration: 0.5 }}
                  />
                </div>
              </div>

              {/* RAM Progress Bar */}
              <div>
                <div className="flex justify-between text-xs font-mono text-slate-400 mb-2">
                  <span>RAM Usage</span>
                  <span>{isOffline ? '0%' : `${data?.metrics.ram}%`}</span>
                </div>
                <div className="w-full h-2 bg-white/5 rounded-full overflow-hidden">
                  <motion.div
                    className="h-full bg-gradient-to-r from-indigo-500 to-purple-500"
                    animate={{ width: isOffline ? '0%' : `${data?.metrics.ram}%` }}
                    transition={{ duration: 0.5 }}
                  />
                </div>
              </div>
            </div>
          </div>
          
          <div className="border-t border-white/5 pt-4 mt-4">
            <span className="text-[10px] tracking-wider text-slate-500 uppercase font-mono block mb-1">Active GPU</span>
            <span className="text-sm font-mono text-slate-300 truncate block">
              {isOffline ? 'Unknown device' : data?.metrics.gpu || 'N/A'}
            </span>
          </div>
        </section>

        {/* Live Chat & Log Console */}
        <section className="glass-panel p-6 flex flex-col justify-between border border-white/5 rounded-2xl bg-white/[0.02] backdrop-blur-xl h-80 lg:col-span-2">
          <div className="flex items-center justify-between mb-4">
            <h3 className="text-sm font-semibold tracking-wider text-slate-400 uppercase font-mono">Core Transcripts</h3>
            <span className="w-2 h-2 rounded-full bg-blue-500 animate-pulse" />
          </div>

          <div className="flex-1 overflow-y-auto font-mono text-xs space-y-3 pr-2 scrollbar-thin scrollbar-thumb-white/10 scrollbar-track-transparent">
            {isOffline ? (
              <div className="text-slate-500 italic h-full flex items-center justify-center">
                Waiting for feed connection...
              </div>
            ) : !data?.chat_history || data.chat_history.length === 0 ? (
              <div className="text-slate-500 italic h-full flex items-center justify-center">
                No telemetry transcripts found.
              </div>
            ) : (
              data.chat_history.map((msg, i) => (
                <div key={i} className={`p-2.5 rounded-lg border ${msg.role === 'user' ? 'bg-blue-950/20 border-blue-500/20 text-blue-300' : 'bg-white/[0.02] border-white/5 text-slate-300'}`}>
                  <span className="text-[10px] uppercase tracking-wider font-semibold text-slate-500 block mb-1">
                    {msg.role === 'user' ? 'User Input' : 'Vespera Output'}
                  </span>
                  <p className="whitespace-pre-wrap leading-relaxed">{msg.text}</p>
                </div>
              ))
            )}
          </div>
        </section>

        {/* Controls and Actions */}
        <section className="glass-panel p-6 border border-white/5 rounded-2xl bg-white/[0.02] backdrop-blur-xl lg:col-span-3">
          <h3 className="text-sm font-semibold tracking-wider text-slate-400 uppercase font-mono mb-6">Operations Panel</h3>
          
          <div className="grid grid-cols-1 sm:grid-cols-2 md:grid-cols-4 gap-4">
            {/* Mic Mute Toggle */}
            <button
              onClick={() => triggerAction('mute', { muted: !isMuted }, 'Mute Control')}
              disabled={isOffline || actionState === 'Mute Control'}
              className={`w-full py-4 px-6 rounded-xl border flex flex-col items-center justify-center gap-2 transition-all duration-300 ${
                isMuted 
                  ? 'bg-amber-500/10 border-amber-500/30 text-amber-400' 
                  : 'bg-white/[0.02] border-white/10 hover:bg-white/[0.05] hover:border-white/20 text-slate-300'
              }`}
            >
              <span className="text-lg font-semibold">{isMuted ? 'Unmute Mic' : 'Mute Mic'}</span>
              <span className="text-[10px] opacity-60 font-mono">Toggle Audio In</span>
            </button>

            {/* Vision Mode Toggle */}
            <button
              onClick={() => triggerAction('vision', { active: !visionActive }, 'Vision Control')}
              disabled={isOffline || actionState === 'Vision Control'}
              className={`w-full py-4 px-6 rounded-xl border flex flex-col items-center justify-center gap-2 transition-all duration-300 ${
                visionActive 
                  ? 'bg-blue-500/10 border-blue-500/30 text-blue-400' 
                  : 'bg-white/[0.02] border-white/10 hover:bg-white/[0.05] hover:border-white/20 text-slate-300'
              }`}
            >
              <span className="text-lg font-semibold">{visionActive ? 'Disable Vision' : 'Enable Vision'}</span>
              <span className="text-[10px] opacity-60 font-mono">Toggle Screen Monitor</span>
            </button>

            {/* Interrupt AI Trigger */}
            <button
              onClick={() => triggerAction('interrupt', undefined, 'Interrupt Trigger')}
              disabled={isOffline || actionState === 'Interrupt Trigger'}
              className="w-full py-4 px-6 rounded-xl border bg-white/[0.02] border-white/10 hover:bg-red-500/10 hover:border-red-500/30 hover:text-red-400 text-slate-300 flex flex-col items-center justify-center gap-2 transition-all duration-300"
            >
              <span className="text-lg font-semibold">Interrupt Core</span>
              <span className="text-[10px] opacity-60 font-mono">Halt Speech Generation</span>
            </button>

            {/* Close/Shutdown */}
            <button
              onClick={() => {
                if (confirm('Are you sure you want to terminate Vespera Core?')) {
                  triggerAction('close', undefined, 'Shutdown Core');
                }
              }}
              disabled={isOffline || actionState === 'Shutdown Core'}
              className="w-full py-4 px-6 rounded-xl border bg-white/[0.02] border-white/10 hover:bg-red-950/40 hover:border-red-600/40 hover:text-red-500 text-slate-300 flex flex-col items-center justify-center gap-2 transition-all duration-300"
            >
              <span className="text-lg font-semibold">Shutdown Core</span>
              <span className="text-[10px] opacity-60 font-mono">Terminate Engine Process</span>
            </button>
          </div>
        </section>

      </main>
    </div>
  );
}
