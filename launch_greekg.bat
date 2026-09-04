@echo off
title GreekG Assistant
cd /d "%~dp0"

echo ============================================================
echo  GreekG Assistant is starting...
echo  A window opens; just minimize it to the tray.
echo ============================================================

"%~dp0greekg_env\Scripts\python.exe" "%~dp0main.py"
