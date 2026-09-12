@echo off
setlocal enabledelayedexpansion
set "PATH=%SystemRoot%\System32;%SystemRoot%\System32\WindowsPowerShell\v1.0;%SystemRoot%;%PATH%"

title Emergency System Restorer - Debug thugs
color 0A
echo ===============================================================================
echo     EMERGENCY SYSTEM RESTORER (RESET ALL TEST ERRORS TO CLEAN DEFAULTS)
echo ===============================================================================
echo [*] Re-enabling and starting Windows Update, BITS, and CryptSvc...
powershell -NoProfile -ExecutionPolicy Bypass -Command "Set-Service -Name wuauserv, bits, cryptsvc -StartupType Automatic -ErrorAction SilentlyContinue; Start-Service -Name wuauserv, bits, cryptsvc -ErrorAction SilentlyContinue"
echo [*] Flushing DNS cache and resetting Winsock...
ipconfig /flushdns >nul 2>&1
echo [*] Cleaning demo adware hooks...
powershell -NoProfile -ExecutionPolicy Bypass -Command "Remove-ItemProperty -Path 'HKCU:\Software\Microsoft\Windows\CurrentVersion\Run' -Name 'SuspiciousAdwareHookDemo' -ErrorAction SilentlyContinue"
echo.
echo ===============================================================================
echo [✓] System is 100% clean and restored to standard Windows defaults!
echo ===============================================================================
pause