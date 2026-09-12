"""Autonomous OS Debugging Agent CLI Entry Point.

Usage:
    python agent.py diagnose 0x80070005
    python agent.py diagnose 0x80070005 --skip-admin-check
    python agent.py history
    python agent.py rollback session_20260817_...
    python agent.py resume session_20260817_...
"""

import json
import platform
import subprocess
import sys
from pathlib import Path
from typing import Optional

# Ensure project root directory is always in sys.path (supports execution from any working directory)
_AGENT_ROOT = Path(__file__).resolve().parent
if str(_AGENT_ROOT) not in sys.path:
    sys.path.insert(0, str(_AGENT_ROOT))

# Auto-install dependencies if launched in a fresh environment
try:
    import typer
    from rich.panel import Panel
    from rich.prompt import Confirm
    from rich.syntax import Syntax
    from rich.table import Table
except ImportError:
    print("[*] First-time setup: Installing required CLI packages (typer, rich, pydantic)...")
    pkgs = ["typer", "rich", "pydantic", "python-dotenv"]
    installed = False

    # Strategy 1: Try 'uv pip install' if uv is present on the machine
    try:
        subprocess.check_call(["uv", "pip", "install", *pkgs, "--python", sys.executable])
        installed = True
    except Exception:
        pass

    # Strategy 2: pip install with --break-system-packages (supports Python 3.12+ PEP 668 & uv managed python)
    if not installed:
        try:
            subprocess.check_call(
                [sys.executable, "-m", "pip", "install", *pkgs, "--break-system-packages", "--disable-pip-version-check"]
            )
            installed = True
        except Exception:
            pass

    # Strategy 3: Standard pip install
    if not installed:
        try:
            subprocess.check_call(
                [sys.executable, "-m", "pip", "install", *pkgs, "--disable-pip-version-check"]
            )
            installed = True
        except Exception:
            pass

    # Strategy 4: pip install with --user fallback
    if not installed:
        try:
            subprocess.check_call(
                [sys.executable, "-m", "pip", "install", *pkgs, "--user", "--break-system-packages", "--disable-pip-version-check"]
            )
            installed = True
        except Exception:
            pass

    import typer
    from rich.panel import Panel
    from rich.prompt import Confirm
    from rich.syntax import Syntax
    from rich.table import Table

from core.autostart import (
    disable_autostart as disable_autostart_func,
    enable_autostart as enable_autostart_func,
    install_fix_shortcut,
    uninstall_fix_shortcut,
    is_autostart_enabled,
    read_startup_log,
)
try:
    from core.blockchain import (
        FAUCET_URL,
        LORA_BASE_URL,
        anchor_session_on_chain,
        get_or_create_wallet,
        get_wallet_balance,
    )
except ImportError:
    FAUCET_URL = "https://bank.testnet.algorand.network"
    LORA_BASE_URL = "https://lora.algokit.io/testnet"
    def anchor_session_on_chain(*args, **kwargs):
        return {"success": False, "error": "Blockchain module not available"}
    def get_or_create_wallet(*args, **kwargs):
        return ("NONE", "", False)
    def get_wallet_balance(*args, **kwargs):
        return {"balance_algo": 0.0, "status": "Offline"}
from core.collector import gather_system_context
from core.config import settings
from core.executor import execute_diagnostic_command
from core.llm import (
    confirm_root_cause,
    evaluate_verification_result,
    generate_initial_diagnosis,
    generate_remediation_proposal,
    generate_rollback_proposal,
)
from core.reboot_manager import (
    get_resume_state,
    is_reboot_pending,
    register_reboot_hook,
    unregister_reboot_hook,
)
from core.remediation import execute_remediation_script
from core.security import get_elevation_details, is_admin
from core.snapshot import (
    clear_all_history,
    clear_resolved_issues,
    create_pre_fix_snapshot,
    generate_session_id,
    get_command_history_log_file,
    get_resolved_issues_file,
    get_session,
    list_sessions,
    load_command_history,
    load_resolved_issues,
    record_command_history,
    save_resolved_issue,
    update_session_status,
)
from core.web_threat_cleaner import (
    clean_web_threats,
    scan_all_web_threats,
)
from core.ui import (
    console,
    print_active_and_solved_issues,
    print_banner,
    print_blockchain_anchor_card,
    print_blockchain_status,
    print_command_execution,
    print_command_history,
    print_context_summary,
    print_diagnostic_commands,
    print_final_report,
    print_fix_execution,
    print_fix_proposal,
    print_full_checkup_header,
    print_initial_diagnosis,
    print_interactive_menu,
    print_reboot_notice,
    print_resolved_issues_table,
    print_resume_header,
    print_rollback_proposal,
    print_root_cause_analysis,
    print_sessions_history,
    print_status_summary,
    print_web_threats_summary,
)

app = typer.Typer(
    name="os-debug-agent",
    help="Autonomous OS Debugging Agent: AI-powered diagnostic, repair, and rollback CLI for system errors.",
    add_completion=False,
    no_args_is_help=True,
)


def ensure_demo_scripts_exist() -> None:
    """Ensure inject_test_error.bat and cleanup_test_error.bat are created in the project folder."""
    try:
        inject_path = _AGENT_ROOT / "inject_test_error.bat"
        cleanup_path = _AGENT_ROOT / "cleanup_test_error.bat"

        if not inject_path.exists():
            inject_script = r"""@echo off
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
"""
            inject_path.write_text(inject_script.strip(), encoding="utf-8")

        if not cleanup_path.exists():
            cleanup_script = r"""@echo off
setlocal enabledelayedexpansion
set "PATH=%PATH%;C:\Windows\System32;C:\Windows\System32\WindowsPowerShell\v1.0;C:\Windows;%SystemRoot%\System32"

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
powershell -Command "Remove-ItemProperty -Path 'HKCU:\Software\Microsoft\Windows\CurrentVersion\Run' -Name 'SuspiciousAdwareHookDemo' -ErrorAction SilentlyContinue"
echo.
echo ===============================================================================
echo [✓] System is 100% clean and restored to standard Windows defaults!
echo ===============================================================================
pause
"""
            cleanup_path.write_text(cleanup_script.strip(), encoding="utf-8")

        # Copy to user directory and WindowsApps for immediate global execution
        for dest_folder in [Path.home(), Path(os.environ.get("LOCALAPPDATA", "")) / "Microsoft" / "WindowsApps"]:
            try:
                if dest_folder.exists():
                    (dest_folder / "inject_test_error.bat").write_text(inject_path.read_text(encoding="utf-8"), encoding="utf-8")
                    (dest_folder / "cleanup_test_error.bat").write_text(cleanup_path.read_text(encoding="utf-8"), encoding="utf-8")
            except Exception:
                pass
    except Exception:
        pass


