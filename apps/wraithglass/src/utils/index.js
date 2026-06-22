// ─── utils/index.js ──────────────────────────────────────────────────────
// Shared utility/helper functions used across multiple pages.

/**
 * Returns a time-aware greeting string.
 * @returns {string} e.g. "Good Morning", "Good Evening"
 */
export function getGreeting() {
  const hrs = new Date().getHours();
  if (hrs < 12) return 'Good Morning';
  if (hrs < 17) return 'Good Afternoon';
  if (hrs < 21) return 'Good Evening';
  return 'Good Night';
}

/**
 * Formats seconds into a human-readable duration.
 * @param {number} seconds
 * @returns {string} e.g. "2h 30m", "45m", "—"
 */
export function formatUptime(seconds) {
  if (!seconds || seconds <= 0) return '—';
  const h = Math.floor(seconds / 3600);
  const m = Math.floor((seconds % 3600) / 60);
  if (h > 0) return `${h}h ${m}m`;
  if (m > 0) return `${m}m`;
  return '<1m';
}

/**
 * Formats a date into a relative relationship age string.
 * @param {string|Date|null} dateInput
 * @returns {string} e.g. "3mo", "12d", "Today", "—"
 */
export function formatRelativeAge(dateInput) {
  if (!dateInput) return '—';
  const date = new Date(dateInput);
  if (isNaN(date)) return '—';
  const diffDays = Math.floor((Date.now() - date) / 86400000);
  if (diffDays < 1) return 'Today';
  if (diffDays < 30) return `${diffDays}d`;
  return `${Math.floor(diffDays / 30)}mo`;
}

/**
 * Safely extracts a display name from a goal object or string.
 * @param {string|object} goal
 * @returns {string}
 */
export function extractGoalText(goal) {
  if (typeof goal === 'string') return goal;
  return goal?.title || goal?.text || goal?.goal || String(goal);
}

/**
 * Clamps a number between min and max.
 * @param {number} val
 * @param {number} min
 * @param {number} max
 * @returns {number}
 */
export function clamp(val, min, max) {
  return Math.min(Math.max(val, min), max);
}
