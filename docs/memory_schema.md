# Cognitive Memory Schema

VESPERA OS uses SQLite3 database files to manage long-term contexts, preferences, chat histories, and learned workflows.

## Table Structures

### `chat_history`
- `id`: INTEGER PRIMARY KEY AUTOINCREMENT
- `timestamp`: TEXT (ISO8601 formatting)
- `role`: TEXT ('user' | 'ai')
- `message`: TEXT

### `settings`
- `key`: TEXT PRIMARY KEY
- `value`: TEXT (JSON serialized configurations)

### `workflows`
- `name`: TEXT PRIMARY KEY
- `steps`: TEXT (JSON array)
- `created_at`: TEXT

## Maintenance and Repairs
- Database files undergo integrity verification on startup.
- In case of SQLite corruption, the DB doctor copies the corrupted database to `db.sqlite3.backup` and creates a fresh database structure automatically.
