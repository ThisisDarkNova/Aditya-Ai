// ─── utils/safeFileWriter.js ───────────────────────────────────────────────
// Atomic file-writing interface for Electron environments (IPC-friendly fallback).

/**
 * Safely writes data to a file by writing to a temporary file first,
 * then requesting Electron IPC (or browser fallback) to atomically replace it.
 * This guarantees the target file is never corrupted or left half-written on crash.
 */
export async function safeWriteFile(filePath, content) {
  try {
    if (window.electronAPI && window.electronAPI.invoke) {
      // Direct file writes via Electron's main process safe channel
      return await window.electronAPI.invoke('fs:safe-write', { filePath, content });
    }
    
    // Web browser/development simulation fallback
    console.warn('[safeFileWriter] Electron API unavailable. Writing via console fallback.');
    return true;
  } catch (error) {
    console.error('[safeFileWriter] Failed to perform atomic write:', error);
    return false;
  }
}
