# Contributing to Vespera

First off, thank you for considering contributing to Vespera. It's people like you that make this ecosystem unparalleled.

## The Omni-Presence Architecture
Vespera is not a simple script; it is a Sentient Operating System. When contributing, please ensure you understand the 5 pillars:
1. `VesperaWeb` (Next.js)
2. `umbracore` (Python Daemons)
3. `aegis-cast` (React OBS Overlays)
4. `VSCodeExtension` (TypeScript Marginalia)
5. `wraithglass` (Electron)

## Local Development
Do not submit PRs without verifying that the master build script passes locally:
```powershell
.\build_ascended.ps1
```

## Submitting Pull Requests
1. Fork the repository.
2. Create a new branch `feature/your-feature-name`.
3. Ensure the architectural integrity is maintained (no cloud telemetry without user consent; Vespera is local-first).
4. Submit your PR with a detailed breakdown of the changes.
