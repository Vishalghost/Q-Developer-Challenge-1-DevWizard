@echo off
echo Dev Assistant - Installation Script
echo ==============================

REM Check for Python installation
python --version >nul 2>&1
if %ERRORLEVEL% NEQ 0 (
    echo ERROR: Python is not installed or not in PATH.
    echo Please install Python 3.6+ and try again.
    pause
    exit /b 1
)

echo Installing dependencies...
python -m pip install -r "%~dp0requirements.txt"

echo.
echo Creating desktop shortcut...
echo Set oWS = WScript.CreateObject("WScript.Shell") > "%TEMP%\shortcut.vbs"
echo sLinkFile = "%USERPROFILE%\Desktop\Dev Assistant.lnk" >> "%TEMP%\shortcut.vbs"
echo Set oLink = oWS.CreateShortcut(sLinkFile) >> "%TEMP%\shortcut.vbs"
echo oLink.TargetPath = "%~dp0start_dev.bat" >> "%TEMP%\shortcut.vbs"
echo oLink.WorkingDirectory = "%~dp0" >> "%TEMP%\shortcut.vbs"
echo oLink.Description = "Dev Assistant - Workflow Automation" >> "%TEMP%\shortcut.vbs"
echo oLink.IconLocation = "%SystemRoot%\System32\SHELL32.dll,21" >> "%TEMP%\shortcut.vbs"
echo oLink.Save >> "%TEMP%\shortcut.vbs"
cscript /nologo "%TEMP%\shortcut.vbs"
del "%TEMP%\shortcut.vbs"

echo.
echo Creating startup shortcut for background mode...
echo Set oWS = WScript.CreateObject("WScript.Shell") > "%TEMP%\startup.vbs"
echo sLinkFile = "%APPDATA%\Microsoft\Windows\Start Menu\Programs\Startup\Dev Assistant.lnk" >> "%TEMP%\startup.vbs"
echo Set oLink = oWS.CreateShortcut(sLinkFile) >> "%TEMP%\startup.vbs"
echo oLink.TargetPath = "%~dp0start_dev.bat" >> "%TEMP%\startup.vbs"
echo oLink.Arguments = "--tray" >> "%TEMP%\startup.vbs"
echo oLink.WorkingDirectory = "%~dp0" >> "%TEMP%\startup.vbs"
echo oLink.Description = "Dev Assistant - Background Mode" >> "%TEMP%\startup.vbs"
echo oLink.IconLocation = "%SystemRoot%\System32\SHELL32.dll,21" >> "%TEMP%\startup.vbs"
echo oLink.Save >> "%TEMP%\startup.vbs"
cscript /nologo "%TEMP%\startup.vbs"
del "%TEMP%\startup.vbs"

echo.
echo Installation complete!
echo.
echo You can now:
echo  - Run Dev Assistant from the desktop shortcut
echo  - Dev Assistant will start automatically in tray mode at system startup
echo  - Edit configuration with: dev_assistant.py --config
echo.
pause