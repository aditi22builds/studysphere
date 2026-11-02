@echo off
title StudySphere Launcher
cd /d "%~dp0"
echo ========================================================
echo        StudySphere - Personal Student Command Center
echo ========================================================
echo Launching StudySphere Desktop Application...
python main.py
if %ERRORLEVEL% NEQ 0 (
    echo.
    echo [ERROR] Application exited with an error code %ERRORLEVEL%.
    pause
)