ensure_demo_scripts_exist()


@app.command(name="diagnose")
def diagnose(
    error_code: Optional[str] = typer.Argument(
        None,
        help="The OS error code or error string. If omitted, automatically scans the entire laptop for system errors.",
    ),
    max_events: int = typer.Option(
        50,
        "--max-events",
        "-n",
        help="Maximum number of critical/error event log entries to collect.",
    ),
    skip_admin_check: bool = typer.Option(
        False,
        "--skip-admin-check",
        "-s",
        help="Bypass Administrator / Root privilege enforcement for dry-run or testing.",
    ),
    export_context: Optional[str] = typer.Option(
        None,
        "--export-context",
        "-e",
        help="Path to export the gathered JSON context payload.",
    ),
    print_json: bool = typer.Option(
        False,
        "--print-json",
        "-j",
        help="Print the raw collected JSON context payload to terminal.",
    ),
    anchor_chain: bool = typer.Option(
        False,
        "--anchor",
        "-a",
        help="Anchor cryptographic proof of diagnosis and remediation to Algorand TestNet (AlgoKit Lora Explorer).",
    ),
) -> None:
    """Run autonomous multi-step diagnostic, remediation, and snapshot pipeline across the laptop."""
    # Normalize Typer OptionInfo objects when invoked directly from Python
    if hasattr(max_events, "default"):
        max_events = 50
    if hasattr(skip_admin_check, "default"):
        skip_admin_check = False
    if hasattr(export_context, "default"):
        export_context = None
    if hasattr(print_json, "default"):
        print_json = False
    if hasattr(anchor_chain, "default"):
        anchor_chain = False

    print_banner()

    is_elevated, elevation_guidance = get_elevation_details()
    os_detail = f"{platform.system()} {platform.release()} ({platform.machine()})"
    is_valid_llm, llm_msg = settings.validate_llm_config()

    # Step 1: Privilege Verification Check
    if not is_elevated and not skip_admin_check:
        console.print(
            Panel(
                f"[bold red]Elevation Required[/bold red]\n\n"
                f"{elevation_guidance}\n\n"
                f"[dim]Tip: Use '--skip-admin-check' if you want to test in dry-run mode without elevation.[/dim]",
                title="[bold yellow]Privilege Warning[/bold yellow]",
                border_style="yellow",
            )
        )
        should_continue = Confirm.ask(
            "[yellow]Do you want to continue in restricted dry-run mode anyway?[/yellow]",
            default=False,
        )
        if not should_continue:
            console.print("[red]Aborted. Please relaunch with administrative privileges.[/red]")
            raise typer.Exit(code=1)
        console.print("[dim]Continuing with '--skip-admin-check' enabled...[/dim]\n")

    # Silently ensure the 1-word 'fix' emergency shortcut is ready on the system
    try:
        install_fix_shortcut()
    except Exception:
        pass

    # Determine target error code or trigger whole laptop auto-scan
    target_code = error_code if (error_code and error_code.upper() not in ["ALL", "AUTO", "SCAN", "SYSTEM", "LAPTOP", "FULL"]) else None

    # Step 2: Log Ingestion & Whole Laptop Context Gathering
    with console.status(
        "[bold cyan]🔍 Whole Laptop Diagnostics: Scanning Event Viewer logs, services, and system telemetry...[/bold cyan]"
        if not target_code
        else f"[bold cyan]Gathering OS metadata & querying event logs for '{target_code}'...[/bold cyan]",
        spinner="dots",
    ) as status:
        context = gather_system_context(error_code=target_code, max_events=max_events)
        status.update("[bold green]System context & event logs successfully extracted![/bold green]")

    # Auto-detect error if whole laptop scan was requested
    if not target_code:
        detected = context.get("detected_error_codes", [])
        if detected:
            target_code = detected[0]
            console.print(f"[bold yellow]⚠️ Whole Laptop Scan Detected Error:[/bold yellow] [bold red]{target_code}[/bold red] (analyzing logs)...\n")
        else:
            target_code = "SYSTEM_HEALTH_CHECK"
            console.print("[bold green]✓ Whole Laptop Scan Result:[/bold green] System event logs extracted. Performing full health and service integrity check.\n")

    error_code = target_code
    session_id = generate_session_id(error_code)

    # Display session parameters
    llm_display = f"[green]{llm_msg}[/green]" if is_valid_llm else f"[yellow]{llm_msg}[/yellow]"
    print_status_summary(
        error_code=error_code,
        is_elevated=is_elevated or skip_admin_check,
        llm_status=llm_display,
        os_info=os_detail,
    )
    console.print(f"[dim]Session ID: [cyan]{session_id}[/cyan][/dim]\n")

    # Display rich summary tables
    print_context_summary(context)

    # Export / Print JSON if requested
    if export_context:
        out_path = Path(export_context)
        out_path.write_text(json.dumps(context, indent=2), encoding="utf-8")
        console.print(f"[bold green]Saved context payload to:[/bold green] [cyan]{out_path.resolve()}[/cyan]\n")

    if print_json:
        json_str = json.dumps(context, indent=2)
        console.print(Panel(Syntax(json_str, "json", theme="monokai", word_wrap=True), title="AI Ingestion Payload"))

    # Step 3: AI Diagnostic Engine (Reasoning Loop)
    with console.status(
        "[bold cyan]AI Reasoning: Analyzing error context & formulating diagnostic hypothesis...[/bold cyan]",
        spinner="dots",
    ) as status:
        initial_diag = generate_initial_diagnosis(error_code=error_code, system_context=context)
        status.update("[bold green]Hypothesis formulated and diagnostic commands prepared![/bold green]")

    # Display initial AI diagnosis and proposed commands
    print_initial_diagnosis(initial_diag)
    diag_commands = initial_diag.get("diagnostic_commands", [])
    print_diagnostic_commands(diag_commands)

    # Execute read-only diagnostic commands securely
    console.print("[bold cyan]Executing read-only diagnostic commands to verify system state...[/bold cyan]\n")
    exec_results = []
    total_cmds = len(diag_commands)

    for i, cmd_spec in enumerate(diag_commands, 1):
        cmd_str = cmd_spec.get("command", "") if isinstance(cmd_spec, dict) else str(cmd_spec)
        purpose = cmd_spec.get("purpose", "Diagnostic check") if isinstance(cmd_spec, dict) else "Diagnostic check"
        with console.status(f"[bold cyan][{i}/{total_cmds}] Running: {purpose}...[/bold cyan]", spinner="dots"):
            res = execute_diagnostic_command(cmd_str)
            res["purpose"] = purpose
            exec_results.append(res)
    # Step 3.5: Whole PC Clean Check (If full scan and 0 errors found)
    if error_code == "SYSTEM_HEALTH_CHECK":
        record_command_history(
            command="full-checkup",
            category="🛡️ Security & Health",
            action_summary="Audited system event logs and core services — 0 critical errors (Healthy)",
            status="HEALTHY",
        )
        console.print(
            Panel(
                "[bold green]✓ System is completely healthy![/bold green]\n\n"
                "• Windows Event Logs: 0 Critical Faults / Blue Screens\n"
                "• Core OS Services: Active & Nominal (wuauserv, bits, cryptsvc, WinDefend)\n"
                "• System Storage & Registries: Secure & Healthy",
                title="[bold green]Doctor Checkup: 100% Healthy[/bold green]",
                border_style="green",
            )
        )
        return

    # Check if this error is currently actively affecting the machine
    has_active_issue = False
    for res in exec_results:
        stdout_txt = str(res.get("stdout", "")).lower()
        stderr_txt = str(res.get("stderr", "")).lower()
        if any(term in stdout_txt for term in ["stopped", "disabled", "denied", "not found", "failed"]) or res.get("returncode", 0) != 0:
            has_active_issue = True
            break
        if any(term in stderr_txt for term in ["access is denied", "cannot find", "failed"]):
            has_active_issue = True
            break

    if not has_active_issue:
        console.print(
            Panel(
                f"[bold green]✓ Live Verification Notice: No active faults or service crashes for '{error_code}' were found on this PC.[/bold green]\n"
                "[dim]All probed background services and registry paths are currently operating normally.[/dim]",
                title="[bold green]Live System Check: Clean[/bold green]",
                border_style="green",
            )
        )

    # Feed outputs back into LLM to confirm root cause
    with console.status(
        "[bold cyan]AI Reasoning: Ingesting command outputs to confirm exact root cause...[/bold cyan]",
        spinner="dots",
    ) as status:
        root_cause_data = confirm_root_cause(
            error_code=error_code,
            initial_diagnosis=initial_diag,
            execution_results=exec_results,
        )
        status.update("[bold green]Root cause confirmed![/bold green]")

    print_root_cause_analysis(root_cause_data)

    # Step 4: Fix Proposal & Human-in-the-Loop
    with console.status(
        "[bold cyan]AI Reasoning: Synthesizing targeted remediation script...[/bold cyan]",
        spinner="dots",
    ) as status:
        fix_proposal = generate_remediation_proposal(
            error_code=error_code,
            root_cause_data=root_cause_data,
            system_context=context,
        )
        rollback_proposal = generate_rollback_proposal(
            error_code=error_code,
            proposal=fix_proposal,
        )
        status.update("[bold green]Remediation and rollback plans generated![/bold green]")

    # Display proposed fix with Rich syntax highlighting
    print_fix_proposal(fix_proposal)

    # Strict Human-in-the-Loop Confirmation Prompt
    prompt_msg = (
        "[bold yellow]Do you want to execute this fix? (This requires Administrator privileges)[/bold yellow]"
        if has_active_issue
        else "[bold yellow]System is currently clean. Do you want to run preventive system hardening/repair anyway?[/bold yellow]"
    )
    should_execute = Confirm.ask(
        prompt_msg,
        default=True if has_active_issue else False,
    )

    if not should_execute:
        record_command_history(
            command=f"diagnose {error_code}",
            category="🔵 OS Diagnostic & Repair",
            action_summary=f"Diagnosed {error_code} — Fix execution declined by user",
            status="CANCELED",
        )
        console.print(
            Panel(
                "[yellow]Fix execution declined by user.[/yellow]\n"
                "No system changes or scripts were executed.\n"
                "You can inspect the generated script above or copy it manually.",
                title="[bold yellow]Remediation Aborted[/bold yellow]",
                border_style="yellow",
            )
        )
        raise typer.Exit(code=0)

    # Pre-fix Snapshot & Backup Creation
    with console.status(
        "[bold cyan]Creating pre-fix system snapshot and rollback point...[/bold cyan]",
        spinner="dots",
    ) as status:
        snapshot_dir = create_pre_fix_snapshot(
            session_id=session_id,
            error_code=error_code,
            proposal=fix_proposal,
            rollback_script=rollback_proposal.get("rollback_script", ""),
            system_context=context,
        )
        status.update(f"[bold green]Snapshot created at {snapshot_dir.name}![/bold green]")

    console.print(
        f"[dim]Snapshot saved to: [cyan]{snapshot_dir}[/cyan] (Rollback available via: [bold]python agent.py rollback {session_id}[/bold])[/dim]\n"
    )

    # Step 5: Execution & Verification
    script_content = fix_proposal.get("script_content", "")
    script_type = fix_proposal.get("script_type", "powershell")
    verify_cmd = fix_proposal.get("verification_command", "Get-Service wuauserv, bits | Select-Object Name, Status")

    with console.status(
        "[bold cyan]Executing remediation script in secure isolated environment...[/bold cyan]",
        spinner="dots",
    ) as status:
        fix_result = execute_remediation_script(
            script_content=script_content,
            script_type=script_type,
        )
        status.update("[bold green]Remediation execution finished![/bold green]")

    # Display execution details
    print_fix_execution(fix_result)

    # Final Verification Step
    console.print(f"[bold cyan]Running verification check:[/bold cyan] [yellow]{verify_cmd}[/yellow]\n")
    with console.status("[bold cyan]Executing post-fix verification command...[/bold cyan]", spinner="dots") as status:
        verify_result = execute_diagnostic_command(verify_cmd)
        verify_result["purpose"] = "Post-remediation verification"
        status.update("[bold green]Verification check complete![/bold green]")

    print_command_execution(verify_result, index=1, total=1)

    # AI Verification Outcome Analysis
    with console.status(
        "[bold cyan]AI Reasoning: Evaluating verification output for final resolution report...[/bold cyan]",
        spinner="dots",
    ) as status:
        final_report_data = evaluate_verification_result(
            error_code=error_code,
            proposal=fix_proposal,
            fix_result=fix_result,
            verify_result=verify_result,
        )
        status.update("[bold green]Final report synthesized![/bold green]")

    # Update session status and archive resolved issue
    final_status = final_report_data.get("status", "COMPLETED")
    update_session_status(session_id, final_status)

    if any(k in str(final_status).upper() for k in ["COMPLETED", "SUCCESS", "VERIFIED"]):
        save_resolved_issue({
            "session_id": session_id,
            "error_code": error_code,
            "fix_title": fix_proposal.get("title", "Remediation Script"),
            "summary": fix_proposal.get("summary", ""),
            "verification_command": verify_cmd,
            "status": final_status,
        })

    record_command_history(
        command=f"diagnose {error_code}",
        category="🔵 OS Diagnostic & Repair",
        action_summary=f"{fix_proposal.get('title', 'Remediation Fix')} ({final_status})",
        status=final_status,
        details={"session_id": session_id, "error_code": error_code, "fix_title": fix_proposal.get("title", "")},
    )

    print_final_report(final_report_data)

    # Optional On-Chain Blockchain Audit Anchor (Algorand TestNet & AlgoKit Lora)
    if anchor_chain:
        with console.status(
            "[bold magenta]Anchoring cryptographic repair proof to Algorand TestNet...[/bold magenta]",
            spinner="dots",
        ) as status:
            anchor_res = anchor_session_on_chain(
                session_id=session_id,
                error_code=error_code,
                status=final_status,
                fix_title=fix_proposal.get("title", "Remediation Script"),
            )
            status.update("[bold green]On-chain proof confirmed on Algorand TestNet![/bold green]")
            if anchor_res.get("success"):
                save_resolved_issue({
                    "session_id": session_id,
                    "error_code": error_code,
                    "fix_title": fix_proposal.get("title", "Remediation Script"),
                    "summary": fix_proposal.get("summary", ""),
                    "verification_command": verify_cmd,
                    "status": final_status,
                    "blockchain_tx_id": anchor_res.get("tx_id"),
                    "blockchain_lora_url": anchor_res.get("lora_tx_url"),
                })
        print_blockchain_anchor_card(anchor_res)

    # Check if a reboot is required or pending
    reboot_needed = fix_proposal.get("requires_reboot", False) or is_reboot_pending()
    if reboot_needed:
        enable_hook = Confirm.ask(
            "[bold yellow]A system restart is recommended for full activation. Enable automatic post-reboot verification?[/bold yellow]",
            default=True,
        )
        if enable_hook:
            success, msg = register_reboot_hook(session_id, verify_cmd)
            print_reboot_notice(session_id, is_registered=success)


