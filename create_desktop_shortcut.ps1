# PowerShell script to create desktop shortcuts for Suna AI

# Get the current script directory (project root)
$projectPath = Split-Path -Parent $MyInvocation.MyCommand.Path
$batchFile = Join-Path $projectPath "Launch Suna AI 2.0.bat"

# Get the desktop path
$desktop = [Environment]::GetFolderPath("Desktop")

# Create WScript Shell object
$WScriptShell = New-Object -ComObject WScript.Shell

Write-Host "Creating Suna AI desktop shortcuts..." -ForegroundColor Yellow
Write-Host "" # Empty line

# 1. Create Local Development shortcut
$localShortcutPath = Join-Path $desktop "Suna AI Local.lnk"
$localShortcut = $WScriptShell.CreateShortcut($localShortcutPath)
$localShortcut.TargetPath = $batchFile
$localShortcut.WorkingDirectory = $projectPath
$localShortcut.Description = "Launch Suna AI Local Development Environment"
$localShortcut.IconLocation = "$env:SystemRoot\System32\shell32.dll,21"  # Computer icon
$localShortcut.Save()

Write-Host "✓ Local Development shortcut created" -ForegroundColor Green
Write-Host "  Location: $localShortcutPath" -ForegroundColor Cyan
Write-Host "  Target: $batchFile" -ForegroundColor Cyan
Write-Host "" # Empty line

# 2. Create Render Deployment shortcut
$renderShortcutPath = Join-Path $desktop "Suna AI Render.lnk"
$renderShortcut = $WScriptShell.CreateShortcut($renderShortcutPath)
$renderShortcut.TargetPath = "https://suna-m91e.onrender.com"
$renderShortcut.Description = "Open Suna AI on Render (Production)"
$renderShortcut.IconLocation = "$env:SystemRoot\System32\shell32.dll,14"  # Globe icon
$renderShortcut.Save()

Write-Host "✓ Render Deployment shortcut created" -ForegroundColor Green
Write-Host "  Location: $renderShortcutPath" -ForegroundColor Cyan
Write-Host "  Target: https://suna-m91e.onrender.com" -ForegroundColor Cyan
Write-Host "" # Empty line

# 3. Create Railway Deployment shortcut (placeholder)
$railwayShortcutPath = Join-Path $desktop "Suna AI Railway.lnk"
$railwayShortcut = $WScriptShell.CreateShortcut($railwayShortcutPath)
$railwayShortcut.TargetPath = "https://railway.app"  # Placeholder until Railway URL is available
$railwayShortcut.Description = "Open Suna AI on Railway (Staging) - URL to be updated"
$railwayShortcut.IconLocation = "$env:SystemRoot\System32\shell32.dll,13"  # Network icon
$railwayShortcut.Save()

Write-Host "✓ Railway Deployment shortcut created" -ForegroundColor Green
Write-Host "  Location: $railwayShortcutPath" -ForegroundColor Cyan
Write-Host "  Target: https://railway.app (placeholder)" -ForegroundColor Yellow
Write-Host "" # Empty line

Write-Host "All desktop shortcuts created successfully!" -ForegroundColor Green
Write-Host "You can now access Suna AI through:" -ForegroundColor White
Write-Host "  • Local Development (requires setup)" -ForegroundColor Cyan
Write-Host "  • Render Production (live deployment)" -ForegroundColor Cyan
Write-Host "  • Railway Staging (update URL when available)" -ForegroundColor Cyan

# Release COM object
[System.Runtime.Interopservices.Marshal]::ReleaseComObject($WScriptShell) | Out-Null

Pause