@echo off
title GreekG Assistant
cd /d "C:\WORK\LIFE EASY"

echo ============================================================
echo  GreekG Assistant is starting...
echo  Close THIS window any time to fully stop it and free RAM.
echo ============================================================
echo.

"C:\WORK\LIFE EASY\greekg_env\Scripts\python.exe" "C:\WORK\LIFE EASY\greekg_assistant.py"

echo.
echo [GreekG] Process ended (crashed or was stopped).
echo Close this window to fully exit.
pause >nul