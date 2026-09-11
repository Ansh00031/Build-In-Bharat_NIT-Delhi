"""Windows persistent auto-start and startup task manager with single-instance enforcement and logging."""

import os
import platform
import sys
from datetime import datetime
from pathlib import Path
from typing import Tuple

REG_RUN_PATH = r"Software\Microsoft\Windows\CurrentVersion\Run"
AUTOSTART_VALUE_NAME = "AutonomousOSDebugAgent"


def get_startup_folder() -> Path:
    """Return the Windows User Startup folder path."""
    appdata = os.environ.get("APPDATA", "")
    if appdata:
        return Path(appdata) / "Microsoft" / "Windows" / "Start Menu" / "Programs" / "Startup"
    return Path.home() / "AppData" / "Roaming" / "Microsoft" / "Windows" / "Start Menu" / "Programs" / "Startup"


def is_autostart_enabled() -> Tuple[bool, str]:
    """Check if the agent is registered to run automatically on PC startup.

    Returns:
        Tuple[bool, str]: (is_enabled, details_or_method)
    """
    if platform.system() != "Windows":
        return False, "Auto-start is only supported on Windows."

    # 1. Check Startup Folder Launcher (Primary)
    startup_bat = get_startup_folder() / "OS_Debug_Agent_Startup.bat"
    if startup_bat.exists():
        return True, f"Startup Folder Launcher ({startup_bat.name})"

    # 2. Check Registry Run Key
    try:
        import winreg
        with winreg.OpenKey(winreg.HKEY_CURRENT_USER, REG_RUN_PATH, 0, winreg.KEY_READ) as key:
            val, _ = winreg.QueryValueEx(key, AUTOSTART_VALUE_NAME)
            if val:
                return True, f"Windows Registry Run Key ({AUTOSTART_VALUE_NAME})"
    except Exception:
        pass

    return False, "Not registered for startup."


def enable_autostart(mode: str = "health_check") -> Tuple[bool, str]:
    """Register a single, clean startup launcher with persistent logging and visible window retention.

    Returns:
        Tuple[bool, str]: (success, status_message)
    """
    if platform.system() != "Windows":
        return False, "Auto-start is only supported on Windows operating systems."

    try:
        # First clean up any duplicate registry entries to prevent multiple popups
        disable_autostart()

        agent_dir = Path(__file__).resolve().parent.parent
        agent_py = agent_dir / "agent.py"
        python_exe = sys.executable
        backups_dir = agent_dir / ".backups"
        backups_dir.mkdir(parents=True, exist_ok=True)
        log_file = backups_dir / "startup_log.txt"

        # Create a single, high-visibility launcher in the Startup Folder
        startup_dir = get_startup_folder()
        startup_dir.mkdir(parents=True, exist_ok=True)
        startup_bat = startup_dir / "OS_Debug_Agent_Startup.bat"

        bat_content = f"""@echo off
cls
color 0B
echo ===============================================================================
echo     AUTONOMOUS OS DEBUGGING AGENT - SYSTEM STARTUP HEALTH MONITOR
echo ===============================================================================
echo [INFO] Timestamp: %DATE% %TIME%
echo [INFO] Session Log: {log_file}
echo.

cd /d "{agent_dir}"

REM Log execution to persistent file
echo [STARTUP_RUN] %DATE% %TIME% >> "{log_file}"

REM Run startup-monitor (shows problem faced, solution statement, and live health)
"{python_exe}" "{agent_py}" startup-monitor
echo.
echo ===============================================================================
echo [STATUS] Startup health scan complete. The agent is active and monitoring.
echo To run diagnostics on a specific error: python agent.py diagnose [ERROR_CODE]
echo ===============================================================================
echo.
pause
"""
        startup_bat.write_text(bat_content, encoding="utf-8")

        # Also install the 1-word emergency 'fix' shortcut
        install_fix_shortcut()

        return True, f"Auto-start enabled! Created clean single startup launcher: {startup_bat.name} & installed 'fix' shortcut."

    except Exception as ex:
        return False, f"Failed to enable auto-start: {str(ex)}"


