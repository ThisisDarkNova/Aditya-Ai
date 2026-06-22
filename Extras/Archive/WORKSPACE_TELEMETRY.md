# VESPERA Workspace Telemetry & Monitoring

This document describes how VESPERA monitors running processes, system performance, and active workspaces.

## Monitored Applications

VESPERA actively scans the running task list on Windows for the following categories:

| Category | Process Name | Action Triggered |
|---|---|---|
| **Valorant** | `VALORANT-Win64-Shipping.exe` | Launches Valorant Workspace (lineups, rank metrics). |
| **Fortnite** | `FortniteClient-Win64-Shipping.exe` | Launches Fortnite Workspace (aim configs, sensitivty). |
| **Minecraft** | `javaw.exe`, `minecraft.exe` | Launches Survival Assistant. |
| **OBS** | `obs64.exe`, `obs.exe` | Switches to Streamer Workspace and launches dashboard. |

## System Optimization

When a game workspace is detected, VESPERA enters **Game Boost** mode:
1. Temporarily suspends Windows Search Indexer service.
2. Elevates the game process's CPU priority to High.
3. Automatically silences notifications and alarms.
