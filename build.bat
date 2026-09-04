@echo off
echo ============================================
echo  GreekG Assistant - Build Script
echo ============================================
echo.

where pyinstaller >nul 2>nul
if %errorlevel% neq 0 (
    echo PyInstaller not found. Installing...
    pip install pyinstaller>=6.0
)

echo Building GreekG Assistant...
echo This may take 2-5 minutes on first run.
echo.

pyinstaller build.spec --clean --noconfirm

if %errorlevel% equ 0 (
    echo.
    echo ============================================
    echo  BUILD SUCCESSFUL
    echo  Output: dist\GreekG Assistant\
    echo ============================================
    echo.
    echo To distribute, zip the 'dist\GreekG Assistant' folder.
    echo Users just need to extract and run 'GreekG Assistant.exe'
) else (
    echo.
    echo BUILD FAILED - check the output above for errors.
)

pause
