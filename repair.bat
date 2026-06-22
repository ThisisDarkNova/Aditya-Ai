@echo off
setlocal
echo ==============================================
echo 🌌 VESPERA -- System Repair and Diagnostics
echo ==============================================
echo.
echo [1/4] Clearing Python __pycache__ directories...
for /d /r . %%d in (__pycache__) do @if exist "%%d" rd /s /q "%%d"
echo [OK] Python cache cleared.

echo.
echo [2/4] Clearing Vite/NPM caches...
if exist "apps\wraithglass\node_modules\.vite" rd /s /q "apps\wraithglass\node_modules\.vite"
call npm cache clean --force --prefix apps\wraithglass
echo [OK] NPM cache cleared.

echo.
echo [3/4] Reinstalling Python Dependencies (Force)...
if exist "packages\umbracore\requirements.txt" (
    pip install --upgrade --force-reinstall -r packages\umbracore\requirements.txt
)

echo.
echo [4/4] Reinstalling Node Dependencies...
if exist "apps\wraithglass\node_modules" rd /s /q "apps\wraithglass\node_modules"
if exist "apps\wraithglass\package-lock.json" del /f /q "apps\wraithglass\package-lock.json"
call npm install --prefix apps\wraithglass

echo.
echo 🎉 Repair Complete! All caches cleared and dependencies rebuilt.
pause
endlocal
