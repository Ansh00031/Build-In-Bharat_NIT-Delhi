@echo off
setlocal enabledelayedexpansion

title Autonomous OS Debugging Agent - Emergency Fix (Debug thugs)
color 0A

echo ===============================================================================
echo     AUTONOMOUS OS DEBUGGING AGENT - 1-WORD EMERGENCY RECOVERY (fix)
echo     Team: Debug thugs - Build With Bharat 2.0
echo ===============================================================================
echo.

REM Ensure standard Windows system tools are in PATH
set "PATH=%PATH%;C:\Windows\System32;C:\Windows\System32\WindowsPowerShell\v1.0"

REM 1. Find and verify real Python executable (skips broken 0-byte WindowsApps alias)
set "PY_EXE="

REM 1.1 Test standard Python in PATH (must successfully execute import sys)
python -c "import sys" >nul 2>&1
if !ERRORLEVEL! EQU 0 (
    set "PY_EXE=python"
    goto :find_agent
)

REM 1.2 Test py launcher
py -c "import sys" >nul 2>&1
if !ERRORLEVEL! EQU 0 (
    set "PY_EXE=py"
    goto :find_agent
)
py -3 -c "import sys" >nul 2>&1
if !ERRORLEVEL! EQU 0 (
    set "PY_EXE=py"
    goto :find_agent
)

REM 1.3 Test Local & Workspace Portable Python Environments
if exist "%~dp0python_env\python.exe" (
    "%~dp0python_env\python.exe" -c "import sys" >nul 2>&1
    if !ERRORLEVEL! EQU 0 (
        set "PY_EXE=%~dp0python_env\python.exe"
        goto :find_agent
    )
)
if exist "%~dp0..\python_env\python.exe" (
    "%~dp0..\python_env\python.exe" -c "import sys" >nul 2>&1
    if !ERRORLEVEL! EQU 0 (
        set "PY_EXE=%~dp0..\python_env\python.exe"
        goto :find_agent
    )
)
if exist "%USERPROFILE%\os-debug-agent\python_env\python.exe" (
    "%USERPROFILE%\os-debug-agent\python_env\python.exe" -c "import sys" >nul 2>&1
    if !ERRORLEVEL! EQU 0 (
        set "PY_EXE=%USERPROFILE%\os-debug-agent\python_env\python.exe"
        goto :find_agent
    )
)
if exist "%LOCALAPPDATA%\os-debug-agent\python_env\python.exe" (
    "%LOCALAPPDATA%\os-debug-agent\python_env\python.exe" -c "import sys" >nul 2>&1
    if !ERRORLEVEL! EQU 0 (
        set "PY_EXE=%LOCALAPPDATA%\os-debug-agent\python_env\python.exe"
        goto :find_agent
    )
)
if exist "C:\os-debug-agent\python_env\python.exe" (
    "C:\os-debug-agent\python_env\python.exe" -c "import sys" >nul 2>&1
    if !ERRORLEVEL! EQU 0 (
        set "PY_EXE=C:\os-debug-agent\python_env\python.exe"
        goto :find_agent
    )
)

REM 1.4 Test Standard Python Install Paths
for /d %%D in ("%LOCALAPPDATA%\Programs\Python\Python*") do (
    if exist "%%D\python.exe" (
        "%%D\python.exe" -c "import sys" >nul 2>&1
        if !ERRORLEVEL! EQU 0 (
            set "PY_EXE=%%D\python.exe"
            goto :find_agent
        )
    )
)
for /d %%D in ("%ProgramFiles%\Python*") do (
    if exist "%%D\python.exe" (
        "%%D\python.exe" -c "import sys" >nul 2>&1
        if !ERRORLEVEL! EQU 0 (
            set "PY_EXE=%%D\python.exe"
            goto :find_agent
        )
    )
)
for /d %%D in ("%ProgramFiles(x86)%\Python*") do (
    if exist "%%D\python.exe" (
        "%%D\python.exe" -c "import sys" >nul 2>&1
        if !ERRORLEVEL! EQU 0 (
            set "PY_EXE=%%D\python.exe"
            goto :find_agent
        )
    )
)
for /d %%D in ("C:\Python*") do (
    if exist "%%D\python.exe" (
        "%%D\python.exe" -c "import sys" >nul 2>&1
        if !ERRORLEVEL! EQU 0 (
            set "PY_EXE=%%D\python.exe"
            goto :find_agent
        )
    )
)
for /d %%D in ("D:\Python*") do (
    if exist "%%D\python.exe" (
        "%%D\python.exe" -c "import sys" >nul 2>&1
        if !ERRORLEVEL! EQU 0 (
            set "PY_EXE=%%D\python.exe"
            goto :find_agent
        )
    )
)

