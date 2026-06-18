// ─── utils/logger.js ────────────────────────────────────────────────────────
// Centralized Logger to handle structured logging and forward errors to backend if needed.

const LOG_LEVELS = {
  DEBUG: 0,
  INFO: 1,
  WARN: 2,
  ERROR: 3,
};

// Set current log level (could read from settings/process env in future)
const CURRENT_LOG_LEVEL = LOG_LEVELS.INFO;

function log(level, message, extra = null) {
  if (LOG_LEVELS[level] < CURRENT_LOG_LEVEL) return;

  const timestamp = new Date().toISOString();
  const logPrefix = `[ADITYA][${level}][${timestamp}]`;

  if (extra) {
    console.log(logPrefix, message, extra);
  } else {
    console.log(logPrefix, message);
  }

  // If it's a critical error, we can send it asynchronously to a local backend API
  if (level === 'ERROR') {
    try {
      fetch('http://localhost:8000/api/logs', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          level,
          message: typeof message === 'object' ? message.message || JSON.stringify(message) : message,
          extra: extra ? (extra.stack || JSON.stringify(extra)) : null,
          timestamp
        })
      }).catch(() => {
        // Silent catch: prevent cyclic errors if backend is dead
      });
    } catch (e) {
      // Silent catch
    }
  }
}

export const logger = {
  debug: (msg, extra) => log('DEBUG', msg, extra),
  info: (msg, extra) => log('INFO', msg, extra),
  warn: (msg, extra) => log('WARN', msg, extra),
  error: (msg, extra) => log('ERROR', msg, extra),
};
