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
if exist "CognitiveCore\requirements.txt" (
    pip install -r CognitiveCore\requirements.txt
) else (
    echo [WARNING] CognitiveCore\requirements.txt not found!
)

echo.
echo Updating Client Dependencies...
if exist "VisionInterface\package.json" (
    npm install --prefix client
) else (
    echo [WARNING] VisionInterface\package.json not found!
)

echo.
echo 🎉 Update Complete! ADITYA is now running the latest version.
pause
endlocal
