# VESPERA OS - Sentient Cognitive Operating System Installer
# Usage: irm "https://raw.githubusercontent.com/ThisisDarkNova/Vespera-Ai/main/install.ps1" | iex

$ErrorActionPreference = "Stop"

# Force TLS 1.2 & TLS 1.3 protocol compliance for GitHub connections
[Net.ServicePointManager]::SecurityProtocol = [Net.SecurityProtocolType]::Tls12 -bor [Net.SecurityProtocolType]::Tls13


# Clear host and print a premium ASCII banner
Clear-Host
Write-Host "🌌 VESPERA — Sentient Cognitive Operating System" -ForegroundColor Cyan
Write-Host "==============================================" -ForegroundColor DarkGray
Write-Host "Initializing secure installation pipeline..." -ForegroundColor Gray

# Define repository specific URLs
$repoOwner = "ThisisDarkNova"
$repoName = "Vespera-Ai"
$releaseVersion = "v1.0.0"
$installerName = "VESPERA.Setup.1.0.0.exe"

# If the installer filename on GitHub Releases contains spaces, GitHub might replace spaces with dots or %20.
# The asset name uploaded is "VESPERA Setup 1.0.0.exe" or "VESPERA Setup 1.0.0.exe".
$downloadUrl = "https://github.com/$repoOwner/$repoName/releases/download/$releaseVersion/VESPERA%20Setup%201.0.0.exe"
$tempPath = Join-Path $env:TEMP "VESPERA_Setup_1.0.0.exe"

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
Write-Host "Launching VESPERA Setup..." -ForegroundColor Cyan
Write-Host "Please complete the setup wizard window." -ForegroundColor Gray

try {
    # Start the installer process and wait for it to complete
    $process = Start-Process -FilePath $tempPath -Wait -PassThru
    
    if ($process.ExitCode -eq 0) {
        Write-Host "🎉 VESPERA OS installed successfully!" -ForegroundColor Green
        Write-Host "You can now run VESPERA from your desktop or start menu." -ForegroundColor Cyan
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
