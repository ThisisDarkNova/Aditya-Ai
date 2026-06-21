const { app, BrowserWindow, ipcMain, dialog, Tray, Menu, nativeImage, session, desktopCapturer, screen } = require('electron');
const path = require('path');
const fs = require('fs');
const os = require('os');
const { spawn, execSync } = require('child_process');
const http = require('http');

const startupStartTime = Date.now();
const isStartup = process.argv.includes('--startup');

let mainWindow;
let tray = null;
let backendProcess = null;
let isBackendReady = false;
let logFilePath = null;
let logStream = null;

function logLine(stream, level, msg) {
    const stamped = `[${new Date().toISOString()}] [${level}] ${msg}\n`;
    try { process.stdout.write(stamped); } catch (_) {}
    if (logStream && !logStream.destroyed) {
        try { logStream.write(stamped); } catch (_) {}
    }
}

function setupLogging() {
    try {
        const userData = app.getPath('userData');
        fs.mkdirSync(userData, { recursive: true });
        logFilePath = path.join(userData, 'launcher.log');
        logStream = fs.createWriteStream(logFilePath, { flags: 'a' });
        logLine(null, 'INFO', `Launcher log opened at ${logFilePath}`);
        logLine(null, 'INFO', `app.isPackaged=${app.isPackaged} resourcesPath=${process.resourcesPath || ''}`);
    } catch (e) {
        logLine(null, 'WARN', `Could not open launcher.log: ${e.message}`);
    }
}

function killStaleAdityaProcesses() {
    // If a previous ADITYA / AdityaCore is still around holding port 7865,
    // our new instance will fail to bind. Clean them up first.
    const names = ['AdityaCore.exe', 'ADITYA.exe'];
    for (const name of names) {
        try {
            const out = execSync(`tasklist /FI "IMAGENAME eq ${name}" /FO CSV /NH`, { 
                stdio: ['ignore', 'pipe', 'ignore'],
                windowsHide: true 
            }).toString();
            const pids = [];
            for (const line of out.split(/\r?\n/)) {
                const m = line.match(/^"([^"]+)","(\d+)"/);
                if (m && m[1].toLowerCase() === name.toLowerCase()) pids.push(m[2]);
            }
            for (const pid of pids) {
                if (parseInt(pid, 10) === process.pid) continue;
                try {
                    execSync(`taskkill /F /PID ${pid}`, { 
                        stdio: 'ignore',
                        windowsHide: true 
                    });
                    logLine(null, 'INFO', `Killed stale ${name} (PID ${pid})`);
                } catch (_) {}
            }
        } catch (_) {}
    }
}

// Determine absolute paths depending on development mode
const isDev = !app.isPackaged || process.argv.includes('--dev');

// Simple file logger so we can debug packaged-app issues
const LOG_DIR = process.env.ADITYA_LOG_DIR
    || (process.platform === 'win32'
        ? path.join(process.env.APPDATA || os.homedir(), 'ADITYA', 'logs')
        : path.join(os.tmpdir(), 'aditya-logs'));
try { fs.mkdirSync(LOG_DIR, { recursive: true }); } catch (_) {}
const LOG_FILE = path.join(LOG_DIR, 'electron.log');
function logToFile(...args) {
    const line = `[${new Date().toISOString()}] ${args.map(a => typeof a === 'string' ? a : JSON.stringify(a)).join(' ')}\n`;
    try { fs.appendFileSync(LOG_FILE, line); } catch (_) {}
    console.log(...args);
}
process.on('uncaughtException', (err) => {
    logToFile('[FATAL] uncaughtException:', err && err.stack || err);
});
logToFile(`[Electron] Starting. isDev=${isDev} isPackaged=${app.isPackaged} resourcesPath=${process.resourcesPath} logFile=${LOG_FILE}`);

function findBackendExe() {
    const projectRoot = path.resolve(__dirname, '..');
    const candidates = [
        path.join(process.resourcesPath || '', 'AdityaCore.exe'),
        path.join(projectRoot, 'backend', 'dist', 'AdityaCore.exe'),
        path.join(projectRoot, 'backend', 'AdityaCore.exe'),
        path.join(projectRoot, 'client', 'release', 'win-unpacked', 'resources', 'AdityaCore.exe'),
    ];
    for (const candidate of candidates) {
        if (candidate && fs.existsSync(candidate)) {
            return candidate;
        }
    }
    return null;
}