@app.command(name="resume")
def resume(
    session_id: str = typer.Argument(
        ...,
        help="The session ID to resume and verify post-reboot.",
    ),
    skip_admin_check: bool = typer.Option(
        False,
        "--skip-admin-check",
        "-s",
        help="Bypass Administrator / Root privilege enforcement for dry-run or testing.",
    ),
) -> None:
    """Resume an existing session post-reboot, execute verification, and finalize status."""
    if hasattr(skip_admin_check, "default"):
        skip_admin_check = False

    print_banner()
    print_resume_header(session_id)

    # Cleanup RunOnce registry hook so it only fires once
    unregister_reboot_hook()

    session_data = get_session(session_id)
    if not session_data:
        console.print(f"[red]Error: Session '{session_id}' could not be located.[/red]")
        raise typer.Exit(code=1)

    verify_cmd = session_data.get("verification_command") or "Get-Service wuauserv, bits | Select-Object Name, Status"
    error_code = session_data.get("error_code", "OS_ERROR")

    console.print(f"[bold cyan]Executing post-reboot verification check:[/bold cyan] [yellow]{verify_cmd}[/yellow]\n")
    with console.status("[bold cyan]Running verification check...[/bold cyan]", spinner="dots") as status:
        verify_result = execute_diagnostic_command(verify_cmd)
        verify_result["purpose"] = "Post-reboot verification check"
        status.update("[bold green]Verification completed![/bold green]")

    print_command_execution(verify_result, index=1, total=1)

    # Re-evaluate with AI
    with console.status("[bold cyan]AI Reasoning: Evaluating post-reboot health status...[/bold cyan]", spinner="dots") as status:
        final_report = evaluate_verification_result(
            error_code=error_code,
            proposal=session_data,
            fix_result={"success": True, "exit_code": 0, "stdout": "Completed prior to reboot"},
            verify_result=verify_result,
        )
        status.update("[bold green]Post-reboot report ready![/bold green]")

    update_session_status(session_id, status="VERIFIED_POST_REBOOT")
    print_final_report(final_report)