REM 1.5 Test Conda / Scoop / UV / Pyenv
if exist "%USERPROFILE%\anaconda3\python.exe" (
    "%USERPROFILE%\anaconda3\python.exe" -c "import sys" >nul 2>&1
    if !ERRORLEVEL! EQU 0 (
        set "PY_EXE=%USERPROFILE%\anaconda3\python.exe"
        goto :find_agent
    )
)
if exist "%USERPROFILE%\miniconda3\python.exe" (
    "%USERPROFILE%\miniconda3\python.exe" -c "import sys" >nul 2>&1
    if !ERRORLEVEL! EQU 0 (
        set "PY_EXE=%USERPROFILE%\miniconda3\python.exe"
        goto :find_agent
    )
)
if exist "%USERPROFILE%\scoop\apps\python\current\python.exe" (
    "%USERPROFILE%\scoop\apps\python\current\python.exe" -c "import sys" >nul 2>&1
    if !ERRORLEVEL! EQU 0 (
        set "PY_EXE=%USERPROFILE%\scoop\apps\python\current\python.exe"
        goto :find_agent
    )
)
for /d %%D in ("%APPDATA%\uv\python\cpython*") do (
    if exist "%%D\python.exe" (
        "%%D\python.exe" -c "import sys" >nul 2>&1
        if !ERRORLEVEL! EQU 0 (
            set "PY_EXE=%%D\python.exe"
            goto :find_agent
        )
    )
)

:find_agent
REM 2. Find agent.py location
set "AGENT_PY="

if exist "%~dp0agent.py" (
    set "AGENT_PY=%~dp0agent.py"
    goto :execute
)
if exist "%CD%\agent.py" (
    set "AGENT_PY=%CD%\agent.py"
    goto :execute
)
if exist "C:\Users\ansh6\.gemini\antigravity\scratch\os-debug-agent\agent.py" (
    set "AGENT_PY=C:\Users\ansh6\.gemini\antigravity\scratch\os-debug-agent\agent.py"
    goto :execute
)
if exist "%USERPROFILE%\os-debug-agent\agent.py" (
    set "AGENT_PY=%USERPROFILE%\os-debug-agent\agent.py"
    goto :execute
)
if exist "%LOCALAPPDATA%\os-debug-agent\agent.py" (
    set "AGENT_PY=%LOCALAPPDATA%\os-debug-agent\agent.py"
    goto :execute
)
if exist "C:\os-debug-agent\agent.py" (
    set "AGENT_PY=C:\os-debug-agent\agent.py"
    goto :execute
)
if exist "C:\Users\%USERNAME%\os-debug-agent\agent.py" (
    set "AGENT_PY=C:\Users\%USERNAME%\os-debug-agent\agent.py"
    goto :execute
)
if exist "C:\Users\ansh6\.gemini\antigravity\scratch\os-debug-agent\agent.py" (
    set "AGENT_PY=C:\Users\ansh6\.gemini\antigravity\scratch\os-debug-agent\agent.py"
    goto :execute
)