function startBackend() {
    let cmd, args, cwd;

    if (isDev) {
        // In development, spawn the python script directly
        const pythonScript = path.resolve(__dirname, '../backend/main.py');
        if (!fs.existsSync(pythonScript)) {
            const exePath = findBackendExe();
            if (exePath) {
                logLine(null, 'INFO', `[Dev] Python script missing, falling back to compiled engine: ${exePath}`);
                cmd = exePath;
                args = ['--no-ui'];
                cwd = path.dirname(exePath);
            } else {
                logLine(null, 'ERROR', `Python script not found at: ${pythonScript} and no compiled fallback.`);
                dialog.showErrorBox(
                    'ADITYA Backend Error',
                    `Python script not found at: ${pythonScript}\nAnd no compiled AdityaCore.exe fallback was found.`
                );
                app.quit();
                return;
            }
        } else {
            logLine(null, 'INFO', `[Dev] Starting Python Backend script: ${pythonScript}`);
            cmd = 'python';
            args = [pythonScript, '--no-ui'];
            cwd = path.dirname(pythonScript);
        }
    } else {
        // In production, spawn the bundled AdityaCore.exe from resources folder (packaged via electron-builder extraResources)
        let exePath = path.join(process.resourcesPath, 'AdityaCore.exe');
        if (!fs.existsSync(exePath)) {
            const fallback = findBackendExe();
            if (fallback) {
                logLine(null, 'WARN', `[Prod] AdityaCore.exe missing at resources path, using fallback: ${fallback}`);
                exePath = fallback;
            }
        }
        if (!fs.existsSync(exePath)) {
            logLine(null, 'ERROR', `AdityaCore.exe not found. resourcesPath=${process.resourcesPath} isPackaged=${app.isPackaged}`);
            dialog.showErrorBox(
                'ADITYA Backend Error',
                `AdityaCore.exe not found. Looked at:\n${path.join(process.resourcesPath, 'AdityaCore.exe')}\nprocess.resourcesPath: ${process.resourcesPath}\napp.isPackaged: ${app.isPackaged}`
            );
            app.quit();
            return;
        }
        logLine(null, 'INFO', `[Prod] Starting Python Backend EXE: ${exePath}`);
        cmd = exePath;
        args = ['--no-ui'];
        cwd = path.dirname(exePath);
    }

    backendProcess = spawn(cmd, args, {
        cwd: cwd,
        windowsHide: true,
        stdio: 'pipe' // pipe instead of inherit to avoid console allocation issues
    });

    logLine(null, 'INFO', `Spawned backend (pid=${backendProcess.pid})`);

    backendProcess.stdout.on('data', (data) => {
        const text = data.toString();
        text.split(/\r?\n/).filter(Boolean).forEach((line) => logLine(null, 'BACKEND', line));
    });
    backendProcess.stderr.on('data', (data) => {
        const text = data.toString();
        text.split(/\r?\n/).filter(Boolean).forEach((line) => logLine(null, 'BACKEND-ERR', line));
    });

    backendProcess.on('error', (err) => {
        logLine(null, 'ERROR', `Failed to start Python backend: ${err.message}`);
        if (!isBackendReady) {
            dialog.showErrorBox(
                'ADITYA Backend Error',
                `Failed to start the background engine: ${err.message}\n\nSee: ${logFilePath || 'launcher.log'}`
            );
            app.quit();
        }
    });

    backendProcess.on('exit', (code, signal) => {
        logLine(null, 'WARN', `Backend exited code=${code} signal=${signal}`);
        if (!isBackendReady && code !== 0 && code !== null) {
            dialog.showErrorBox(
                'ADITYA Backend Exited',
                `The background engine exited unexpectedly with code ${code}.\n\nSee: ${logFilePath || 'launcher.log'}`
            );
            app.quit();
        }
    });
}

function checkBackendReady(callback) {
    const req = http.request({
        host: '127.0.0.1',
        port: 7865,
        path: '/api/status',
        method: 'GET',
        timeout: 800
    }, (res) => {
        if (res.statusCode === 200) {
            callback(true);
        } else {
            callback(false);
        }
    });

    req.on('error', () => {
        callback(false);
    });

    req.on('timeout', () => {
        req.destroy();
        callback(false);
    });

    req.end();
}

function loadMainApp() {
    if (isDev) {
        // Dev: load Vite dev server (HMR); backend still serves /api/*
        logLine(null, 'INFO', 'Dev: loading Vite dev server at http://localhost:5173');
        mainWindow.loadURL('http://localhost:5173');
        mainWindow.webContents.openDevTools();
        return;
    }

    // Production: load the React UI directly from the packaged app (built `dist/`).
    // The React frontend communicates with the AdityaCore backend over HTTP API calls.
    const uiPath = path.join(__dirname, 'dist', 'index.html');
    logLine(null, 'INFO', `Loading UI from: ${uiPath}`);
    mainWindow.loadFile(uiPath);
}

