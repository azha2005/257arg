@echo off
setlocal
start "" "%SystemRoot%\System32\WindowsPowerShell\v1.0\powershell.exe" -NoLogo -NoProfile -ExecutionPolicy Bypass -File "%~dp0herramientas\atlas_terminal\iniciar.ps1" %*