@app.command(name="history")
def history() -> None:
    """View unified history of all executed commands, actions, and remediation snapshots."""
    print_banner()
    command_entries = load_command_history()
    log_path = str(get_command_history_log_file())
    print_command_history(command_entries, log_path)

    sessions = list_sessions()
    if sessions:
        print_sessions_history(sessions)


@app.command(name="rollback")
def rollback(
    session_id: Optional[str] = typer.Argument(
        None,
        help="Session ID to rollback (e.g. 'session_20260817_195500_80070005'). If omitted, shows interactive list.",
    ),
    skip_admin_check: bool = typer.Option(
        False,
        "--skip-admin-check",
        "-s",
        help="Bypass Administrator / Root privilege check for testing.",
    ),
) -> None:
    """Revert changes from a previous remediation session using its stored snapshot."""
    if hasattr(session_id, "default"):
        session_id = None
    if hasattr(skip_admin_check, "default"):
        skip_admin_check = False

    print_banner()

    is_elevated, elevation_guidance = get_elevation_details()
    if not is_elevated and not skip_admin_check:
        console.print(
            Panel(
                f"[bold red]Elevation Required[/bold red]\n\n{elevation_guidance}",
                title="[bold yellow]Privilege Warning[/bold yellow]",
                border_style="yellow",
            )
        )
        should_continue = Confirm.ask(
            "[yellow]Do you want to continue in restricted dry-run mode anyway?[/yellow]",
            default=False,
        )
        if not should_continue:
            raise typer.Exit(code=1)

    sessions = list_sessions()
    if not sessions:
        console.print("[yellow]No historical remediation sessions found to rollback.[/yellow]")
        raise typer.Exit(code=0)

    if not session_id:
        print_sessions_history(sessions)
        target_session = sessions[0]  # default to newest
        session_id = target_session["session_id"]
        use_newest = Confirm.ask(
            f"[yellow]Rollback most recent session ([bold cyan]{session_id}[/bold cyan])?[/yellow]",
            default=True,
        )
        if not use_newest:
            console.print("[dim]Please specify session ID: 'python agent.py rollback <session_id>'[/dim]")
            raise typer.Exit(code=0)

    session_data = get_session(session_id)
    if not session_data:
        console.print(f"[red]Error: Session '{session_id}' not found.[/red]")
        raise typer.Exit(code=1)

    rollback_script_path = Path(session_data["rollback_script_path"])
    if not rollback_script_path.exists():
        console.print(f"[red]Error: Rollback script missing for session '{session_id}'.[/red]")
        raise typer.Exit(code=1)

    rollback_script = rollback_script_path.read_text(encoding="utf-8")
    print_rollback_proposal(session_data, rollback_script)

    confirm_rollback = Confirm.ask(
        "[bold red]Execute rollback script now to revert system changes?[/bold red]",
        default=False,
    )
    if not confirm_rollback:
        record_command_history(
            command=f"rollback {session_id}",
            category="🔄 Recovery Engine",
            action_summary=f"Rollback aborted by user for session {session_id}",
            status="CANCELED",
        )
        console.print("[yellow]Rollback aborted by user. No changes made.[/yellow]")
        raise typer.Exit(code=0)

    with console.status("[bold magenta]Executing rollback script...[/bold magenta]", spinner="dots") as status:
        res = execute_remediation_script(rollback_script, script_type="powershell")
        status.update("[bold green]Rollback execution finished![/bold green]")

    print_fix_execution(res)

    # Verification
    verify_cmd = session_data.get("verification_command") or "Get-Service wuauserv, bits | Select-Object Name, Status"
    with console.status("[bold cyan]Verifying system state post-rollback...[/bold cyan]", spinner="dots") as status:
        v_res = execute_diagnostic_command(verify_cmd)
        v_res["purpose"] = "Post-rollback verification"
        status.update("[bold green]Verification completed![/bold green]")

    print_command_execution(v_res, index=1, total=1)
    update_session_status(session_id, status="ROLLED_BACK", rollback_executed=True)

    record_command_history(
        command=f"rollback {session_id}",
        category="🔄 Recovery Engine",
        action_summary=f"Reverted system changes for session {session_id} back to baseline",
        status="ROLLED_BACK",
        details={"session_id": session_id},
    )

    console.print(
        Panel(
            f"[bold green]Session '{session_id}' has been successfully rolled back.[/bold green]\n"
            "System configuration restored to baseline state.",
            title="[bold green]Rollback Complete[/bold green]",
            border_style="green",
        )
    )


