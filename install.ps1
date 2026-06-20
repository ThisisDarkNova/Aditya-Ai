# ADITYA OS - Sentient Cognitive Operating System Installer
# Usage: irm "https://raw.githubusercontent.com/ThisisDarkNova/Aditya-Ai/main/install.ps1" | iex

$ErrorActionPreference = "Stop"

# Clear host and print a premium ASCII banner
Clear-Host
Write-Host "🌌 ADITYA — Sentient Cognitive Operating System" -ForegroundColor Cyan
Write-Host "==============================================" -ForegroundColor DarkGray
Write-Host "Initializing secure installation pipeline..." -ForegroundColor Gray

# Define repository specific URLs
$repoOwner = "ThisisDarkNova"
$repoName = "Aditya-Ai"
$releaseVersion = "v1.0.0"
$installerName = "ADITYA.Setup.1.0.0.exe"

# If the installer filename on GitHub Releases contains spaces, GitHub might replace spaces with dots or %20.
# The asset name uploaded is "ADITYA Setup 1.0.0.exe" or "ADITYA Setup 1.0.0.exe".
$downloadUrl = "https://github.com/$repoOwner/$repoName/releases/download/$releaseVersion/ADITYA%20Setup%201.0.0.exe"
$tempPath = Join-Path $env:TEMP "ADITYA_Setup_1.0.0.exe"

Write-Host "Downloading installer from GitHub Releases..." -ForegroundColor Yellow
Write-Host "Source: $downloadUrl" -ForegroundColor DarkGray
Write-Host "Target: $tempPath" -ForegroundColor DarkGray

try {
    # Download the installer file with progress bar
    Invoke-RestMethod -Uri $downloadUrl -OutFile $tempPath
    Write-Host "✅ Download completed successfully!" -ForegroundColor Green
}
catch {
    Write-Host "❌ Failed to download installer: $_" -ForegroundColor Red
    return
}

# Run the installer
Write-Host "Launching ADITYA Setup..." -ForegroundColor Cyan
Write-Host "Please complete the setup wizard window." -ForegroundColor Gray

try {
    # Start the installer process and wait for it to complete
    $process = Start-Process -FilePath $tempPath -Wait -PassThru
    
    if ($process.ExitCode -eq 0) {
        Write-Host "🎉 ADITYA OS installed successfully!" -ForegroundColor Green
        Write-Host "You can now run ADITYA from your desktop or start menu." -ForegroundColor Cyan
    } else {
        Write-Host "⚠️ Installer closed with exit code: $($process.ExitCode)" -ForegroundColor Yellow
    }
}
catch {
    Write-Host "❌ Failed to launch installer: $_" -ForegroundColor Red
}
finally {
    # Clean up the downloaded installer file
    if (Test-Path $tempPath) {
        Remove-Item $tempPath -Force
    }
}