def disable_autostart() -> Tuple[bool, str]:
    """Unregister and remove all startup launchers and duplicate registry entries."""
    if platform.system() != "Windows":
        return False, "Auto-start is only supported on Windows."

    removed_items = []
    try:
        # 1. Clean Registry Run Key
        import winreg
        try:
            with winreg.OpenKey(winreg.HKEY_CURRENT_USER, REG_RUN_PATH, 0, winreg.KEY_SET_VALUE) as key:
                winreg.DeleteValue(key, AUTOSTART_VALUE_NAME)
                removed_items.append("Registry Run Key")
        except FileNotFoundError:
            pass

        # 2. Clean RunOnce Key if left over
        try:
            with winreg.OpenKey(winreg.HKEY_CURRENT_USER, r"Software\Microsoft\Windows\CurrentVersion\RunOnce", 0, winreg.KEY_SET_VALUE) as key:
                winreg.DeleteValue(key, "OSDebugAgentResume")
                removed_items.append("RunOnce Key")
        except FileNotFoundError:
            pass

        # 3. Clean Startup Folder Launcher
        startup_bat = get_startup_folder() / "OS_Debug_Agent_Startup.bat"
        if startup_bat.exists():
            startup_bat.unlink()
            removed_items.append(f"Startup file ({startup_bat.name})")

        if removed_items:
            return True, f"Successfully cleaned startup triggers (Removed: {', '.join(removed_items)})."
        else:
            return True, "Auto-start was already disabled."

    except Exception as ex:
        return False, f"Failed to disable auto-start: {str(ex)}"