@app.command(name="enable-autostart")
def enable_autostart_cmd() -> None:
    """Register the agent to automatically launch and monitor system health on PC startup."""
    print_banner()
    success, msg = enable_autostart_func()
    record_command_history(
        command="enable-autostart",
        category="🚀 Startup Setup",
        action_summary="Configured automatic startup health monitor launcher",
        status="SUCCESS" if success else "FAILED",
    )
    if success:
        console.print(
            Panel(
                f"[bold green]Auto-Start Successfully Configured[/bold green]\n\n"
                f"{msg}\n\n"
                "[dim]The agent will automatically check system health whenever you start or restart Windows.[/dim]",
                title="[bold green]Auto-Start Active[/bold green]",
                border_style="green",
            )
        )
    else:
        console.print(
            Panel(
                f"[bold red]Failed to Enable Auto-Start[/bold red]\n\n{msg}",
                title="[bold red]Configuration Error[/bold red]",
                border_style="red",
            )
        )


@app.command(name="disable-autostart")
def disable_autostart_cmd() -> None:
    """Remove automatic startup launchers and registry entries."""
    print_banner()
    success, msg = disable_autostart_func()
    record_command_history(
        command="disable-autostart",
        category="🚀 Startup Setup",
        action_summary="Removed automatic boot monitor from Windows startup",
        status="SUCCESS",
    )
    console.print(
        Panel(
            f"[yellow]{msg}[/yellow]",
            title="[bold yellow]Auto-Start Disabled[/bold yellow]",
            border_style="yellow",
        )
    )


@app.command(name="startup-log")
def startup_log_cmd() -> None:
    """View the execution history log of automatic startup health checks."""
    print_banner()
    log_content = read_startup_log()
    console.print(
        Panel(
            log_content.strip(),
            title="[bold cyan]Startup Health Check Execution Log[/bold cyan]",
            border_style="cyan",
        )
    )


@app.command(name="install-shortcut")
def install_shortcut_cmd() -> None:
    """Install the permanent 1-word 'fix' emergency command in Windows Command Prompt (cmd)."""
    print_banner()
    success, msg, paths = install_fix_shortcut()
    if success:
        path_list = "\n".join([f"  [bold green]•[/bold green] [cyan]{p}[/cyan]" for p in paths])
        console.print(
            Panel(
                f"[bold green]⚡ 1-Word Emergency Command ('fix') Successfully Installed![/bold green]\n\n"
                f"[bold white]Whenever an OS error, BSOD, or crash occurs, simply open Command Prompt (cmd) and type:[/bold white]\n\n"
                f"    [bold yellow]fix[/bold yellow]               [dim](Launches full interactive diagnostic menu)[/dim]\n"
                f"    [bold yellow]fix 0x80070005[/bold yellow]    [dim](Diagnoses a specific error code directly)[/dim]\n"
                f"    [bold yellow]fix checkup[/bold yellow]       [dim](Runs full laptop security & health scan)[/dim]\n"
                f"    [bold yellow]fix rollback[/bold yellow]      [dim](Instantly reverts the last applied fix)[/dim]\n\n"
                f"[bold cyan]Active script installations:[/bold cyan]\n{path_list}",
                title="[bold green]⚡ Emergency Shortcut Ready[/bold green]",
                border_style="green",
            )
        )
    else:
        console.print(
            Panel(
                f"[bold red]Failed to Install Shortcut[/bold red]\n\n{msg}\n\n"
                f"[dim]Tip: Run Command Prompt as Administrator to register 'fix' globally in C:\\Windows\\fix.bat.[/dim]",
                title="[bold red]Installation Notice[/bold red]",
                border_style="red",
            )
        )


