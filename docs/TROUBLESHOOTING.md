# VESPERA OS Troubleshooting Guide

This guide covers common issues, root causes, and resolutions for developing or running VESPERA OS.

---

## 1. App Crashes Immediately on Launch (Windows console flashes/closes)

### Symptom
The desktop executable crashes immediately on startup.

### Resolution
Check `packages/umbracore/main.py` database integrity checks:
- Ensure `memory_system` is imported locally or globally without causing a circular dependency.
- Make sure stdout encoding doesn't crash on standard Windows consoles. We force encoding wrappers in `packages/umbracore/core/vespera_memory.py` to prevent `UnicodeEncodeError`.

---

## 2. Windows Locked File Errors (`PermissionError: [WinError 32]`)

### Symptom
Running unit tests or deleting test directories throws a permission error:
`PermissionError: [WinError 32] The process cannot access the file because it is being used by another process`

### Resolution
Windows holds locks on file descriptors that haven't been garbage-collected yet.
In your teardown code, invoke Python's garbage collector before deleting folders:
```python
import gc
gc.collect()
```

---

## 3. SQLite Database Integrity Corruption

### Symptom
`sqlite3.DatabaseError: file is encrypted or is not a database` or `database disk image is malformed`.

### Resolution
Run the built-in database doctor module to verify and automatically repair sqlite structures:
```bash
python packages/umbracore/main.py --repair-db
```
This will back up the old database and rebuild tables cleanly.