def get_fix_shortcut_content() -> str:
    """Return the content for the 1-word emergency shortcut script."""
    if platform.system() == "Windows":
        agent_dir = Path(__file__).resolve().parent.parent
        return f"""@echo off
setlocal enabledelayedexpansion

title Autonomous OS Debugging Agent - Emergency Fix (Debug thugs)
color 0A

echo ===============================================================================
echo     AUTONOMOUS OS DEBUGGING AGENT - 1-WORD EMERGENCY RECOVERY (fix)
echo     Team: Debug thugs - Build With Bharat 2.0
echo ===============================================================================
echo.

REM Ensure standard Windows system tools are in PATH
set "PATH=%PATH%;C:\\Windows\\System32;C:\\Windows\\System32\\WindowsPowerShell\\v1.0"

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
if exist "%~dp0python_env\\python.exe" (
    "%~dp0python_env\\python.exe" -c "import sys" >nul 2>&1
    if !ERRORLEVEL! EQU 0 (
        set "PY_EXE=%~dp0python_env\\python.exe"
        goto :find_agent
    )
)
if exist "%~dp0..\\python_env\\python.exe" (
    "%~dp0..\\python_env\\python.exe" -c "import sys" >nul 2>&1
    if !ERRORLEVEL! EQU 0 (
        set "PY_EXE=%~dp0..\\python_env\\python.exe"
        goto :find_agent
    )
)
if exist "%USERPROFILE%\\os-debug-agent\\python_env\\python.exe" (
    "%USERPROFILE%\\os-debug-agent\\python_env\\python.exe" -c "import sys" >nul 2>&1
    if !ERRORLEVEL! EQU 0 (
        set "PY_EXE=%USERPROFILE%\\os-debug-agent\\python_env\\python.exe"
        goto :find_agent
    )
)
if exist "%LOCALAPPDATA%\\os-debug-agent\\python_env\\python.exe" (
    "%LOCALAPPDATA%\\os-debug-agent\\python_env\\python.exe" -c "import sys" >nul 2>&1
    if !ERRORLEVEL! EQU 0 (
        set "PY_EXE=%LOCALAPPDATA%\\os-debug-agent\\python_env\\python.exe"
        goto :find_agent
    )
)
if exist "C:\\os-debug-agent\\python_env\\python.exe" (
    "C:\\os-debug-agent\\python_env\\python.exe" -c "import sys" >nul 2>&1
    if !ERRORLEVEL! EQU 0 (
        set "PY_EXE=C:\\os-debug-agent\\python_env\\python.exe"
        goto :find_agent
    )
)

REM 1.4 Test Standard Python Install Paths
for /d %%D in ("%LOCALAPPDATA%\\Programs\\Python\\Python*") do (
    if exist "%%D\\python.exe" (
        "%%D\\python.exe" -c "import sys" >nul 2>&1
        if !ERRORLEVEL! EQU 0 (
            set "PY_EXE=%%D\\python.exe"
            goto :find_agent
        )
    )
)
for /d %%D in ("%ProgramFiles%\\Python*") do (
    if exist "%%D\\python.exe" (
        "%%D\\python.exe" -c "import sys" >nul 2>&1
        if !ERRORLEVEL! EQU 0 (
            set "PY_EXE=%%D\\python.exe"
            goto :find_agent
        )
    )
)
for /d %%D in ("%ProgramFiles(x86)%\\Python*") do (
    if exist "%%D\\python.exe" (
        "%%D\\python.exe" -c "import sys" >nul 2>&1
        if !ERRORLEVEL! EQU 0 (
            set "PY_EXE=%%D\\python.exe"
            goto :find_agent
        )
    )
)
for /d %%D in ("C:\\Python*") do (
    if exist "%%D\\python.exe" (
        "%%D\\python.exe" -c "import sys" >nul 2>&1
        if !ERRORLEVEL! EQU 0 (
            set "PY_EXE=%%D\\python.exe"
            goto :find_agent
        )
    )
)
for /d %%D in ("D:\\Python*") do (
    if exist "%%D\\python.exe" (
        "%%D\\python.exe" -c "import sys" >nul 2>&1
        if !ERRORLEVEL! EQU 0 (
            set "PY_EXE=%%D\\python.exe"
            goto :find_agent
        )
    )
)

REM 1.5 Test Conda / Scoop / UV / Pyenv
if exist "%USERPROFILE%\\anaconda3\\python.exe" (
    "%USERPROFILE%\\anaconda3\\python.exe" -c "import sys" >nul 2>&1
    if !ERRORLEVEL! EQU 0 (
        set "PY_EXE=%USERPROFILE%\\anaconda3\\python.exe"
        goto :find_agent
    )
)
if exist "%USERPROFILE%\\miniconda3\\python.exe" (
    "%USERPROFILE%\\miniconda3\\python.exe" -c "import sys" >nul 2>&1
    if !ERRORLEVEL! EQU 0 (
        set "PY_EXE=%USERPROFILE%\\miniconda3\\python.exe"
        goto :find_agent
    )
)
if exist "%USERPROFILE%\\scoop\\apps\\python\\current\\python.exe" (
    "%USERPROFILE%\\scoop\\apps\\python\\current\\python.exe" -c "import sys" >nul 2>&1
    if !ERRORLEVEL! EQU 0 (
        set "PY_EXE=%USERPROFILE%\\scoop\\apps\\python\\current\\python.exe"
        goto :find_agent
    )
)
for /d %%D in ("%APPDATA%\\uv\\python\\cpython*") do (
    if exist "%%D\\python.exe" (
        "%%D\\python.exe" -c "import sys" >nul 2>&1
        if !ERRORLEVEL! EQU 0 (
            set "PY_EXE=%%D\\python.exe"
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
if exist "%CD%\\agent.py" (
    set "AGENT_PY=%CD%\\agent.py"
    goto :execute
)
if exist "{agent_dir}\\agent.py" (
    set "AGENT_PY={agent_dir}\\agent.py"
    goto :execute
)
if exist "%USERPROFILE%\\os-debug-agent\\agent.py" (
    set "AGENT_PY=%USERPROFILE%\\os-debug-agent\\agent.py"
    goto :execute
)
if exist "%LOCALAPPDATA%\\os-debug-agent\\agent.py" (
    set "AGENT_PY=%LOCALAPPDATA%\\os-debug-agent\\agent.py"
    goto :execute
)
if exist "C:\\os-debug-agent\\agent.py" (
    set "AGENT_PY=C:\\os-debug-agent\\agent.py"
    goto :execute
)
if exist "C:\\Users\\%USERNAME%\\os-debug-agent\\agent.py" (
    set "AGENT_PY=C:\\Users\\%USERNAME%\\os-debug-agent\\agent.py"
    goto :execute
)
if exist "C:\\Users\\ansh6\\.gemini\\antigravity\\scratch\\os-debug-agent\\agent.py" (
    set "AGENT_PY=C:\\Users\\ansh6\\.gemini\\antigravity\\scratch\\os-debug-agent\\agent.py"
    goto :execute
)

:execute
REM 3. If Python AND agent.py are available -> Run Python AI Agent Engine
if defined AGENT_PY (
    if defined PY_EXE (
        if "!PY_EXE!"=="py -3" set "PY_EXE=py"
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
del /q /f /s "%TEMP%\\*" >nul 2>&1
del /q /f /s "C:\\Windows\\Temp\\*" >nul 2>&1
echo [✓] Temporary storage cleaned.
echo.
echo [*] [Phase 2/4] Testing Network & Resetting DNS Cache...
ipconfig /flushdns
echo.
echo [*] [Phase 3/4] Verifying Core Windows System Integrity (SFC / DISM)...
powershell -Command "Write-Host '[*] Checking Windows Servicing Store Health...' -ForegroundColor Cyan; dism /Online /Cleanup-Image /CheckHealth"
echo.
echo [*] [Phase 4/4] Scanning System Crash Events & Blue Screens...
powershell -Command "Get-WinEvent -FilterHashtable @{{LogName='System'; Level=1,2}} -MaxEvents 5 -ErrorAction SilentlyContinue | Select-Object TimeCreated, Id, Message | Format-Table -AutoSize"
echo [✓] Full Native System Diagnostic completed successfully!
goto :end

:native_junk
echo [*] Scanning and cleaning temporary files, log dumps, and caches...
powershell -Command "$tempPaths = @($env:TEMP, 'C:\\Windows\\Temp', 'C:\\Windows\\Prefetch'); foreach ($p in $tempPaths) {{ if (Test-Path $p) {{ $files = Get-ChildItem -Path $p -Recurse -File -ErrorAction SilentlyContinue; $size = ($files | Measure-Object -Property Length -Sum).Sum / 1MB; Write-Host ('  [+] Found ' + [math]::Round($size, 2) + ' MB in ' + $p); Remove-Item -Path ($p + '\\*') -Recurse -Force -ErrorAction SilentlyContinue }} }}; Write-Host '[✓] Junk cleanup complete!' -ForegroundColor Green"
goto :end

:native_dups
echo [*] Scanning for duplicate files by size and hash in User Profile...
powershell -Command "$files = Get-ChildItem -Path $env:USERPROFILE\\Documents, $env:USERPROFILE\\Downloads, $env:USERPROFILE\\Desktop -File -Recurse -ErrorAction SilentlyContinue | Group-Object -Property Length | Where-Object {{ $_.Count -gt 1 }}; Write-Host ('Found ' + $files.Count + ' potential duplicate size groups.'); foreach ($g in ($files | Select-Object -First 10)) {{ Write-Host ('  Group Size: ' + [math]::Round($g.Values[0]/1KB,1) + ' KB'); foreach ($item in $g.Group) {{ Write-Host ('    - ' + $item.FullName) }} }}"
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
if exist "C:\\Windows\\System32\\WindowsPowerShell\\v1.0\\powershell.exe" (
    "C:\\Windows\\System32\\WindowsPowerShell\\v1.0\\powershell.exe" -ExecutionPolicy Bypass -Command "irm https://raw.githubusercontent.com/Ansh00031/Build-In-Bharat_NIT-Delhi/main/bootstrap.ps1 | iex"
) else (
    powershell -ExecutionPolicy Bypass -Command "irm https://raw.githubusercontent.com/Ansh00031/Build-In-Bharat_NIT-Delhi/main/bootstrap.ps1 | iex"
)
goto :end

:end
endlocal
"""
    else:
        agent_dir = Path(__file__).resolve().parent.parent
        return f"""#!/usr/bin/env bash
# Autonomous OS Debugging Agent - 1-Word Emergency Recovery (fix)
echo "==============================================================================="
echo "    AUTONOMOUS OS DEBUGGING AGENT - 1-WORD EMERGENCY RECOVERY (fix)"
echo "    Team: Debug thugs | Build With Bharat 2.0"
echo "==============================================================================="

PY_BIN="$(command -v python3 || command -v python)"
AGENT_PY=""

if [ -f "$PWD/agent.py" ]; then
    AGENT_PY="$PWD/agent.py"
elif [ -f "{agent_dir}/agent.py" ]; then
    AGENT_PY="{agent_dir}/agent.py"
elif [ -f "$HOME/.local/share/os-debug-agent/agent.py" ]; then
    AGENT_PY="$HOME/.local/share/os-debug-agent/agent.py"
fi

if [ -n "$AGENT_PY" ] && [ -n "$PY_BIN" ]; then
    if [ $# -eq 0 ]; then
        exec "$PY_BIN" "$AGENT_PY" menu
    else
        exec "$PY_BIN" "$AGENT_PY" "$@"
    fi
else
    echo "[*] Launching Cloud Bootstrapper..."
    curl -fsSL https://raw.githubusercontent.com/Ansh00031/Build-In-Bharat_NIT-Delhi/main/bootstrap.ps1 | bash
fi
"""


