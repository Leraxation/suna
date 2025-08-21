# Updated Suna AI Launcher - Uses Official start.py Script
# Path to your Suna AI project directory
$sunaPath = "C:\Users\ASUS\AI\AI_Agents_Projects\Suna-Ai-latest"

# Path to Docker Desktop executable (adjust if yours is different)
$dockerDesktopPath = "C:\Program Files\Docker\Docker\Docker Desktop.exe"

# URL for Suna AI frontend
$sunaUrl = "http://localhost:3000"

Write-Host "=== Suna AI Launcher ===" -ForegroundColor Cyan
Write-Host "Starting Suna AI services..." -ForegroundColor Green

# Check if Docker Desktop is running
$dockerProcess = Get-Process "Docker Desktop" -ErrorAction SilentlyContinue
if (-not $dockerProcess) {
    Write-Host "Docker Desktop is not running. Starting Docker Desktop..." -ForegroundColor Yellow
    try {
        Start-Process -FilePath $dockerDesktopPath
        Write-Host "Waiting for Docker Desktop to initialize..." -ForegroundColor Yellow
        Start-Sleep -Seconds 60
    } catch {
        Write-Error "Failed to start Docker Desktop. Please start it manually and try again."
        pause
        exit 1
    }
} else {
    Write-Host "Docker Desktop is already running." -ForegroundColor Green
}

# Navigate to Suna AI directory
Write-Host "Navigating to Suna AI directory: $sunaPath" -ForegroundColor Cyan
Set-Location $sunaPath

# Check if setup has been run
if (-not (Test-Path ".setup_progress")) {
    Write-Warning "Setup hasn't been run yet. Please run 'python setup.py' first to configure Suna AI."
    $runSetup = Read-Host "Would you like to run setup now? (y/N)"
    if ($runSetup -eq "y" -or $runSetup -eq "Y") {
        Write-Host "Running Suna AI setup..." -ForegroundColor Cyan
        python setup.py
        if ($LASTEXITCODE -ne 0) {
            Write-Error "Setup failed. Please check the error messages above."
            pause
            exit 1
        }
    } else {
        Write-Host "Exiting. Please run setup first." -ForegroundColor Yellow
        pause
        exit 1
    }
}

# Use the official start.py script with force flag to skip confirmation
Write-Host "Starting Suna AI services using official start script..." -ForegroundColor Cyan
python start.py -f

if ($LASTEXITCODE -eq 0) {
    Write-Host "Suna AI services started successfully!" -ForegroundColor Green
    
    # Wait a bit for services to fully initialize
    Write-Host "Waiting for services to fully initialize..." -ForegroundColor Yellow
    Start-Sleep -Seconds 30
    
    # Check if services are actually running
    $servicesRunning = docker compose ps -q
    if ($servicesRunning) {
        Write-Host "Opening Suna AI in your default browser..." -ForegroundColor Cyan
        try {
            Start-Process $sunaUrl
            Write-Host "Suna AI is now accessible at: $sunaUrl" -ForegroundColor Green
        } catch {
            Write-Warning "Could not open browser automatically. Please open $sunaUrl manually."
        }
    } else {
        Write-Warning "Services may not have started properly. Please check Docker logs."
    }
} else {
    Write-Error "Failed to start Suna AI services. Please check the error messages above."
    Write-Host "You can try running 'docker compose logs' to see detailed error information." -ForegroundColor Yellow
}

Write-Host "`nSuna AI Launcher completed. You can close this window." -ForegroundColor Cyan
Write-Host "To stop Suna AI, run 'python start.py' again or use 'docker compose down'" -ForegroundColor Yellow

# Keep window open briefly
Start-Sleep -Seconds 10
