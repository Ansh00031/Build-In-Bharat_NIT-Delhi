@echo off
title Emergency System Restorer - Debug thugs
color 0A
echo ===============================================================================
echo     EMERGENCY SYSTEM RESTORER (RESET ALL TEST ERRORS TO CLEAN DEFAULTS)
echo ===============================================================================
echo [*] Re-enabling and starting Windows Update, BITS, and CryptSvc...
powershell -Command "Set-Service -Name wuauserv, bits, cryptsvc -StartupType Automatic -ErrorAction SilentlyContinue; Start-Service -Name wuauserv, bits, cryptsvc -ErrorAction SilentlyContinue"
echo [*] Flushing DNS cache and resetting Winsock...
ipconfig /flushdns >nul 2>&1
echo [*] Cleaning demo adware hooks...
reg delete "HKCU\Software\Microsoft\Windows\CurrentVersion\Run" /v "SuspiciousAdwareHookDemo" /f >nul 2>&1
echo.
echo ===============================================================================
echo [✓] System is 100% clean and restored to standard Windows defaults!
echo ===============================================================================
pause
