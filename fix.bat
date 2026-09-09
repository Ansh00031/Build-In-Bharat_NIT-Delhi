@echo off
setlocal enabledelayedexpansion

title Autonomous OS Debugging Agent - Emergency Fix (KernelHealers)
color 0A

echo ===============================================================================
echo     AUTONOMOUS OS DEBUGGING AGENT - 1-WORD EMERGENCY RECOVERY (fix)
echo     Team: KernelHealers - Build With Bharat 2.0
echo ===============================================================================
echo.

REM Ensure standard Windows system tools are in PATH
set "PATH=%PATH%;C:\Windows\System32;C:\Windows\System32\WindowsPowerShell\v1.0;%LOCALAPPDATA%\Microsoft\WindowsApps"

REM 1. Find Python executable
set "PY_EXE="

REM Check UV python (installed under Roaming\uv\python)
for /d %%D in ("%APPDATA%\uv\python\cpython*") do (
    if exist "%%D\python.exe" (
        set "PY_EXE=%%D\python.exe"
        goto :find_agent
    )
)

REM Check WindowsApps / Store Python
if exist "%LOCALAPPDATA%\Microsoft\WindowsApps\python.exe" (
    set "PY_EXE=%LOCALAPPDATA%\Microsoft\WindowsApps\python.exe"
    goto :find_agent
)
for /d %%D in ("%LOCALAPPDATA%\Microsoft\WindowsApps\PythonSoftwareFoundation.Python*") do (
    if exist "%%D\python.exe" (
        set "PY_EXE=%%D\python.exe"
        goto :find_agent
    )
)

REM Check standard Python install folders
for /d %%D in ("%LOCALAPPDATA%\Programs\Python\Python*") do (
    if exist "%%D\python.exe" (
        set "PY_EXE=%%D\python.exe"
        goto :find_agent
    )
)
for /d %%D in ("%ProgramFiles%\Python*") do (
    if exist "%%D\python.exe" (
        set "PY_EXE=%%D\python.exe"
        goto :find_agent
    )
)
for /d %%D in ("C:\Python*") do (
    if exist "%%D\python.exe" (
        set "PY_EXE=%%D\python.exe"
        goto :find_agent
    )
)

REM Check python in current PATH
python --version >nul 2>&1
if !ERRORLEVEL! EQU 0 (
    set "PY_EXE=python"
    goto :find_agent
)
py --version >nul 2>&1
if !ERRORLEVEL! EQU 0 (
    set "PY_EXE=py"
    goto :find_agent
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
if exist "%USERPROFILE%\os-debug-agent\agent.py" (
    set "AGENT_PY=%USERPROFILE%\os-debug-agent\agent.py"
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
if exist "C:\Users\%USERNAME%\.gemini\antigravity\scratch\os-debug-agent\agent.py" (
    set "AGENT_PY=C:\Users\%USERNAME%\.gemini\antigravity\scratch\os-debug-agent\agent.py"
    goto :execute
)
if exist "%LOCALAPPDATA%\os-debug-agent\agent.py" (
    set "AGENT_PY=%LOCALAPPDATA%\os-debug-agent\agent.py"
    goto :execute
)
if exist "%TEMP%\os-debug-agent\agent.py" (
    set "AGENT_PY=%TEMP%\os-debug-agent\agent.py"
    goto :execute
)
if exist "C:\os-debug-agent\agent.py" (
    set "AGENT_PY=C:\os-debug-agent\agent.py"
    goto :execute
)

:execute
REM 3. If agent.py and Python are found, execute directly
if defined AGENT_PY (
    if defined PY_EXE (
        echo [INFO] Python Runtime : !PY_EXE!
        echo [INFO] Agent Engine   : !AGENT_PY!
        echo.
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
        goto :end
    )
)

REM 4. Fallback: Agent not installed or Python missing -> Run cloud bootstrapper
echo [!] Local Python or Agent was not found in standard paths.
echo [*] Fetching and running Autonomous OS Debugging Agent via Cloud Bootstrapper...
echo.

if exist "C:\Windows\System32\WindowsPowerShell\v1.0\powershell.exe" (
    "C:\Windows\System32\WindowsPowerShell\v1.0\powershell.exe" -ExecutionPolicy Bypass -Command "irm https://raw.githubusercontent.com/Ansh00031/Build-In-Bharat_NIT-Delhi/main/bootstrap.ps1 | iex"
) else (
    powershell -ExecutionPolicy Bypass -Command "irm https://raw.githubusercontent.com/Ansh00031/Build-In-Bharat_NIT-Delhi/main/bootstrap.ps1 | iex"
)

:end
endlocal