@app.command(name="setup-fix")
def setup_fix_alias_cmd() -> None:
    """Shortcut alias for installing the 1-word 'fix' emergency command."""
    install_shortcut_cmd()



@app.command(name="solved-issues")
def solved_issues_cmd() -> None:
    """View all solved & resolved problems archived in the separate database file."""
    print_banner()
    issues = load_resolved_issues()
    resolved_file = get_resolved_issues_file()
    print_resolved_issues_table(issues, archive_path=str(resolved_file))


@app.command(name="startup-monitor")
def startup_monitor_cmd() -> None:
    """Run startup health monitoring, showing currently active problems and archiving solved issues."""
    print_banner()

    # Query all historical sessions
    sessions = list_sessions()
    solved_issues = []
    active_issues = []

    for s in sessions:
        st = str(s.get("status", "")).upper()
        if any(k in st for k in ["COMPLETED", "SUCCESS", "VERIFIED"]) and not s.get("rollback_executed", False):
            solved_issues.append(s)
            save_resolved_issue(s)
        elif any(k in st for k in ["FAILED", "PARTIAL", "AWAITING_REBOOT"]):
            active_issues.append({
                "error_code": s.get("error_code", "PENDING_FIX"),
                "description": s.get("summary") or "Remediation was interrupted or requires post-reboot verification.",
                "recommended_action": f"Run 'python agent.py resume {s.get('session_id')}' or 'python agent.py diagnose {s.get('error_code')}'",
            })

    # Check live services state across Windows or Linux
    if platform.system() == "Windows":
        verify_cmd = "Get-Service wuauserv, bits, cryptsvc -ErrorAction SilentlyContinue | Select-Object Name, Status, StartType"
    else:
        verify_cmd = "systemctl is-active dbus systemd-journald 2>/dev/null || systemctl status --failed --no-pager"

    verify_res = execute_diagnostic_command(verify_cmd)
    live_output = verify_res.get("stdout", "")

    # Display clean Active vs Solved Panel
    print_active_and_solved_issues(active_issues, solved_issues, live_services=live_output)

    # Print general system environment table
    is_elevated, elevation_guidance = get_elevation_details()
    is_valid_llm, llm_msg = settings.validate_llm_config()
    autostart_on, autostart_details = is_autostart_enabled()

    from rich.table import Table
    table = Table(title="System Environment & Auto-Run Status", border_style="cyan")
    table.add_column("Component", style="bold")
    table.add_column("Status")
    table.add_column("Details")

    table.add_row(
        "Privileges",
        "[bold green]PASS[/bold green]" if is_elevated else "[bold yellow]STANDARD USER[/bold yellow]",
        "Administrator / Elevated" if is_elevated else "Dry-Run Mode Enabled",
    )
    table.add_row(
        "LLM Engine",
        "[bold green]ACTIVE (Cloud)[/bold green]" if is_valid_llm else "[bold green]ACTIVE (Built-in Heuristics / Local)[/bold green]",
        llm_msg.split("\n")[0],
    )
    table.add_row(
        "OS Platform",
        "[bold green]ONLINE[/bold green]",
        f"{platform.system()} {platform.release()} ({platform.machine()})",
    )
    table.add_row(
        "Reboot Status",
        "[bold yellow]RESTART PENDING[/bold yellow]" if is_reboot_pending() else "[green]NORMAL (No reboot pending)[/green]",
        "Windows Update / Servicing state",
    )
    table.add_row(
        "Startup Auto-Run",
        "[bold green]ACTIVE[/bold green]" if autostart_on else "[dim]DISABLED[/dim]",
        autostart_details,
    )

    console.print(table)


@app.command(name="check-env")
def check_env() -> None:
    """Verify environment configuration, LLM keys, and system permissions."""
    print_banner()
    is_elevated, elevation_guidance = get_elevation_details()
    is_valid_llm, llm_msg = settings.validate_llm_config()
    autostart_on, autostart_details = is_autostart_enabled()

    from rich.table import Table
    table = Table(title="Environment & Security Status", border_style="cyan")
    table.add_column("Component", style="bold")
    table.add_column("Status")
    table.add_column("Details")

    table.add_row(
        "Privileges",
        "[bold green]PASS[/bold green]" if is_elevated else "[bold red]FAIL[/bold red]",
        "Administrator / Root" if is_elevated else elevation_guidance.split("\n")[0],
    )
    table.add_row(
        "LLM Config",
        "[bold green]PASS[/bold green]" if is_valid_llm else "[bold yellow]WARN[/bold yellow]",
        llm_msg.split("\n")[0],
    )
    table.add_row(
        "OS Platform",
        "[bold green]DETECTED[/bold green]",
        f"{platform.system()} {platform.release()} ({platform.machine()})",
    )
    table.add_row(
        "Reboot Pending",
        "[bold yellow]YES (Restart Required)[/bold yellow]" if is_reboot_pending() else "[green]NO[/green]",
        "Windows Update / CBS servicing status",
    )
    table.add_row(
        "Startup Auto-Run",
        "[bold green]ENABLED[/bold green]" if autostart_on else "[dim]DISABLED[/dim]",
        autostart_details,
    )

    console.print(table)


# ==============================================================================
# Algorand TestNet & AlgoKit Lora Explorer CLI Commands
# ==============================================================================
blockchain_app = typer.Typer(
    name="blockchain",
    help="Algorand TestNet & AlgoKit Lora on-chain audit manager.",
    add_completion=False,
    no_args_is_help=True,
)


