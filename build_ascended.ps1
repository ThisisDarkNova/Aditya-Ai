# Vespera Master Build Script (build_ascended.ps1)
# Compiles all 5 pillars of the ecosystem into a final Release folder.

$ErrorActionPreference = "Stop"
$MonorepoRoot = "C:\Users\DarkNova\Code\Aether-1.0.0"
$ReleaseDir = "$MonorepoRoot\Release"

Write-Host "==========================================" -ForegroundColor Cyan
Write-Host "🚀 ASCENSION: PRODUCTION BUILD INITIATED" -ForegroundColor Cyan
Write-Host "==========================================" -ForegroundColor Cyan

# 1. Prepare Release Directory
if (Test-Path $ReleaseDir) {
    # Remove files but ignore errors on locked files (like *.old)
    Get-ChildItem $ReleaseDir | ForEach-Object {
        try { Remove-Item -Recurse -Force $_.FullName -ErrorAction SilentlyContinue } catch {}
    }
} else {
    New-Item -ItemType Directory -Force -Path $ReleaseDir | Out-Null
}

# 2. Build aegis-cast (OBS Overlays)
Write-Host "`n[1/4] Building aegis-cast (Vite)..." -ForegroundColor Yellow
Set-Location "$MonorepoRoot\aegis-cast"
npm install --silent
npm run build
New-Item -ItemType Directory -Force -Path "$ReleaseDir\aegis-cast_Build" | Out-Null
Copy-Item -Path "$MonorepoRoot\aegis-cast\dist\*" -Destination "$ReleaseDir\aegis-cast_Build" -Recurse -Force
Write-Host "✅ aegis-cast compiled successfully." -ForegroundColor Green

# 3. Build VS Code Extension
Write-Host "`n[2/4] Building VS Code Extension (TypeScript)..." -ForegroundColor Yellow
Set-Location "$MonorepoRoot\VSCodeExtension"
npm install --silent
npm run compile
npx -y @vscode/vsce package -o "$ReleaseDir\vespera-marginalia-1.0.0.vsix" --no-dependencies
Write-Host "✅ VS Code Extension packaged successfully." -ForegroundColor Green

# 4. Build umbracore (Python)
Write-Host "`n[3/4] Compiling umbracore Core and Daemons (PyInstaller)..." -ForegroundColor Yellow
Set-Location "$MonorepoRoot\umbracore"
# Use virtual environment python to run PyInstaller
& .venv\Scripts\pyinstaller --onefile --noconsole TheDailyHub\MorningBriefing.py --distpath "$ReleaseDir\Daemons" --clean
& .venv\Scripts\pyinstaller --onefile --noconsole V12Cylinders\TheChauffeur.py --distpath "$ReleaseDir\Daemons" --clean
& .venv\Scripts\pyinstaller VesperaCore.spec --distpath "$ReleaseDir" --clean
Write-Host "✅ Python Core & Daemons compiled successfully." -ForegroundColor Green

# 5. Build lumen-desk (Next.js)
Write-Host "`n[4/4] Building Web Portal (Next.js)..." -ForegroundColor Yellow
Set-Location "$MonorepoRoot\lumen-desk"
npm run build
New-Item -ItemType Directory -Force -Path "$ReleaseDir\lumen-desk_Build" | Out-Null
Copy-Item -Path "$MonorepoRoot\lumen-desk\.next\*" -Destination "$ReleaseDir\lumen-desk_Build" -Recurse -Force
Write-Host "✅ Next.js Production Build complete." -ForegroundColor Green

# 6. Finalization
Set-Location $MonorepoRoot
Write-Host "`n==========================================" -ForegroundColor Cyan
Write-Host "🏆 ASCENSION COMPLETE" -ForegroundColor Green
Write-Host "All assets compiled securely to $ReleaseDir." -ForegroundColor Cyan
Write-Host "==========================================" -ForegroundColor Cyan
