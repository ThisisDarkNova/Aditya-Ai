// ─── utils/rateLimiter.js ──────────────────────────────────────────────────
// A client-side queue and rate-limiter to prevent 429 Too Many Requests errors.

class RequestRateLimiter {
  constructor(maxRequestsPerWindow = 10, windowMs = 5000) {
    self.maxRequests = maxRequestsPerWindow;
    self.window = windowMs;
    self.requestTimestamps = [];
    self.queue = [];
    self.processing = false;
  }

  /**
   * Wraps a promise-returning request function and throttles it.
   */
  async execute(fn) {
    return new Promise((resolve, reject) => {
      this.queue.push({ fn, resolve, reject });
      this._processQueue();
    });
  }

  async _processQueue() {
    if (this.processing || this.queue.length === 0) return;
    this.processing = true;

    while (this.queue.length > 0) {
      const now = Date.now();
      // Remove timestamps older than the window
      this.requestTimestamps = this.requestTimestamps.filter(t => now - t < this.window);

      if (this.requestTimestamps.length >= this.maxRequests) {
        const oldestTimestamp = this.requestTimestamps[0];
        const waitTime = this.window - (now - oldestTimestamp);
        await new Promise(resolve => setTimeout(resolve, Math.max(10, waitTime)));
        continue;
      }

      const { fn, resolve, reject } = this.queue.shift();
      this.requestTimestamps.push(Date.now());

      try {
        const result = await fn();
        resolve(result);
      } catch (err) {
        reject(err);
      }
    }

    this.processing = false;
  }
}

export const rateLimiter = new RequestRateLimiter(8, 4000); // Max 8 requests every 4 seconds
