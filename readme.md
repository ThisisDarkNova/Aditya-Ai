# 🌌 ADITYA — Sentient Cognitive Operating System

<div align="center">
  <img src="assets/banner.svg" width="100%" max-width="800" alt="ADITYA Animated Banner" />
  <p><em>An animated, high-performance, dark-glassmorphism AI companion & automation engine for Windows.</em></p>

  [![CI Code Quality](https://img.shields.io/badge/CI--Code--Quality-passing-22c55e?style=flat-square&logo=github-actions&logoColor=white)](#)
  [![Client Quality Checks](https://img.shields.io/badge/Client--Quality--Checks-passing-22c55e?style=flat-square&logo=github-actions&logoColor=white)](#)
  [![Security Analysis](https://img.shields.io/badge/Security--Analysis-secured-22c55e?style=flat-square&logo=github-actions&logoColor=white)](#)
  [![License](https://img.shields.io/github/license/DarkNova/aditya-os?style=flat-square&color=3382f6)](LICENSE)
  [![Electron App Version](https://img.shields.io/badge/electron-v33.4.11-blue.svg?style=flat-square&logo=electron&logoColor=white)](client/package.json)
  [![Python Backend Version](https://img.shields.io/badge/python-3.12-yellow.svg?style=flat-square&logo=python&logoColor=white)](backend/requirements.txt)
</div>

---

## 🚀 Key Highlights & Design Aesthetics

ADITYA is built around a custom dark-glassmorphism visual theme tailored to premium desktop environments:

*   **Liquid SVG Turbulence Orb**: A floating 3D voice visualizer reacting with organic fluid movements, changing color instantly based on Aditya's emotional state (Listening = Royal Blue, Thinking = Violet Purple, Speaking = Vibrant Green, Gaming Mode = Vivid Orange).
*   **Dynamic HSL Particle Canvas**: A GPU-accelerated canvas background spawning floating neon particle clouds that rotate and scale to match the active user profile persona.
*   **Zero-Latency Verbal Engine**: Optimized for fast-paced, full-duplex conversations. Built-in filler response systems ensure the AI begins speaking within milliseconds while tools execute asynchronously in the background.

---
---

## 🖼️ Premium Visual Interfaces

Here are actual previews of the premium glassmorphism interfaces loaded directly in the Electron shell:

### 🏠 Main Mission Control Dashboard
Shows your active persona widgets, telemetry data, streaks, and context-specific AI summaries.
<img src="assets/premium_home_dashboard.png" width="100%" alt="Aditya Home Dashboard" style="border-radius: 8px; border: 1px solid #333;" />

### ⚙️ Premium Settings Panel
Allows configuring theme preferences, hotkeys, microphone levels, and active personas.
<img src="assets/premium_settings_panel.png" width="100%" alt="Aditya Settings" style="border-radius: 8px; border: 1px solid #333;" />
## 🛠️ Decoupled Architecture

ADITYA features a multi-process runtime environment designed for resilience and low overhead:

*   **Frontend Dashboard (React + Vite)**: Hosted within a lightweight Electron window, utilizing custom glassmorphism styles, Framer Motion transitions, and global error boundaries.
*   **Cognitive Core Backend (Python Engine)**: Drives the non-blocking PyAudio pipeline, manages local databases, reads the screen via Tesseract OCR, tracks system CPU/RAM telemetry, and executes custom automated skills.

---

## 🔮 Active OS Capabilities

Aditya has direct local access to interact with your computer:

| Capability | Module | Description |
|---|---|---|
| **OS Commands** | `brain.py` | Control system volume, manage screen brightness, execute media shortcuts, lock PC, sleep, restart, or shutdown. |
| **Physical Automation** | `app_opener.py` | Move the mouse pointer, perform left/right/double clicks, drag elements, type text, copy, paste, and execute keyboard shortcuts. |
| **OCR Text Targeting** | `screen_ocr.py` | Captures screen frames, processes low-contrast elements with multi-pass filters, and performs sequential word matching to click on buttons (e.g., "Class - X"). |
| **PC Optimization** | `pc_optimizer.py` | Game booster (suspends Windows Search indexers and raises process priority), deletes junk temporary caches, and displays live system metrics. |
| **Study Helpers** | `study_helper.py` | Generate Concept Notes, revision schedules, and custom quizzes directly to your local folders. |

---

## 🔧 Dev Installation & Source Run

### 1. Prerequisites
1.  **Python 3.11** or **3.12** (Ensure `python` is added to your Environment PATH).
2.  **Node.js (LTS)** (Required to build the React dashboard).
3.  **Tesseract OCR**:
    *   Download from the [Tesseract GitHub Repository](https://github.com/UB-Mannheim/tesseract/wiki).
    *   Install to standard location: `C:\Program Files\Tesseract-OCR\tesseract.exe`.

### 2. Python Environment Setup
Open a PowerShell terminal in the root directory and install dependencies:
```powershell
pip install -r requirements.txt
```

### 3. API Keys Configuration
Create a `.env` file in the project root:
```env
# Gemini API Key (Required for live audio reasoning)
GEMINI_API_KEY=your_gemini_key_here

# OpenWeather API Key (Optional)
OPENWEATHER_API_KEY=your_weather_key_here

# NewsAPI Key (Optional)
NEWS_API_KEY=your_news_key_here
```

### 4. Running the Development Build
You can run and build the workspace directly from the root directory using the unified scripts:
*   **Launch App Dev Server**:
    ```bash
    npm run dev:electron
    ```
*   **Compile Backend Binary**:
    ```bash
    npm run build:backend
    ```
*   **Package Single Setup Installer**:
    ```bash
    npm run build:electron
    ```

---

## 🛡️ Repository Health & Stability Framework

We have built a premium, production-ready environment configured for automatic validation and safety checks on GitHub:

*   **Continuous Integration & Verification**:
    *   [test.yml](file:///.github/workflows/test.yml) - Automatic execution of all 17 backend unit tests on push/PR.
    *   [lint.yml](file:///.github/workflows/lint.yml) - Enforces styling rules using Ruff and ESLint.
    *   [codeql-analysis.yml](file:///.github/workflows/codeql-analysis.yml) - Dynamic semantic security vulnerability scans.
    *   [security-scan.yml](file:///.github/workflows/security-scan.yml) - Audits python/npm dependencies for vulnerabilities using `pip-audit` & `npm audit`.
*   **Release & Community Operations**:
    *   [release.yml](file:///.github/workflows/release.yml) - Deploys packaged Electron installers automatically on version tag updates.
    *   [lock.yml](file:///.github/workflows/lock.yml) - Automatically locks stale issues and PRs to keep the boards clean.
    *   [pr-title-checker.yml](file:///.github/workflows/pr-title-checker.yml) - Enforces semantic Conventional Commits syntax on Pull Requests.
*   **Containerized Environments**:
    *   [Dockerfile](file:///Dockerfile) & [docker-compose.yml](file:///docker-compose.yml) - Multi-stage runner virtualizing backend services and executing test suites inside isolated containers.

---

## 📦 Single Executable Setup
The compiled, production-ready setup installer is located at:
*   **Setup Binary**: [ADITYA Setup 1.0.0.exe](file:///c:/Users/DarkNova/Downloads/Aether-1.0.0/client/release/ADITYA%20Setup%201.0.0.exe)