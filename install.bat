@echo off
setlocal
:: ADITYA OS - Sentient Cognitive Operating System Installer
:: Usage: Run this batch script to download and install ADITYA OS

echo ==============================================
echo 🌌 ADITYA -- Sentient Cognitive Operating System
echo ==============================================
echo Initializing secure installation pipeline...

set "REPO_OWNER=ThisisDarkNova"
set "REPO_NAME=Aditya-Ai"
set "RELEASE_VERSION=v1.0.0"
set "DOWNLOAD_URL=https://github.com/%REPO_OWNER%/%REPO_NAME%/releases/download/%RELEASE_VERSION%/ADITYA%%20Setup%%201.0.0.exe"
set "TEMP_PATH=%TEMP%\ADITYA_Setup_1.0.0.exe"

echo Downloading installer from GitHub Releases...
echo Source: %DOWNLOAD_URL%
echo Target: %TEMP_PATH%

:: Use PowerShell to handle the download over TLS 1.2/1.3
powershell -NoProfile -Command "[Net.ServicePointManager]::SecurityProtocol = [Net.SecurityProtocolType]::Tls12 -bor [Net.SecurityProtocolType]::Tls13; try { Invoke-RestMethod -Uri '%DOWNLOAD_URL%' -OutFile '%TEMP_PATH%'; Write-Host 'Download completed successfully!' -ForegroundColor Green } catch { Write-Host 'Failed to download installer.' -ForegroundColor Red; exit 1 }"
if %ERRORLEVEL% NEQ 0 (
    echo [ERROR] Failed to download installer.
    pause
    exit /b %ERRORLEVEL%
)

echo.
echo Launching ADITYA Setup...
echo Please complete the setup wizard window.
echo.

start /wait "" "%TEMP_PATH%"

if %ERRORLEVEL% EQU 0 (
    echo 🎉 ADITYA OS installed successfully!
    echo You can now run ADITYA from your desktop or start menu.
) else (
    echo [WARNING] Installer closed with exit code: %ERRORLEVEL%
)

:: Cleanup
if exist "%TEMP_PATH%" del /f /q "%TEMP_PATH%"

pause
endlocal