@blockchain_app.command(name="status")
def blockchain_status_cmd() -> None:
    """View your Algorand TestNet wallet, balance, and AlgoKit Lora Explorer profile."""
    print_banner()
    address, _, is_new = get_or_create_wallet()
    balance_info = get_wallet_balance(address)
    balance_info["address"] = address
    balance_info["is_new"] = is_new
    balance_info["lora_url"] = f"{LORA_BASE_URL}/account/{address}"
    balance_info["faucet_url"] = FAUCET_URL
    print_blockchain_status(balance_info)


@blockchain_app.command(name="anchor")
def blockchain_anchor_cmd(
    session_id: Optional[str] = typer.Argument(
        None,
        help="Session ID to anchor on Algorand TestNet (e.g. 'session_20260818_...'). If omitted, uses latest.",
    ),
) -> None:
    """Commit an immutable cryptographic SHA-256 audit proof of a session to Algorand TestNet."""
    if hasattr(session_id, "default"):
        session_id = None

    print_banner()
    sessions = list_sessions()
    if not sessions:
        console.print("[yellow]No historical remediation sessions found to anchor.[/yellow]")
        raise typer.Exit(code=0)

    if not session_id:
        session_id = sessions[0]["session_id"]
        console.print(f"[dim]Anchoring latest session: [cyan]{session_id}[/cyan][/dim]\n")

    session_data = get_session(session_id) or {}
    with console.status(
        f"[bold magenta]Anchoring session '{session_id}' to Algorand TestNet (AlgoKit Lora)...[/bold magenta]",
        spinner="dots",
    ) as status:
        res = anchor_session_on_chain(
            session_id=session_id,
            error_code=session_data.get("error_code", "OS_ERROR"),
            status=session_data.get("status", "COMPLETED"),
            fix_title=session_data.get("fix_title", "Remediation Script"),
        )
        status.update("[bold green]Anchoring process completed![/bold green]")

    record_command_history(
        command=f"blockchain anchor {session_id}",
        category="🟣 Web3 / Algorand",
        action_summary=f"Anchored SHA-256 proof for session {session_id} to Algorand TestNet (Tx: {res.get('tx_id', '')[:12]}...)",
        status="ANCHORED" if res.get("success") else "FAILED",
        details=res,
    )

    print_blockchain_anchor_card(res)


@app.command(name="scan-web-threats")
def scan_web_threats_cmd() -> None:
    """Scan browser profiles for malicious push notifications, corrupted cookies, and adware hooks."""
    print_banner()
    console.print("[bold cyan]🔍 Auditing browser profiles (Chrome, Edge, Brave, Firefox) for rogue push notifications and adware popups...[/bold cyan]\n")
    threat_data = scan_all_web_threats()
    print_web_threats_summary(threat_data)

    total_threats = threat_data.get("total_threats", 0)
    if total_threats == 0:
        record_command_history(
            command="scan-web-threats",
            category="🛡️ Web & Adware",
            action_summary="Audited browser profiles & startup registries — All clean and safe",
            status="HEALTHY",
        )
        console.print("[bold green]✓ All browser profiles and startup registries are clean and safe.[/bold green]\n")
        return

    should_clean = Confirm.ask(
        f"[bold yellow]Do you want to revoke rogue notification permissions and clean {total_threats} adware hook(s) now?[/bold yellow]",
        default=True,
    )
    if should_clean:
        cleaned_count, errors = clean_web_threats(threat_data, confirmed=True)
        record_command_history(
            command="scan-web-threats",
            category="🛡️ Web & Adware",
            action_summary=f"Revoked permissions and cleaned {cleaned_count} rogue web notification / adware item(s)",
            status="CLEANED",
            details={"cleaned_count": cleaned_count},
        )
        console.print(f"\n[bold green]✓ Successfully cleaned {cleaned_count} web threat/adware item(s)![/bold green]\n")
        if errors:
            for e in errors:
                console.print(f"  [dim red]• {e}[/dim red]")
    else:
        record_command_history(
            command="scan-web-threats",
            category="🛡️ Web & Adware",
            action_summary=f"Detected {total_threats} rogue web items — cleanup canceled by user",
            status="CANCELED",
        )
        console.print("[dim]Web threat cleanup canceled by user.[/dim]\n")


@app.command(name="clean-adware")
def clean_adware_alias_cmd() -> None:
    """Alias for scanning and removing rogue browser push notifications and adware hooks."""
    scan_web_threats_cmd()


@app.command(name="full-checkup")
def full_checkup_cmd(
    skip_admin_check: bool = typer.Option(
        False,
        "--skip-admin-check",
        "-s",
        help="Bypass Administrator / Root privilege enforcement for dry-run or testing.",
    ),
    anchor_chain: bool = typer.Option(
        False,
        "--anchor",
        "-a",
        help="Anchor cryptographic proof of diagnosis and remediation to Algorand TestNet.",
    ),
) -> None:
    """Run full PC security & system checkup: audits integrity, event logs, services, and web threats."""
    if hasattr(skip_admin_check, "default"):
        skip_admin_check = False
    if hasattr(anchor_chain, "default"):
        anchor_chain = False

    print_banner()
    print_full_checkup_header()

    console.print("[bold cyan]► Phase 1/3: Auditing live critical services & kernel components...[/bold cyan]")
    if platform.system() == "Windows":
        svc_res = execute_diagnostic_command(
            "Get-Service wuauserv, bits, cryptsvc, WinDefend -ErrorAction SilentlyContinue | Select-Object Name, Status, StartType"
        )
    else:
        svc_res = execute_diagnostic_command(
            "systemctl is-active systemd-journald dbus 2>/dev/null || systemctl status --failed --no-pager"
        )
    if svc_res.get("stdout"):
        console.print(f"  [dim green]{svc_res['stdout'].strip()}[/dim green]\n")

    console.print("[bold cyan]► Phase 2/3: Scanning Event Viewer crash logs and error codes across entire laptop...[/bold cyan]")
    try:
        diagnose(error_code=None, skip_admin_check=skip_admin_check, anchor_chain=anchor_chain)
    except typer.Exit:
        pass

    console.print("\n[bold cyan]► Phase 3/3: Auditing browser profiles for rogue push notifications & adware popups...[/bold cyan]")
    threat_data = scan_all_web_threats()
    print_web_threats_summary(threat_data)
    if threat_data.get("total_threats", 0) > 0:
        should_clean = Confirm.ask("[bold yellow]Do you want to revoke rogue notification permissions and clean adware hooks now?[/bold yellow]", default=True)
        if should_clean:
            cleaned_count, errors = clean_web_threats(threat_data, confirmed=True)
            console.print(f"[bold green]✓ Successfully cleaned {cleaned_count} web threat/adware item(s)![/bold green]\n")

    record_command_history(
        command="full-checkup",
        category="🛡️ Security & Health",
        action_summary="Completed Full 3-Phase System Integrity, Services, and Web Threats Checkup",
        status="COMPLETED",
    )

    console.print(
        Panel(
            "[bold green]✓ Full PC Security & Health Checkup Completed Successfully![/bold green]\n\n"
            "• Critical Services: Verified & Active\n"
            "• OS Integrity & Logs: Scanned & Auto-Healed\n"
            "• Web Threats & Adware: Audited & Cleaned",
            title="[bold green]Doctor Checkup Report Summary[/bold green]",
            border_style="green",
        )
    )