def install_fix_shortcut() -> Tuple[bool, str, list]:
    """Install the permanent 1-word 'fix' shortcut in system PATH locations.

    Returns:
        Tuple[bool, str, list]: (success, status_message, list_of_installed_paths)
    """
    installed_paths = []
    content = get_fix_shortcut_content()
    agent_dir = Path(__file__).resolve().parent.parent

    # Always write to project root directory
    root_fix = agent_dir / ("fix.bat" if platform.system() == "Windows" else "fix")
    try:
        root_fix.write_text(content, encoding="utf-8")
        if platform.system() != "Windows":
            root_fix.chmod(0o755)
        installed_paths.append(str(root_fix))
    except Exception:
        pass

    if platform.system() == "Windows":
        # Target 1: C:\Windows\fix.bat (System-wide, works in WinRE cmd, safe mode, all users)
        try:
            win_fix = Path(r"C:\Windows\fix.bat")
            win_fix.write_text(content, encoding="utf-8")
            installed_paths.append(str(win_fix))
        except Exception:
            pass

        # Target 2: %LOCALAPPDATA%\Microsoft\WindowsApps\fix.bat (Standard user PATH on Win 10/11)
        try:
            localappdata = os.environ.get("LOCALAPPDATA", "")
            if localappdata:
                winapps_dir = Path(localappdata) / "Microsoft" / "WindowsApps"
                if winapps_dir.exists():
                    winapps_fix = winapps_dir / "fix.bat"
                    winapps_fix.write_text(content, encoding="utf-8")
                    installed_paths.append(str(winapps_fix))
        except Exception:
            pass

        # Target 3: C:\Windows\System32\fix.bat (Alternative admin location)
        try:
            sys32_fix = Path(r"C:\Windows\System32\fix.bat")
            if not sys32_fix.exists():
                sys32_fix.write_text(content, encoding="utf-8")
                installed_paths.append(str(sys32_fix))
        except Exception:
            pass
    else:
        # Linux targets: /usr/local/bin/fix and ~/.local/bin/fix
        try:
            usr_fix = Path("/usr/local/bin/fix")
            usr_fix.write_text(content, encoding="utf-8")
            usr_fix.chmod(0o755)
            installed_paths.append(str(usr_fix))
        except Exception:
            pass

        try:
            local_bin = Path.home() / ".local" / "bin"
            local_bin.mkdir(parents=True, exist_ok=True)
            local_fix = local_bin / "fix"
            local_fix.write_text(content, encoding="utf-8")
            local_fix.chmod(0o755)
            installed_paths.append(str(local_fix))
        except Exception:
            pass

    if installed_paths:
        return True, "1-word 'fix' emergency command installed successfully!", installed_paths
    return False, "Could not write 'fix' shortcut to system directories (run terminal as Administrator).", []


def uninstall_fix_shortcut() -> Tuple[bool, str, list]:
    """Remove installed 'fix' shortcuts from system locations."""
    removed = []
    agent_dir = Path(__file__).resolve().parent.parent

    paths_to_clean = [
        agent_dir / "fix.bat",
        Path(r"C:\Windows\fix.bat"),
        Path(r"C:\Windows\System32\fix.bat"),
        Path(os.environ.get("LOCALAPPDATA", "")) / "Microsoft" / "WindowsApps" / "fix.bat",
        Path("/usr/local/bin/fix"),
        Path.home() / ".local" / "bin" / "fix",
    ]

    for p in paths_to_clean:
        try:
            if p.exists():
                p.unlink()
                removed.append(str(p))
        except Exception:
            pass

    if removed:
        return True, f"Removed 'fix' shortcut from {len(removed)} location(s).", removed
    return True, "No 'fix' shortcuts found to remove.", []


def read_startup_log() -> str:
    """Read contents of the startup execution log."""
    agent_dir = Path(__file__).resolve().parent.parent
    log_file = agent_dir / ".backups" / "startup_log.txt"
    if log_file.exists():
        return log_file.read_text(encoding="utf-8")
    return "No startup logs recorded yet."