function pollBackend(startTime, timeoutMs) {
    if (isBackendReady) return;

    // Check if app has been closed during polling
    if (!mainWindow) return;

    checkBackendReady((ready) => {
        if (ready) {
            isBackendReady = true;
            const bootDuration = Date.now() - startupStartTime;
            logLine(null, 'INFO', `Backend is ready. Loading main app. Startup took ${bootDuration}ms.`);
            logToFile(`[Telemetry] Startup finished in ${bootDuration}ms`);
            loadMainApp();
        } else {
            const elapsed = Date.now() - startTime;
            if (elapsed > timeoutMs) {
                logLine(null, 'ERROR', `Backend ready polling timed out after ${timeoutMs}ms`);
                dialog.showErrorBox(
                    'ADITYA Startup Timeout',
                    `The background cognitive engine failed to start within ${Math.round(timeoutMs / 1000)} seconds.\n\nSee: ${logFilePath || 'launcher.log'}`
                );
                app.quit();
            } else {
                setTimeout(() => pollBackend(startTime, timeoutMs), 500);
            }
        }
    });
}

function createWindow() {
    mainWindow = new BrowserWindow({
        width: 1280,
        height: 800,
        minWidth: 900,
        minHeight: 600,
        title: "ADITYA",
        show: !isStartup,
        transparent: true,      // Floating Glass UI
        frame: false,           // No window borders
        alwaysOnTop: true,      // Absolute priority
        hasShadow: false,
        backgroundColor: '#00000000', // Fully transparent background
        webPreferences: {
            preload: path.join(__dirname, 'preload.cjs'),
            contextIsolation: true,
            nodeIntegration: false,
        },
    });

    // Phantom Mode: Screen Capture Detection
    setInterval(async () => {
        try {
            const sources = await desktopCapturer.getSources({ types: ['screen', 'window'] });
            // Very basic mock check for Discord/OBS capturing
            // Electron's desktopCapturer isn't perfect for reverse-detecting WHO is recording,
            // but we can simulate the "Phantom Mode" opacity drop.
            // In a production C++ addon, we would hook D3D11 to see active capture sessions.
            let isBeingCaptured = false;
            
            if (isBeingCaptured && mainWindow.getOpacity() !== 0) {
                mainWindow.setOpacity(0.0);
                console.log("[Phantom Mode] Screen capture detected. Turning invisible.");
            } else if (!isBeingCaptured && mainWindow.getOpacity() === 0) {
                mainWindow.setOpacity(1.0);
            }
        } catch (err) {
            console.error(err);
        }
    }, 5000);

    // Expose IPC for Phantom Engine commands
    ipcMain.on('engine-command', (event, command) => {
        console.log('Received command from Engine:', command);
    });
    
    // Omni-Screen Teleportation handler
    ipcMain.on('omni-screen:teleport', () => {
        const point = screen.getCursorScreenPoint();
        const display = screen.getDisplayNearestPoint(point);
        mainWindow.setBounds(display.workArea);
        logToFile(`[Omni-Screen] Teleported UI to display: ${display.id}`);
    });

    // Redirect renderer console messages to main process log with level indicators
    mainWindow.webContents.on('console-message', (event, level, message, line, sourceId) => {
        const levelNames = ['DEBUG', 'INFO', 'WARN', 'ERROR'];
        const lvlName = levelNames[level] || 'INFO';
        logLine(null, lvlName, `[Renderer] ${message} (at ${sourceId}:${line})`);
        
        // Log errors/warnings specifically to the central file log
        if (level >= 2) {
            logToFile(`[Renderer-${lvlName}] ${message} (at ${sourceId}:${line})`);
        }
    });

    // Register safe atomic file writer channel handle
    ipcMain.handle('fs:safe-write', async (event, { filePath, content }) => {
        try {
            const tempPath = filePath + `.tmp_${process.pid}`;
            // Write to temporary buffer
            fs.writeFileSync(tempPath, content, 'utf8');
            // Safely swap files atomically
            if (fs.existsSync(filePath)) {
                fs.unlinkSync(filePath);
            }
            fs.renameSync(tempPath, filePath);
            logToFile(`[IPC-FS] Safely wrote file atomically: ${filePath}`);
            return { success: true };
        } catch (err) {
            logToFile(`[IPC-FS-ERROR] Safe write operation failed on ${filePath}: ${err.message}`);
            return { success: false, error: err.message };
        }
    });

    ipcMain.handle('aditya:openApp', async (event, appName) => {
        logToFile(`[IPC-API] Request to open app: ${appName}`);
        return new Promise((resolve) => {
            const encoded = encodeURIComponent(appName);
            http.get(`http://127.0.0.1:7865/api/focus-app?name=${encoded}`, (res) => {
                let data = '';
                res.on('data', chunk => { data += chunk; });
                res.on('end', () => {
                    try {
                        const result = JSON.parse(data);
                        if (result.error) {
                            logToFile(`[IPC-API] Error resolving: ${result.error}`);
                            resolve({ success: false, error: result.error });
                            return;
                        }
                        if (result.focused) {
                            logToFile(`[IPC-API] App ${result.name} is already running and has been focused.`);
                            resolve({ success: true, message: `Switched to running app: ${result.name}` });
                            return;
                        }

                        // App is not running. Launch it directly.
                        const targetPath = result.path;
                        // Validate path
                        if (!fs.existsSync(targetPath)) {
                            resolve({ success: false, error: `Target path does not exist: ${targetPath}` });
                            return;
                        }
                        
                        logToFile(`[IPC-API] Launching executable directly: ${targetPath}`);
                        const child = spawn(targetPath, [], {
                            detached: true,
                            stdio: 'ignore',
                            windowsHide: false
                        });
                        child.unref();

                        resolve({ success: true, message: `Launched app: ${result.name}` });
                    } catch (e) {
                        resolve({ success: false, error: e.message });
                    }
                });
            }).on('error', (err) => {
                logToFile(`[IPC-API] Failed to contact backend resolver: ${err.message}`);
                resolve({ success: false, error: err.message });
            });
        });
    });

    // Remove the default menu
    mainWindow.setMenu(null);

    // Map any request to localhost -> 127.0.0.1 so the React app's hardcoded
    // `http://localhost:7865` API base matches the origin it was loaded from
    // (`http://127.0.0.1:7865`). Without this, fetch() can hang or be blocked
    // by the browser's mixed-content / private-network heuristics on Windows.
    try {
        session.defaultSession.webRequest.onBeforeRequest(
            { urls: ['http://localhost:7865/*', 'http://localhost/*'] },
            (details, callback) => {
                const redirected = details.url.replace(
                    /^http:\/\/localhost(?=[:/]|$)/,
                    'http://127.0.0.1'
                );
                if (redirected !== details.url) {
                    logLine(null, 'INFO', `Redirect: ${details.url} -> ${redirected}`);
                }
                callback({ redirectURL: redirected });
            }
        );
    } catch (e) {
        logLine(null, 'WARN', `Could not install localhost redirect: ${e.message}`);
    }

    // Show loading screen first
    mainWindow.loadFile(path.join(__dirname, 'loading.html'));

    mainWindow.on('close', (event) => {
        if (!app.isQuiting) {
            event.preventDefault();
            mainWindow.hide();
        }
        return false;
    });

    mainWindow.on('closed', () => {
        mainWindow = null;
    });

    // Setup Tray
    const iconPath = path.join(__dirname, 'dist', 'tray_icon.png');
    tray = new Tray(nativeImage.createFromPath(iconPath));
    const contextMenu = Menu.buildFromTemplate([
        { label: 'Show Aditya', click: () => { mainWindow.show(); mainWindow.focus(); } },
        { type: 'separator' },
        { label: 'Quit', click: () => { app.isQuiting = true; app.quit(); } }
    ]);
    tray.setToolTip('ADITYA Cognitive Core');
    tray.setContextMenu(contextMenu);
    tray.on('click', () => {
        mainWindow.show();
        mainWindow.focus();
    });

    // Start polling backend
    pollBackend(Date.now(), 90000); // 90s to allow PyInstaller EXE to self-extract and boot
}

