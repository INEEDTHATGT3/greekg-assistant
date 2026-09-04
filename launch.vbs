' GreekG Assistant - Detached Launcher
' Launch the app without a terminal/console so it is NOT killed when
' the source terminal or PowerShell is closed. Uses pythonw.exe (no console)
' and runs hidden without waiting, fully detached from the parent terminal.
'
' Double-click this file, or run it from anywhere. To stop the app, use the
' tray icon (right-click -> Quit).

Option Explicit

Dim shell
Set shell = CreateObject("WScript.Shell")

shell.Run _
    """C:\WORK\Greek_g assistant\greekg_env\Scripts\pythonw.exe"" ""C:\WORK\Greek_g assistant\main.py""", _
    0, _
    False
