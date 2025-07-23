@echo off
echo Cleaning up repository...

REM Remove duplicate or unnecessary files
echo Removing unnecessary files...
if exist aws_profile_manager.py del aws_profile_manager.py
if exist aws_profile.bat del aws_profile.bat
if exist aws_tray_manager.py del aws_tray_manager.py
if exist aws_tray.bat del aws_tray.bat
if exist dev_assistant.log del dev_assistant.log
if exist install.bat del install.bat
if exist start_dev.bat del start_dev.bat

REM Keep only DevWizard files
echo Keeping only DevWizard files...

REM Add files to git
echo Adding files to git...
git add devwizard.py devwizard.bat devwizard_config.json README_DevWizard.md install_tools.ps1 setup_wsl.ps1 .gitignore

REM Commit changes
echo Committing changes...
git commit -m "Clean up repository and keep only DevWizard files"

echo Done!
echo Now you can push to GitHub with: git push -u origin master
pause