@echo off
echo Starting P8 PRO Drone Controller...
echo.

REM Change to the script directory
cd /d "%~dp0python"

REM Check if Python is available
python --version >nul 2>&1
if errorlevel 1 (
    echo ERROR: Python is not installed or not in PATH
    echo Please run install.bat first
    pause
    exit /b 1
)

REM Start the GUI application
echo Launching Drone Controller GUI...
python drone_gui.py

pause