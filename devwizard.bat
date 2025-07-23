@echo off
echo Starting DevWizard...
python "%~dp0devwizard.py" %*
if %ERRORLEVEL% NEQ 0 (
    echo.
    echo Python not found! Please install Python 3.6 or higher.
    echo.
    pause
    exit /b 1
)
pause