@echo off
setlocal
echo ==============================================
echo 🌌 ADITYA -- System Repair and Diagnostics
echo ==============================================
echo.
echo [1/4] Clearing Python __pycache__ directories...
for /d /r . %%d in (__pycache__) do @if exist "%%d" rd /s /q "%%d"
echo [OK] Python cache cleared.

echo.
echo [2/4] Clearing Vite/NPM caches...
if exist "client\node_modules\.vite" rd /s /q "client\node_modules\.vite"
call npm cache clean --force --prefix client
echo [OK] NPM cache cleared.

echo.
echo [3/4] Reinstalling Python Dependencies (Force)...
if exist "backend\requirements.txt" (
    pip install --upgrade --force-reinstall -r backend\requirements.txt
)

echo.
echo [4/4] Reinstalling Node Dependencies...
if exist "client\node_modules" rd /s /q "client\node_modules"
if exist "client\package-lock.json" del /f /q "client\package-lock.json"
call npm install --prefix client

echo.
echo 🎉 Repair Complete! All caches cleared and dependencies rebuilt.
pause
endlocal