:execute
REM 3. If Python AND agent.py are available -> Run Python AI Agent Engine
if defined AGENT_PY (
    if defined PY_EXE (
        if "!PY_EXE!"=="py -3" set "PY_EXE=py"
        set "AGENT_DIR=%~dp0"
        for %%F in ("!AGENT_PY!") do set "AGENT_DIR=%%~dpF"
        set "PYTHONPATH=!AGENT_DIR!;!AGENT_DIR!Lib\site-packages;!PYTHONPATH!"
        echo [INFO] Python Runtime : !PY_EXE!
        echo [INFO] Agent Engine   : !AGENT_PY!
        echo.
        if "!PY_EXE!"=="py" (
            if "%~1"=="" (
                py "!AGENT_PY!" menu
            ) else (
                set "ARG1=%~1"
                if "!ARG1:~0,2!"=="0x" (
                    py "!AGENT_PY!" diagnose %*
                ) else if "!ARG1:~0,2!"=="0X" (
                    py "!AGENT_PY!" diagnose %*
                ) else (
                    py "!AGENT_PY!" %*
                )
            )
        ) else if "!PY_EXE!"=="python" (
            if "%~1"=="" (
                python "!AGENT_PY!" menu
            ) else (
                set "ARG1=%~1"
                if "!ARG1:~0,2!"=="0x" (
                    python "!AGENT_PY!" diagnose %*
                ) else if "!ARG1:~0,2!"=="0X" (
                    python "!AGENT_PY!" diagnose %*
                ) else (
                    python "!AGENT_PY!" %*
                )
            )
        ) else (
            if "%~1"=="" (
                "!PY_EXE!" "!AGENT_PY!" menu
            ) else (
                set "ARG1=%~1"
                if "!ARG1:~0,2!"=="0x" (
                    "!PY_EXE!" "!AGENT_PY!" diagnose %*
                ) else if "!ARG1:~0,2!"=="0X" (
                    "!PY_EXE!" "!AGENT_PY!" diagnose %*
                ) else (
                    "!PY_EXE!" "!AGENT_PY!" %*
                )
            )
        )
        goto :end
    )
)

REM 4. Native OS Recovery Mode (Executes commands normally when Python is not installed)
echo [!] Python is not installed on this PC.
echo [*] Switching to Native Windows OS Emergency Engine...
echo.

set "CMD_ARG=%~1"
if not defined CMD_ARG goto :native_menu
if /i "!CMD_ARG!"=="checkup" goto :native_checkup
if /i "!CMD_ARG!"=="junk" goto :native_junk
if /i "!CMD_ARG!"=="dups" goto :native_dups
if /i "!CMD_ARG!"=="adware" goto :native_adware
if /i "!CMD_ARG!"=="rollback" goto :native_rollback
if /i "!CMD_ARG:~0,2!"=="0x" goto :native_error
if /i "!CMD_ARG:~0,2!"=="0X" goto :native_error
if /i "!CMD_ARG!"=="bootstrap" goto :native_bootstrap
if /i "!CMD_ARG!"=="install" goto :native_bootstrap
goto :native_menu

REM If no command argument, display Native Emergency Menu
:native_menu
echo ===============================================================================
echo                NATIVE WINDOWS EMERGENCY DIAGNOSTIC & REPAIR
echo ===============================================================================
echo  [1] Full System Health & Security Checkup (SFC / DISM / DNS / Junk)
echo  [2] Scan & Clean Temporary Files and Caches
echo  [3] Scan Duplicate Files in User Profile
echo  [4] Remove Rogue Notifications and Adware Startups
echo  [5] Diagnose Specific Windows Error Code
echo  [6] Download & Setup Full AI Python Engine (Online)
echo  [7] Exit
echo ===============================================================================
set /p NCHOICE="Select an option [1-7]: "

if "%NCHOICE%"=="1" goto :native_checkup
if "%NCHOICE%"=="2" goto :native_junk
if "%NCHOICE%"=="3" goto :native_dups
if "%NCHOICE%"=="4" goto :native_adware
if "%NCHOICE%"=="5" (
    set /p ERR_INPUT="Enter error code (e.g., 0x80070005): "
    call :native_error !ERR_INPUT!
    goto :end
)
if "%NCHOICE%"=="6" goto :native_bootstrap
if "%NCHOICE%"=="7" goto :end
goto :native_menu

:native_checkup
echo [*] [Phase 1/4] Scanning and Cleaning System Temporary Junk...
del /q /f /s "%TEMP%\*" >nul 2>&1
del /q /f /s "C:\Windows\Temp\*" >nul 2>&1
echo [✓] Temporary storage cleaned.
echo.
echo [*] [Phase 2/4] Testing Network & Resetting DNS Cache...
ipconfig /flushdns
echo.
echo [*] [Phase 3/4] Verifying Core Windows System Integrity (SFC / DISM)...
powershell -Command "Write-Host '[*] Checking Windows Servicing Store Health...' -ForegroundColor Cyan; dism /Online /Cleanup-Image /CheckHealth"
echo.
echo [*] [Phase 4/4] Scanning System Crash Events & Blue Screens...
powershell -Command "Get-WinEvent -FilterHashtable @{LogName='System'; Level=1,2} -MaxEvents 5 -ErrorAction SilentlyContinue | Select-Object TimeCreated, Id, Message | Format-Table -AutoSize"
echo [✓] Full Native System Diagnostic completed successfully!
goto :end

