# VESPERA OS Core API Documentation

VESPERA OS exposes a local HTTP JSON API on port `7865` for communication between the Electron UI frontend, webviews, and external integrations.

---

## 1. System Status & Control

### `GET /api/status`
Retrieves the overall status, orb styling parameters, chat history, and system metrics.

**Response Schema:**
```json
{
  "status": "listening" | "speaking" | "thinking" | "tool" | "offline",
  "custom_color": "#HEXCODE" | null,
  "particle_count": number | null,
  "message": string | null,
  "rgb_mode": boolean | null,
  "speed": number | null,
  "particle_size": number | null,
  "chat_history": [
    { "role": "user" | "ai", "text": "Message content" }
  ],
  "active_workspace": "general",
  "metrics": {
    "cpu": number,
    "ram": number,
    "gpu": "N/A" | string
  }
}
```

---

## 2. Voice & Realtime Engine

### `GET /api/realtime`
Fetches current voice processing, speech-to-text, and audio engine statuses.

---

## 3. Memory & Personalization

### `GET /api/memory`
Retrieves stored context, preferences, learned facts, goals, and history from the cognitive memory database.

**Response Schema:**
```json
{
  "profile": {},
  "history": [],
  "goals": [],
  "preferences": {},
  "learned_facts": [],
  "workflows": [],
  "long_term_memories": []
}
```

---

## 4. Application Management

### `GET /api/resolve-app?name=<app_name>`
Fuzzy-resolves an application query to its executable path and metadata.

**Response Example:**
```json
{
  "name": "Chrome",
  "path": "C:\\Program Files\\Google\\Chrome\\Application\\chrome.exe",
  "aliases": ["chrome", "browser"]
}
```

### `GET /api/focus-app?name=<app_name>`
Brings the resolved application window to the foreground.

---

## 5. File Indexer & Preview

### `GET /api/files?query=<search_query>&sort_by=<name|date>&descending=<true|false>`
Search and filter indexed workspace files.

### `GET /api/files/preview?path=<file_path>`
Gets safe preview details of a file (e.g., contents, type, and dimensions).

---

## 6. Actions & Integrations

### `POST /api/open-anything`
Executes an intelligent launcher sequence to open a URL, a folder, a system application, or a workspace file based on natural language input.

**Request Payload:**
```json
{
  "query": "open chrome"
}
```

### `POST /api/chat`
Queues a new chat input message into the cognitive queue.

**Request Payload:**
```json
{
  "text": "Check system disk space"
}
```

### `POST /api/settings`
Updates system settings dynamically. Supports auto-registry update for startup behavior.

**Request Payload:**
```json
{
  "startup_delay_seconds": 15,
  "temperature": 0.7,
  "font_size": 14,
  "max_agent_loops": 10
}
```

### `POST /api/research`
Spawns a background search/scraping research job.

**Request Payload:**
```json
{
  "query": "Deep learning paper on state space models"
}
```