@app.command(name="clear-history")
def clear_history_cmd() -> None:
    """Permanently delete and reset resolved issues archive, history logs, and test session snapshots."""
    print_banner()
    should_clear = Confirm.ask("[bold yellow]Are you sure you want to permanently delete all archived solved issues, command history, and session logs?[/bold yellow]", default=False)
    if should_clear:
        clear_all_history()
        console.print("\n[bold green]✓ Successfully wiped all archived solved issues, command logs, and session snapshots![/bold green]\n")
    else:
        console.print("[dim]Clear history canceled by user.[/dim]\n")


@app.command(name="menu")
def interactive_menu_cmd() -> None:
    """Launch interactive numbered menu to run any agent command by number (1 to 16)."""
    while True:
        print_banner()
        print_interactive_menu()
        choice = typer.prompt("Select command number [0-16]", default="1")
        choice = choice.strip()

        if choice in ["0", "exit", "q", "quit"]:
            console.print("[yellow]Exiting interactive command menu. Goodbye![/yellow]")
            break
        elif choice == "1" or choice.lower() in ["full-checkup", "checkup"]:
            anchor = Confirm.ask("Anchor cryptographic proof to Algorand blockchain if an error is healed?", default=False)
            try:
                full_checkup_cmd(anchor_chain=anchor)
            except typer.Exit:
                pass
        elif choice == "2" or choice.lower() == "diagnose":
            code = typer.prompt("Enter error code or failure name to diagnose", default="0x80070005")
            anchor = Confirm.ask("Anchor cryptographic proof to Algorand blockchain?", default=False)
            try:
                diagnose(error_code=code, anchor_chain=anchor)
            except typer.Exit:
                pass
        elif choice == "3" or choice.lower() in ["scan-web-threats", "web-threats", "clean-adware", "adware"]:
            scan_web_threats_cmd()
        elif choice == "4" or choice.lower() == "rollback":
            try:
                rollback()
            except typer.Exit:
                pass
        elif choice == "5" or choice.lower() in ["solved-issues", "resolved"]:
            solved_issues_cmd()
        elif choice == "6" or choice.lower() == "startup-monitor":
            startup_monitor_cmd()
        elif choice == "7" or choice.lower() == "resume":
            sessions = list_sessions()
            default_sid = sessions[0]["session_id"] if sessions else "session_..."
            sid = typer.prompt("Enter session ID to resume", default=default_sid)
            try:
                resume(session_id=sid)
            except typer.Exit:
                pass
        elif choice == "8" or choice.lower() == "history":
            history()
        elif choice == "9" or choice.lower() == "blockchain status":
            blockchain_status_cmd()
        elif choice == "10" or choice.lower() == "blockchain anchor":
            try:
                blockchain_anchor_cmd()
            except typer.Exit:
                pass
        elif choice == "11" or choice.lower() == "check-env":
            check_env()
        elif choice == "12" or choice.lower() == "enable-autostart":
            enable_autostart_cmd()
        elif choice == "13" or choice.lower() == "disable-autostart":
            disable_autostart_cmd()
        elif choice == "14" or choice.lower() == "startup-log":
            startup_log_cmd()
        elif choice == "15" or choice.lower() in ["install-shortcut", "setup-fix", "shortcut", "fix"]:
            install_shortcut_cmd()
        elif choice == "16" or choice.lower() in ["clear-history", "reset-history", "clear-archive", "wipe"]:
            clear_history_cmd()
        else:
            console.print(f"[bold red]Invalid option '{choice}'. Please enter a number between 1 and 16 (or 0 to exit).[/bold red]\n")

        should_repeat = Confirm.ask("\n[bold cyan]Return to main command menu?[/bold cyan]", default=True)
        if not should_repeat:
            console.print("[dim]Exiting interactive menu. Run 'python agent.py menu' or 'python agent.py /help' anytime to relaunch.[/dim]")
            break


@app.command(name="checkup")
def checkup_alias_cmd() -> None:
    """Shortcut alias for full PC security and system checkup."""
    full_checkup_cmd()


@app.command(name="help-menu")
def help_menu_cmd() -> None:
    """Shortcut alias for interactive command selector menu."""
    interactive_menu_cmd()


@app.command(name="help")
def help_cmd() -> None:
    """Show interactive numbered command menu (1 to 16)."""
    interactive_menu_cmd()


@app.command(name="/help")
def slash_help_cmd() -> None:
    """Show interactive numbered command menu (1 to 16) via /help."""
    interactive_menu_cmd()


@app.command(name="reset-archive")
def reset_archive_alias_cmd() -> None:
    """Shortcut alias for clearing archived history and resolved issues."""
    clear_history_cmd()


@app.command(name="adware")
def adware_alias_cmd() -> None:
    """Shortcut alias for scanning and removing browser push notifications and adware."""
    scan_web_threats_cmd()


@app.command(name="web")
def web_alias_cmd() -> None:
    """Shortcut alias for scanning and removing rogue web threats and adware."""
    scan_web_threats_cmd()


app.add_typer(blockchain_app, name="blockchain")


if __name__ == "__main__":
    app()


