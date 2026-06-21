// ─── utils/apiHelper.js ───────────────────────────────────────────────────
// Wrapper around fetch to add auto-retrying, timeouts, and structured error handling.
import { logger } from './logger';

const DEFAULT_RETRIES = 3;
const DEFAULT_DELAY = 1000; // ms

/**
 * Enhanced fetch wrapper with auto-retry on server failures (5xx, Network Errors) and timeouts.
 */
export async function stableFetch(url, options = {}, retries = DEFAULT_RETRIES, delay = DEFAULT_DELAY) {
  const { timeout = 10000, ...fetchOptions } = options;

  const controller = new AbortController();
  const id = setTimeout(() => controller.abort(), timeout);

  try {
    const response = await fetch(url, {
      ...fetchOptions,
      signal: controller.signal
    });

    clearTimeout(id);

    // If it's a server-side error (5xx), we retry
    if (response.status >= 500 && retries > 0) {
      logger.warn(`API server returned status ${response.status}. Retrying in ${delay}ms... (Remaining attempts: ${retries})`, { url });
      await new Promise(resolve => setTimeout(resolve, delay));
      return stableFetch(url, options, retries - 1, delay * 1.5);
    }

    return response;
  } catch (error) {
    clearTimeout(id);

    // If aborted due to timeout or network failure, retry
    if (retries > 0) {
      const isTimeout = error.name === 'AbortError';
      logger.warn(
        isTimeout 
          ? `Request timed out. Retrying in ${delay}ms...` 
          : `Network error: ${error.message}. Retrying in ${delay}ms...`,
        { url }
      );
      await new Promise(resolve => setTimeout(resolve, delay));
      return stableFetch(url, options, retries - 1, delay * 1.5);
    }

    logger.error(`API request failed completely: ${error.message}`, { url });
    throw error;
  }
}
