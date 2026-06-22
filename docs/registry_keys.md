# Windows Registry Configuration

VESPERA OS integrates with Windows registry hives for startup behaviors.

## Registry Subkeys

### 1. AutoRun key
- Path: `HKCU\Software\Microsoft\Windows\CurrentVersion\Run`
- Value Name: `VESPERA OS`
- Value: Path to `VESPERA Setup 1.0.0.exe` or compiled app entry point.

## Safety & Access Controls
- All registry queries catch permissions exceptions locally to avoid system crashes if running under non-administrator accounts.
- Falls back to startup directory shortcuts if registry access is blocked.
