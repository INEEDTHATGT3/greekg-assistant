' Run this file ONCE by double-clicking it.
' It creates a Desktop shortcut that opens a terminal and starts GreekG Assistant.
' Windows won't let scripts auto-pin to the taskbar (blocked for security reasons),
' so the last manual step is: drag the created shortcut onto your taskbar to pin it.

Set WshShell = CreateObject("WScript.Shell")
DesktopPath = WshShell.SpecialFolders("Desktop")

Set Shortcut = WshShell.CreateShortcut(DesktopPath & "\GreekG Assistant.lnk")
Shortcut.TargetPath = "C:\Windows\System32\cmd.exe"
Shortcut.Arguments = "/k ""C:\WORK\LIFE EASY\launch_greekg.bat"""
Shortcut.WorkingDirectory = "C:\WORK\LIFE EASY"
Shortcut.Description = "Launch GreekG Assistant"
Shortcut.WindowStyle = 1
Shortcut.Save

MsgBox "Shortcut created on your Desktop: 'GreekG Assistant'." & vbCrLf & vbCrLf & _
       "Last step (manual, one-time): drag that shortcut onto your Taskbar to pin it." & vbCrLf & _
       "(Or right-click it -> Pin to taskbar, if that option is shown on your Windows version.)" & vbCrLf & vbCrLf & _
       "After that, one click on the taskbar icon launches everything." & vbCrLf & _
       "You can delete this .vbs file now, or keep it in case you need to re-create the shortcut later.", _
       64, "GreekG Setup"