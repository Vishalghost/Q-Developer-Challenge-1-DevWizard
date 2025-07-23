@echo off
echo Starting AWS Profile Tray Manager...

REM Check for Python installation
python --version >nul 2>&1
if %ERRORLEVEL% NEQ 0 (
    echo Python is not installed or not in PATH. Please install Python 3.6+
    pause
    exit /b 1
)

REM Check for required packages
python -c "import pystray, PIL" >nul 2>&1
if %ERRORLEVEL% NEQ 0 (
    echo Installing required packages...
    python -m pip install pystray pillow
)

REM Start the tray application in background
start /b pythonw "%~dp0aws_tray_manager.py"