function startBackendWatchdog() {
    // If AdityaCore dies after we thought it was ready, surface a dialog and quit.
    setInterval(() => {
        if (!backendProcess) return;
        if (backendProcess.killed || backendProcess.exitCode !== null) {
            logLine(null, 'ERROR', `Backend process is no longer alive (exitCode=${backendProcess.exitCode})`);
            if (backendProcess.exitCode !== 0 && backendProcess.exitCode !== null) {
                if (mainWindow && !mainWindow.isDestroyed()) {
                    dialog.showErrorBox(
                        'ADITYA Backend Lost',
                        `The background engine stopped responding.\n\nSee: ${logFilePath || 'launcher.log'}`
                    );
                }
            }
            app.isQuiting = true;
            app.quit();
        }
    }, 5000);
}

app.whenReady().then(() => {
    setupLogging();
    killStaleAdityaProcesses();

    // Start with Windows automatically
    app.setLoginItemSettings({
        openAtLogin: true,
        path: process.execPath,
        args: []
    });

    startBackend();
    startBackendWatchdog();
    createWindow();
});

app.on('window-all-closed', () => {
    // Do not quit when windows are closed, just stay in tray
    if (process.platform !== 'darwin') {
        // app.quit(); // Disabled to allow tray mode
    }
});

app.on('before-quit', () => {
    if (logStream && !logStream.destroyed) {
        try { logStream.end(); } catch (_) {}
    }
    if (backendProcess) {
        try { backendProcess.kill(); } catch (_) {}
    }
});

app.on('activate', () => {
    if (BrowserWindow.getAllWindows().length === 0) {
        createWindow();
    }
});

