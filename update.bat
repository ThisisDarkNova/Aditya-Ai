@echo off
setlocal
echo ==============================================
echo 🌌 ADITYA -- System Update Utility
echo ==============================================
echo Fetching latest updates from GitHub...
git fetch origin
git pull origin main

echo.
echo Updating Backend Dependencies...
if exist "backend\requirements.txt" (
    pip install -r backend\requirements.txt
) else (
    echo [WARNING] backend\requirements.txt not found!
)

echo.
echo Updating Client Dependencies...
if exist "client\package.json" (
    npm install --prefix client
) else (
    echo [WARNING] client\package.json not found!
)

echo.
echo 🎉 Update Complete! ADITYA is now running the latest version.
pause
endlocal
