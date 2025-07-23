@echo off
echo ===================================
echo Dev Assistant - Workflow Automation
echo ===================================
echo.

REM Check if Python is available
where py >nul 2>nul
if %ERRORLEVEL% NEQ 0 (
    echo Python not found! Please install Python 3.6 or higher.
    goto :end
)

echo Starting Dev Assistant...
echo.
py "%~dp0dev_assistant.py" %*

:end
echo.
echo Press any key to exit...
pause >nul