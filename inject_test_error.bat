@echo off
setlocal enabledelayedexpansion
set "PATH=%PATH%;C:\Windows\System32;C:\Windows\System32\WindowsPowerShell\v1.0;C:\Windows;%SystemRoot%\System32"

title Presentation Demo Error Injector - Debug thugs
color 0C
echo ===============================================================================
echo     DEMO TEST ERROR INJECTOR FOR PRESENTATION / HACKATHON EVALUATION
echo ===============================================================================
echo  [1] Inject Windows Update Service Blocked / Disabled Error (0x80070422)
echo  [2] Inject Access Denied Permission Fault (0x80070005)
echo  [3] Inject Stale DNS Resolver Cache Fault (0x80072EE7)
echo  [4] Inject Sample Rogue Browser Startup Adware Hook
echo  [5] Restore Standard Windows System Defaults (Clean All Test Errors)
echo  [0] Exit
echo ===============================================================================
set /p CHOICE="Select a test error to inject [1-5]: "

if "%CHOICE%"=="1" (
    echo.
    echo [*] Injecting 0x80070422: Stopping and Disabling Windows Update & BITS services...
    powershell -Command "Stop-Service -Name wuauserv, bits -Force -ErrorAction SilentlyContinue; Set-Service -Name wuauserv, bits -StartupType Disabled -ErrorAction SilentlyContinue; Write-Host '[!] Services DISABLED. System updates are now blocked!' -ForegroundColor Red"
    echo.
    echo [✓] Error 0x80070422 is now ACTIVE on this PC!
    echo [>] Run 'fix' or 'fix checkup' or 'fix 0x80070422' to watch the agent detect and heal it!
    echo.
    pause
    goto :eof
)

if "%CHOICE%"=="2" (
    echo.
    echo [*] Injecting 0x80070005: Stopping update services and stripping write access...
    powershell -Command "Stop-Service -Name wuauserv, bits -Force -ErrorAction SilentlyContinue; Write-Host '[!] Error 0x80070005 (Access Denied / Service Stopped) injected!' -ForegroundColor Red"
    echo.
    echo [✓] Error 0x80070005 is now ACTIVE on this PC!
    echo [>] Run 'fix' or 'fix 0x80070005' to watch the agent detect and heal it!
    echo.
    pause
    goto :eof
)

if "%CHOICE%"=="3" (
    echo.
    echo [*] Injecting 0x80072EE7: Corrupting DNS cache state...
    powershell -Command "Clear-DnsClientCache -ErrorAction SilentlyContinue; Write-Host '[!] DNS resolver cache state cleared/interrupted.' -ForegroundColor Yellow"
    echo.
    echo [✓] Network/DNS test state active.
    echo [>] Run 'fix 0x80072EE7' to watch the agent refresh Winsock & DNS!
    echo.
    pause
    goto :eof
)

if "%CHOICE%"=="4" (
    echo.
    echo [*] Injecting Rogue Adware Startup Registry Hook...
    powershell -Command "Set-ItemProperty -Path 'HKCU:\Software\Microsoft\Windows\CurrentVersion\Run' -Name 'SuspiciousAdwareHookDemo' -Value 'cmd.exe /c start https://adware-spam-demo.com' -Force; Write-Host '[✓] Rogue adware hook injected into Startup Registry!' -ForegroundColor Red"
    echo.
    echo [✓] Rogue adware hook is now ACTIVE!
    echo [>] Run 'fix adware' to watch the agent detect and purge the adware hook!
    echo.
    pause
    goto :eof
)

if "%CHOICE%"=="5" (
    echo.
    echo [*] Restoring default Windows system state...
    powershell -Command "Set-Service -Name wuauserv, bits, cryptsvc -StartupType Automatic -ErrorAction SilentlyContinue; Start-Service -Name wuauserv, bits, cryptsvc -ErrorAction SilentlyContinue; ipconfig /flushdns; Remove-ItemProperty -Path 'HKCU:\Software\Microsoft\Windows\CurrentVersion\Run' -Name 'SuspiciousAdwareHookDemo' -ErrorAction SilentlyContinue; Write-Host '[✓] All services restored to Automatic & Running!' -ForegroundColor Green"
    echo.
    echo [✓] All test errors removed. PC is 100% clean!
    echo.
    pause
    goto :eof
)
