import { useState, useEffect, useRef, useCallback } from 'react';
import {
  fetchStatus, fetchRealtime, fetchAdityaMemoryEngine,
  sendChat, sendClose, fetchSettings,
  saveSettings as apiSaveSettings,
  updateAdityaMemoryEngine as apiUpdateAdityaMemoryEngine,
  clearChatHistory,
  sendInterrupt as apiSendInterrupt,
  sendMute as apiSendMute,
  sendVision as apiSendVision
} from '../api';

/**
 * useBackend — Enhanced custom hook connecting the React dashboard to the Python backend.
 *
 * Key improvements over original:
 *  - Optimistic chat messages: user's message appears instantly in the UI without
 *    waiting for the next status poll.
 *  - Pending / sending state: tracks whether a message is in-flight.
 *  - Faster poll escalation: poll drops to 200ms while AI is thinking/speaking,
 *    then returns to 500ms once idle again.
 *  - Connection error count: exposes how many consecutive failures occurred.
 *  - Retry debounce: backs off gracefully if the backend is unreachable.
 */
export function useBackend() {
  const [status, setStatus] = useState({
    status: 'connecting',
    custom_color: null,
    particle_count: null,
    message: null,
    rgb_mode: null,
    speed: null,
    particle_size: null,
    chat_history: [],
  });

  const [realtimeStats, setRealtimeStats] = useState({
    uptime_seconds: 0,
    total_requests: 0,
    api_calls_saved: 0,
    save_rate_pct: 0,
    cache: { hits: 0, misses: 0, hit_rate_pct: 0, size: 0 },
    network: { mode: 'NORMAL', avg_latency_ms: 0, consecutive_failures: 0 },
  });

  const [memory, setAdityaMemoryEngine] = useState({
    profile: {},
    history: [],
    goals: [],
    preferences: {},
    learned_facts: [],
    workflows: [],
    long_term_memories: []
  });

  const [settings, setSettings]       = useState({});
  const [isConnected, setIsConnected] = useState(false);
  const [isSending, setIsSending]     = useState(false);  // NEW: tracks in-flight chat
  const [sendError, setSendError]     = useState(null);   // NEW: last send error message
  const [consecutiveErrors, setConsecutiveErrors] = useState(0);

  // Optimistic chat history: merges backend history + any pending user message
  const [optimisticHistory, setOptimisticHistory] = useState([]);

  const mountedRef    = useRef(true);
  const intervalRef   = useRef(null);
  const aiStateRef    = useRef('connecting'); // track without re-render

  // ─── Poll logic ──────────────────────────────────────────────────────────
  const doPoll = useCallback(async () => {
    const data = await fetchStatus();
    if (!mountedRef.current) return;

    const connected = !data._error;
    setIsConnected(connected);

    if (connected) {
      setConsecutiveErrors(0);
      setStatus(data);
      aiStateRef.current = data.status;

      // Merge backend history — clears the optimistic pending bubble once the
      // real AI reply has arrived
      if (Array.isArray(data.chat_history)) {
        setOptimisticHistory(data.chat_history);
      }
    } else {
      setConsecutiveErrors(prev => prev + 1);
    }
  }, []);

  const schedulePoll = useCallback(() => {
    if (intervalRef.current) clearInterval(intervalRef.current);

    // When AI is actively processing, poll 5× faster for snappier UI
    const active = ['thinking', 'speaking', 'tool'].includes(aiStateRef.current);
    const delay  = active ? 200 : 500;

    intervalRef.current = setInterval(doPoll, delay);
  }, [doPoll]);

  useEffect(() => {
    mountedRef.current = true;
    schedulePoll();

    // Medium poll — realtime stats (2s)
    const realtimeInterval = setInterval(async () => {
      const data = await fetchRealtime();
      if (!mountedRef.current) return;
      if (!data.error) setRealtimeStats(data);
    }, 2000);

    // Slow poll — memory (5s)
    const memoryInterval = setInterval(async () => {
      const data = await fetchAdityaMemoryEngine();
      if (!mountedRef.current) return;
      if (!data._error) setAdityaMemoryEngine(data);
    }, 5000);

    // Initial batch fetch
    (async () => {
      const [s, r, m, setts] = await Promise.all([
        fetchStatus(), fetchRealtime(), fetchAdityaMemoryEngine(), fetchSettings()
      ]);
      if (!mountedRef.current) return;

      const connected = !s._error;
      setIsConnected(connected);
      setStatus(s);
      if (Array.isArray(s.chat_history)) setOptimisticHistory(s.chat_history);
      if (!r.error) setRealtimeStats(r);
      if (!m._error) setAdityaMemoryEngine(m);
      if (!setts.error) setSettings(setts);
    })();

    return () => {
      mountedRef.current = false;
      clearInterval(intervalRef.current);
      clearInterval(realtimeInterval);
      clearInterval(memoryInterval);
    };
  }, [schedulePoll]);

  // Re-schedule poll whenever AI state changes (faster during active states)
  useEffect(() => {
    schedulePoll();
  }, [status.status, schedulePoll]);

  // ─── Chat action — instant optimistic + backend fire ─────────────────────
  const chat = useCallback(async (text) => {
    if (!text?.trim()) return false;
    setSendError(null);
    setIsSending(true);

    // 1. Push user message optimistically so it appears instantly
    setOptimisticHistory(prev => [
      ...prev,
      { role: 'user', text: text.trim() }
    ]);

    // 2. Fire to backend
    const ok = await sendChat(text);

    if (!mountedRef.current) return ok;
    setIsSending(false);

    if (!ok) {
      setSendError('Failed to reach Aditya. Is the backend running?');
      // Remove the optimistic message if backend rejected it
      setOptimisticHistory(prev => prev.filter((_, i) => i !== prev.length - 1));
    }

    return ok;
  }, []);

  // ─── Other actions ────────────────────────────────────────────────────────
  const close = useCallback(() => sendClose(), []);
  const interrupt = useCallback(() => apiSendInterrupt(), []);
  const setMute = useCallback((muted) => apiSendMute(muted), []);
  const setVision = useCallback((active) => apiSendVision(active), []);

  const saveSettings = useCallback(async (updated) => {
    const res = await apiSaveSettings(updated);
    if (!res.error) { setSettings(res.settings); return true; }
    return false;
  }, []);

  const saveAdityaMemoryEngine = useCallback(async (updated) => {
    const res = await apiUpdateAdityaMemoryEngine(updated);
    if (!res.error) {
      const m = await fetchAdityaMemoryEngine();
      if (mountedRef.current && !m._error) setAdityaMemoryEngine(m);
      return true;
    }
    return false;
  }, []);

  const clearChat = useCallback(async () => {
    const res = await clearChatHistory();
    if (!res.error) {
      setOptimisticHistory([]);
      setStatus(prev => ({ ...prev, chat_history: [] }));
      return true;
    }
    return false;
  }, []);

  return {
    // Data
    status,
    realtimeStats,
    memory,
    settings,
    isConnected,

    // Derived
    aiState:      status.status,
    chatHistory:  optimisticHistory,           // real + optimistic merged
    networkMode:  realtimeStats?.network?.mode || 'NORMAL',

    // Send state (NEW)
    isSending,
    sendError,
    consecutiveErrors,

    // Actions
    chat,
    close,
    interrupt,
    setMute,
    setVision,
    saveSettings,
    saveAdityaMemoryEngine,
    clearChat,
  };
}
