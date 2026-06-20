# Frequently Asked Questions (FAQ)

Here are answers to the most common questions regarding **ADITYA OS**.

## 1. Why does my microphone not connect?
- Ensure that you have granted microphone permissions in Windows Settings.
- Double-check that your headset is selected as the default input device. ADITYA will automatically attempt to swap and recover default audio pipelines if switched.

## 2. Where are the log files located?
- On Windows: `%APPDATA%/Roaming/ADITYA/logs/` (e.g., `electron.log` and `launcher.log`).

## 3. How do I change my Gemini API Key?
- Open the `.env` file in the installation directory and update the `GEMINI_API_KEY` field.

## 4. How do I configure custom hotkeys?
- The default hotkey is `Ctrl+Alt+J`. You can configure shortcuts inside `backend/core/keyboard_listener.py` or through the settings panel.
