@echo off
title Suna AI Launcher
echo ================================
echo       Suna AI Launcher
echo ================================
echo.

REM Change to the Suna AI directory (current script location)
cd /d "%~dp0"

REM Check if Python is available
python --version >nul 2>&1
if errorlevel 1 (
    echo ERROR: Python is not installed or not in PATH
    echo Please install Python 3.11 or later
    pause
    exit /b 1
)

REM Check if setup has been run
if not exist ".setup_progress" (
    echo WARNING: Setup hasn't been run yet
    echo Please run 'python setup.py' first to configure Suna AI
    echo.
    set /p choice="Would you like to run setup now? (y/N): "
    if /i "%choice%"=="y" (
        echo Running Suna AI setup...
        python setup.py
        if errorlevel 1 (
            echo Setup failed. Please check the error messages above.
            pause
            exit /b 1
        )
    ) else (
        echo Exiting. Please run setup first.
        pause
        exit /b 1
    )
)

REM Start Suna AI using the official script
echo Starting Suna AI services...
python start.py -f

if errorlevel 1 (
    echo.
    echo ERROR: Failed to start Suna AI services
    echo Try running 'docker compose logs' for more details
    pause
    exit /b 1
)

echo.
echo SUCCESS: Suna AI services started!
echo Opening browser in 5 seconds...
timeout /t 5 /nobreak >nul

REM Open browser
start http://localhost:3000

echo.
echo Suna AI is now running at: http://localhost:3000
echo To stop Suna AI, run 'python start.py' again
echo.
pause
