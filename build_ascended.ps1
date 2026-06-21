# Aditya Master Build Script (build_ascended.ps1)
# Compiles all 5 pillars of the ecosystem into a final Release folder.

$ErrorActionPreference = "Stop"
$MonorepoRoot = "C:\Users\DarkNova\Code\Aether-1.0.0"
$ReleaseDir = "$MonorepoRoot\Release"

Write-Host "==========================================" -ForegroundColor Cyan
Write-Host "🚀 ASCENSION: PRODUCTION BUILD INITIATED" -ForegroundColor Cyan
Write-Host "==========================================" -ForegroundColor Cyan

# 1. Prepare Release Directory
if (Test-Path $ReleaseDir) { Remove-Item -Recurse -Force $ReleaseDir }
New-Item -ItemType Directory -Force -Path $ReleaseDir | Out-Null

# 2. Build StreamWidgets (OBS Overlays)
Write-Host "`n[1/4] Building StreamWidgets (Vite)..." -ForegroundColor Yellow
Set-Location "$MonorepoRoot\StreamWidgets"
npm install --silent
npm run build
New-Item -ItemType Directory -Force -Path "$ReleaseDir\StreamWidgets_Build" | Out-Null
Copy-Item -Path "$MonorepoRoot\StreamWidgets\dist\*" -Destination "$ReleaseDir\StreamWidgets_Build" -Recurse -Force
Write-Host "✅ StreamWidgets compiled successfully." -ForegroundColor Green

# 3. Build VS Code Extension
Write-Host "`n[2/4] Building VS Code Extension (TypeScript)..." -ForegroundColor Yellow
Set-Location "$MonorepoRoot\VSCodeExtension"
npm install --silent
npm run compile
npx -y @vscode/vsce package -o "$ReleaseDir\aditya-ghost-writer-1.0.0.vsix" --no-dependencies
Write-Host "✅ VS Code Extension packaged successfully." -ForegroundColor Green

# 4. Build PhantomEngine (Python)
Write-Host "`n[3/4] Compiling PhantomEngine Core and Daemons (PyInstaller)..." -ForegroundColor Yellow
Set-Location "$MonorepoRoot\PhantomEngine"
# Use virtual environment python to run PyInstaller
& .venv\Scripts\pyinstaller --onefile --noconsole TheDailyHub\MorningBriefing.py --distpath "$ReleaseDir\Daemons" --clean
& .venv\Scripts\pyinstaller --onefile --noconsole V12Cylinders\TheChauffeur.py --distpath "$ReleaseDir\Daemons" --clean
& .venv\Scripts\pyinstaller AdityaCore.spec --distpath "$ReleaseDir" --clean
Write-Host "✅ Python Core & Daemons compiled successfully." -ForegroundColor Green

# 5. Build AdityaWeb (Next.js)
Write-Host "`n[4/4] Building Web Portal (Next.js)..." -ForegroundColor Yellow
Set-Location "$MonorepoRoot\AdityaWeb"
npm run build
New-Item -ItemType Directory -Force -Path "$ReleaseDir\AdityaWeb_Build" | Out-Null
Copy-Item -Path "$MonorepoRoot\AdityaWeb\.next\*" -Destination "$ReleaseDir\AdityaWeb_Build" -Recurse -Force
Write-Host "✅ Next.js Production Build complete." -ForegroundColor Green

# 6. Finalization
Set-Location $MonorepoRoot
Write-Host "`n==========================================" -ForegroundColor Cyan
Write-Host "🏆 ASCENSION COMPLETE" -ForegroundColor Green
Write-Host "All assets compiled securely to $ReleaseDir." -ForegroundColor Cyan
Write-Host "==========================================" -ForegroundColor Cyan