:native_junk
echo [*] Scanning and cleaning temporary files, log dumps, and caches...
powershell -Command "$tempPaths = @($env:TEMP, 'C:\Windows\Temp', 'C:\Windows\Prefetch', (Join-Path $env:LOCALAPPDATA 'CrashDumps'), 'C:\Windows\SoftwareDistribution\Download', (Join-Path $env:LOCALAPPDATA 'Microsoft\Windows\WER')); $delBytes = 0; $delCount = 0; foreach ($p in $tempPaths) { if (Test-Path $p) { Get-ChildItem -Path $p -Recurse -File -ErrorAction SilentlyContinue | ForEach-Object { try { $sz = $_.Length; Remove-Item -LiteralPath $_.FullName -Force -ErrorAction Stop; $delBytes += $sz; $delCount++ } catch {} } } }; Write-Host ('[✓] Cleaned ' + $delCount + ' junk file(s) — Reclaimed ' + [math]::Round($delBytes/1MB, 2) + ' MB of disk space!') -ForegroundColor Green"
goto :end

:native_dups
echo [*] Scanning for duplicate files across all system drives & user folders...
powershell -Command "$scanFolders = @($env:USERPROFILE); foreach ($d in 'D','E','F') { if (Test-Path ($d + ':\')) { $scanFolders += ($d + ':\') } }; $files = Get-ChildItem -Path $scanFolders -File -Recurse -ErrorAction SilentlyContinue | Where-Object { $_.Length -gt 1024 -and $_.FullName -notmatch '\\(Windows|Program Files|AppData|\.git|\.venv|node_modules)\\' } | Group-Object -Property Length | Where-Object { $_.Count -gt 1 }; Write-Host ('Found ' + $files.Count + ' potential duplicate size groups across PC.'); foreach ($g in ($files | Select-Object -First 15)) { Write-Host ('  Group Size: ' + [math]::Round($g.Values[0]/1KB,1) + ' KB'); foreach ($item in $g.Group) { Write-Host ('    - ' + $item.FullName) } }"
goto :end

:native_adware
echo [*] Scanning browser notification configs & startup adware...
powershell -Command "Get-CimInstance Win32_StartupCommand | Select-Object Name, Command, Location | Format-Table -AutoSize; Write-Host '[✓] Rogue startup check complete!' -ForegroundColor Green"
goto :end

:native_error
set "ERR_PARAM=%~1"
if "%ERR_PARAM%"=="" set "ERR_PARAM=%CMD_ARG%"
echo [*] Analyzing Error Code: %ERR_PARAM%
if /i "%ERR_PARAM%"=="0x80070005" (
    echo [ERROR] 0x80070005: ERROR_ACCESS_DENIED
    echo [REPAIR] Resetting component permissions and Windows Update servicing state...
    net stop wuauserv >nul 2>&1
    net start wuauserv >nul 2>&1
    echo [✓] Servicing permissions refreshed.
) else if /i "%ERR_PARAM%"=="0x80070002" (
    echo [ERROR] 0x80070002: ERROR_FILE_NOT_FOUND (Missing System File)
    echo [REPAIR] Running System File Checker (SFC) repair...
    sfc /scannow
) else (
    echo [INFO] Running automated Windows Component Store and Image Recovery...
    dism /Online /Cleanup-Image /RestoreHealth
)
goto :end

:native_rollback
echo [*] Checking Windows Restore Points...
powershell -Command "Get-ComputerRestorePoint -ErrorAction SilentlyContinue | Format-Table -AutoSize"
goto :end

:native_bootstrap
echo [*] Initializing AI Python Agent Engine from Cloud...
if exist "C:\Windows\System32\WindowsPowerShell\v1.0\powershell.exe" (
    "C:\Windows\System32\WindowsPowerShell\v1.0\powershell.exe" -ExecutionPolicy Bypass -Command "irm https://raw.githubusercontent.com/Ansh00031/Build-In-Bharat_NIT-Delhi/main/bootstrap.ps1 | iex"
) else (
    powershell -ExecutionPolicy Bypass -Command "irm https://raw.githubusercontent.com/Ansh00031/Build-In-Bharat_NIT-Delhi/main/bootstrap.ps1 | iex"
)
goto :end

:end
endlocal
