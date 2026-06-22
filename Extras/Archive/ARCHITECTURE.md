# VESPERA OS Architecture Design

VESPERA OS features a highly decoupled, multi-process architecture to maximize system performance and UI responsiveness.

## Components Map

```mermaid
graph TD
    A[Electron Frontend Shell] <-->|HTTP / WebSocket| B[FastAPI Backend Daemon]
    B <--> C[PyAudio Voice Stream]
    B <--> D[Tesseract OCR Monitor]
    B <--> E[Gaming Monitor Process]
    B <--> F[Local JSON Database]
```

### 1. Electron Frontend
* Tech Stack: React, Vite, Framer Motion, HSL particles canvas.
* Role: Render the dark-glassmorphism dashboard, display active stats, system metrics, and cognitive memory graphs.

### 2. Python Backend Core
* Tech Stack: Python 3.12, PyAudio, fastapi, uvicorn.
* Role: Drives wake-word listening, handles Tesseract OCR queries, manages the local database (`memory.json`), and updates processes dynamically.
