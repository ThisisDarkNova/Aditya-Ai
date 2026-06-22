@echo off
setlocal
echo ==============================================
echo 🌌 VESPERA -- System Update Utility
echo ==============================================
echo Fetching latest updates from GitHub...
git fetch origin
git pull origin main

echo Updating Backend Dependencies...
if exist "packages\umbracore\requirements.txt" (
    pip install -r packages\umbracore\requirements.txt
) else (
    echo [WARNING] packages\umbracore\requirements.txt not found!
)

echo.
echo Updating Client Dependencies...
if exist "apps\wraithglass\package.json" (
    npm install --prefix apps\wraithglass
) else (
    echo [WARNING] apps\wraithglass\package.json not found!
)

echo.
echo 🎉 Update Complete! VESPERA is now running the latest version.
pause
endlocal
