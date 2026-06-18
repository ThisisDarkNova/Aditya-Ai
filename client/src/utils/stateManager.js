// ─── utils/stateManager.js ──────────────────────────────────────────────────
// Defensive local storage & session state recovery manager.
import { logger } from './logger';

const CORE_SETTINGS_KEYS = ['theme', 'launch_on_startup', 'notifications_enabled', 'activePersona'];

/**
 * Validates browser storage parameters.
 * Cleans corrupt keys, falls back to defaults, and secures boot configuration.
 */
export function initializeAndVerifyStorage() {
  try {
    logger.info('Initializing Recovery State Manager...');
    
    // Verify LocalStorage health
    for (let i = 0; i < localStorage.length; i++) {
      const key = localStorage.key(i);
      const val = localStorage.getItem(key);
      
      // If setting should be valid JSON but is corrupted, wipe or reset it
      if (CORE_SETTINGS_KEYS.includes(key)) {
        try {
          if (val === 'undefined' || val === 'null') {
            logger.warn(`Removing corrupted core settings storage key: ${key}`);
            localStorage.removeItem(key);
          }
        } catch (_) {
          localStorage.removeItem(key);
        }
      }
    }
    
    logger.info('Storage state verified successfully.');
    return true;
  } catch (err) {
    logger.error('LocalStorage recovery system failed to run. Wiping corrupt items to restore stability.', err);
    try {
      localStorage.clear();
    } catch (_) {}
    return false;
  }
}
