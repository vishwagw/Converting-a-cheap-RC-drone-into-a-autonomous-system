@echo off
echo P8 PRO Drone Controller Installation Script
echo ==========================================
echo.

REM Check if Python is installed
python --version >nul 2>&1
if errorlevel 1 (
    echo ERROR: Python is not installed or not in PATH
    echo Please install Python 3.8+ from https://python.org
    pause
    exit /b 1
)

echo Python found. Installing dependencies...
echo.

REM Change to the script directory
cd /d "%~dp0python"

REM Install Python packages
echo Installing Python packages...
pip install -r requirements.txt

if errorlevel 1 (
    echo.
    echo ERROR: Failed to install some packages
    echo Trying alternative PyAudio installation...
    pip install pipwin
    pipwin install pyaudio
    pip install -r requirements.txt
)

echo.
echo Installation complete!
echo.
echo Next steps:
echo 1. Upload arduino/drone_controller.ino to your Arduino Uno
echo 2. Connect nRF24L01 module according to wiring diagram
echo 3. Run: python drone_gui.py
echo.
echo See README.md for detailed instructions
pause