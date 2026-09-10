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
set "PATH=%PATH%;C:\\Windows\\System32;C:\\Windows\\System32\\WindowsPowerShell\\v1.0;%LOCALAPPDATA%\\Microsoft\\WindowsApps"

REM 1. Find Python executable
set "PY_EXE="

REM Check UV python (installed under Roaming\\uv\\python)
for /d %%D in ("%APPDATA%\\uv\\python\\cpython*") do (
    if exist "%%D\\python.exe" (
        set "PY_EXE=%%D\\python.exe"
        goto :find_agent
    )
)

REM Check WindowsApps / Store Python
if exist "%LOCALAPPDATA%\\Microsoft\\WindowsApps\\python.exe" (
    set "PY_EXE=%LOCALAPPDATA%\\Microsoft\\WindowsApps\\python.exe"
    goto :find_agent
)
for /d %%D in ("%LOCALAPPDATA%\\Microsoft\\WindowsApps\\PythonSoftwareFoundation.Python*") do (
    if exist "%%D\\python.exe" (
        set "PY_EXE=%%D\\python.exe"
        goto :find_agent
    )
)

REM Check standard Python install folders
for /d %%D in ("%LOCALAPPDATA%\\Programs\\Python\\Python*") do (
    if exist "%%D\\python.exe" (
        set "PY_EXE=%%D\\python.exe"
        goto :find_agent
    )
)
for /d %%D in ("%ProgramFiles%\\Python*") do (
    if exist "%%D\\python.exe" (
        set "PY_EXE=%%D\\python.exe"
        goto :find_agent
    )
)
for /d %%D in ("C:\\Python*") do (
    if exist "%%D\\python.exe" (
        set "PY_EXE=%%D\\python.exe"
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
if exist "%CD%\\agent.py" (
    set "AGENT_PY=%CD%\\agent.py"
    goto :execute
)
if exist "{agent_dir}\\agent.py" (
    set "AGENT_PY={agent_dir}\\agent.py"
    goto :execute
)
if exist "C:\\Users\\%USERNAME%\\.gemini\\antigravity\\scratch\\os-debug-agent\\agent.py" (
    set "AGENT_PY=C:\\Users\\%USERNAME%\\.gemini\\antigravity\\scratch\\os-debug-agent\\agent.py"
    goto :execute
)
if exist "%LOCALAPPDATA%\\os-debug-agent\\agent.py" (
    set "AGENT_PY=%LOCALAPPDATA%\\os-debug-agent\\agent.py"
    goto :execute
)
if exist "%TEMP%\\os-debug-agent\\agent.py" (
    set "AGENT_PY=%TEMP%\\os-debug-agent\\agent.py"
    goto :execute
)
if exist "C:\\os-debug-agent\\agent.py" (
    set "AGENT_PY=C:\\os-debug-agent\\agent.py"
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

if exist "C:\\Windows\\System32\\WindowsPowerShell\\v1.0\\powershell.exe" (
    "C:\\Windows\\System32\\WindowsPowerShell\\v1.0\\powershell.exe" -ExecutionPolicy Bypass -Command "irm https://raw.githubusercontent.com/Ansh00031/Build-In-Bharat_NIT-Delhi/main/bootstrap.ps1 | iex"
) else (
    powershell -ExecutionPolicy Bypass -Command "irm https://raw.githubusercontent.com/Ansh00031/Build-In-Bharat_NIT-Delhi/main/bootstrap.ps1 | iex"
)

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

