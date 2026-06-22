# VESPERA OS Packaging & Deployment

Follow these steps to compile and package the sentient cognitive OS into a standalone installer on Windows.

## 1. Compile Backend Binary

First compile the Python daemon using PyInstaller:

```bash
cd packages/umbracore
pip install -r requirements.txt
pip install pyinstaller
pyinstaller VesperaCore.spec
```

This generates a standalone executable at `packages/umbracore/dist/VesperaCore.exe`.

## 2. Build Frontend UI Assets

Navigate to the `apps/wraithglass/` directory and build the React/Vite/Electron production code:

```bash
cd apps/wraithglass
npm install
npm run build
```

This compiles static assets into `apps/wraithglass/dist/`.

## 3. Generate Standalone Setup Executable

Compile the final Electron installer using electron-builder:

```bash
cd apps/wraithglass
npm run package
```

The output setup installer will be output to `apps/wraithglass/release/VESPERA Setup 1.0.0.exe`.
This setup includes the compiled Python backend bundled inside as an `extraResource` and extracts it to run alongside the Electron front-end dynamically.
