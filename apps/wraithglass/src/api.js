/**
 * api.js — Service layer connecting the React dashboard to the Python backend.
 * The backend runs at http://localhost:7865 (ui_server.py).
 * Uses stableFetch for API stability under network delay/offline conditions.
 */
import { stableFetch } from './utils/apiHelper';

const API_BASE = 'http://localhost:7865';

/**
 * Fetch AI status (polling target — called every 500ms)
 * We limit retries for status polling to avoid stack pileup when completely offline.
 */
export async function fetchStatus() {
  try {
    const res = await stableFetch(`${API_BASE}/api/status`, { timeout: 3000 }, 1, 500);
    if (!res.ok) throw new Error(`Status ${res.status}`);
    return await res.json();
  } catch (err) {
    return { status: 'offline', chat_history: [], _error: err.message };
  }
}

/**
 * Fetch realtime engine stats
 */
export async function fetchRealtime() {
  try {
    const res = await stableFetch(`${API_BASE}/api/realtime`, { timeout: 3000 }, 2, 800);
    if (!res.ok) throw new Error(`Realtime ${res.status}`);
    return await res.json();
  } catch (err) {
    return { error: err.message };
  }
}

/**
 * Fetch memory data
 */
export async function fetchWraithglassMemoryEngine() {
  try {
    const res = await stableFetch(`${API_BASE}/api/memory`);
    if (!res.ok) throw new Error(`WraithglassMemoryEngine ${res.status}`);
    return await res.json();
  } catch (err) {
    return { profile: {}, history: [], _error: err.message };
  }
}

/**
 * Send a chat message to the AI
 */
export async function sendChat(text) {
  try {
    await stableFetch(`${API_BASE}/api/chat`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ text }),
    });
    return true;
  } catch {
    return false;
  }
}

/**
 * Request the AI to shut down
 */
export async function sendClose() {
  try {
    await stableFetch(`${API_BASE}/api/close`, { method: 'POST' });
    return true;
  } catch {
    return false;
  }
}

export async function sendInterrupt() {
  try {
    await stableFetch(`${API_BASE}/api/interrupt`, { method: 'POST' });
    return true;
  } catch {
    return false;
  }
}

export async function sendMute(muted) {
  try {
    await stableFetch(`${API_BASE}/api/mute`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ muted }),
    });
    return true;
  } catch {
    return false;
  }
}

export async function sendVision(active) {
  try {
    await stableFetch(`${API_BASE}/api/vision`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ active }),
    });
    return true;
  } catch {
    return false;
  }
}

/**
 * Fetch system settings
 */
export async function fetchSettings() {
  try {
    const res = await stableFetch(`${API_BASE}/api/settings`);
    if (!res.ok) throw new Error(`Settings ${res.status}`);
    return await res.json();
  } catch (err) {
    return { error: err.message };
  }
}

/**
 * Update system settings
 */
export async function saveSettings(data) {
  try {
    const res = await stableFetch(`${API_BASE}/api/settings`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify(data),
    });
    if (!res.ok) throw new Error(`Save settings failed: ${res.status}`);
    return await res.json();
  } catch (err) {
    return { error: err.message };
  }
}

/**
 * Fetch workspace files (search + sort)
 */
export async function fetchFiles(query = '', sortBy = 'name', descending = false) {
  try {
    const params = new URLSearchParams({ query, sort_by: sortBy, descending: String(descending) });
    const res = await stableFetch(`${API_BASE}/api/files?${params}`);
    if (!res.ok) throw new Error(`Files ${res.status}`);
    return await res.json();
  } catch (err) {
    return [];
  }
}

/**
 * Fetch file preview content safely
 */
export async function fetchFilePreview(path) {
  try {
    const params = new URLSearchParams({ path });
    const res = await stableFetch(`${API_BASE}/api/files/preview?${params}`);
    if (!res.ok) throw new Error(`Preview ${res.status}`);
    return await res.json();
  } catch (err) {
    return { error: err.message };
  }
}

/**
 * Start research job in background
 */
export async function startResearch(query) {
  try {
    const res = await stableFetch(`${API_BASE}/api/research`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ query }),
    });
    if (!res.ok) throw new Error(`Research start failed: ${res.status}`);
    return await res.json();
  } catch (err) {
    return { error: err.message };
  }
}

/**
 * Fetch research job details or list of all jobs
 */
export async function fetchResearch(jobId = '') {
  try {
    const params = jobId ? new URLSearchParams({ job_id: jobId }) : '';
    const res = await stableFetch(`${API_BASE}/api/research${params ? '?' + params : ''}`);
    if (!res.ok) throw new Error(`Research get failed: ${res.status}`);
    return await res.json();
  } catch (err) {
    return jobId ? { error: err.message } : [];
  }
}

/**
 * Update memory items
 */
export async function updateWraithglassMemoryEngine(data) {
  try {
    const res = await stableFetch(`${API_BASE}/api/memory`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify(data),
    });
    if (!res.ok) throw new Error(`WraithglassMemoryEngine update failed: ${res.status}`);
    return await res.json();
  } catch (err) {
    return { error: err.message };
  }
}

/**
 * Clear chat history in the backend
 */
export async function clearChatHistory() {
  try {
    const res = await stableFetch(`${API_BASE}/api/chat/clear`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
    });
    if (!res.ok) throw new Error(`Clear chat failed: ${res.status}`);
    return await res.json();
  } catch (err) {
    return { error: err.message };
  }
}
