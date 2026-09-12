"""Rich UI utilities for styled CLI output, panels, and spinners."""

from typing import Any, Dict, List, Optional
from rich.console import Console
from rich.panel import Panel
from rich.table import Table
from rich.theme import Theme
from rich.text import Text

custom_theme = Theme({
    "info": "cyan",
    "warning": "yellow",
    "error": "bold red",
    "success": "bold green",
    "highlight": "bold magenta",
    "muted": "dim grey70",
})

console = Console(theme=custom_theme)


def print_banner() -> None:
    """Print the application startup banner."""
    title = Text("Autonomous OS Debugging Agent", style="bold cyan")
    subtitle = Text("AI-Powered System Diagnostics & Automated Remediation", style="dim italic")
    
    content = Text()
    content.append(title)
    content.append("\n")
    content.append(subtitle)
    
    panel = Panel(
        content,
        border_style="cyan",
        padding=(1, 2),
        title="[bold green]v0.1.0[/bold green]",
        title_align="right",
    )
    console.print(panel)


def print_status_summary(
    error_code: str,
    is_elevated: bool,
    llm_status: str,
    os_info: str = "Windows",
) -> None:
    """Print a structured status table for the current diagnostic session."""
    table = Table(title="[bold]Diagnostic Session Parameters[/bold]", border_style="cyan", expand=False)
    table.add_column("Parameter", style="bold", width=22)
    table.add_column("Value", style="cyan")

    table.add_row("Target Error Code", f"[bold yellow]{error_code}[/bold yellow]")
    table.add_row("OS Environment", os_info)
    table.add_row(
        "Privilege Level",
        "[bold green]Administrator (Elevated)[/bold green]"
        if is_elevated
        else "[bold red]Standard User (Not Elevated)[/bold red]",
    )
    table.add_row("LLM Engine", llm_status)

    console.print(table)
    console.print()


def print_context_summary(context: dict) -> None:
    """Display a formatted summary of the gathered OS and Event Log context."""
    os_info = context.get("os_info", {})
    logs_summary = context.get("event_logs_summary", {})
    events = context.get("event_logs", [])

    # OS Info Table
    meta_table = Table(title="[bold]OS Environment Details[/bold]", border_style="blue")
    meta_table.add_column("Property", style="bold")
    meta_table.add_column("Value", style="cyan")

    meta_table.add_row("Operating System", f"{os_info.get('system')} {os_info.get('release')}")
    meta_table.add_row("Kernel / Version", str(os_info.get("version")))
    meta_table.add_row("Architecture", str(os_info.get("architecture")))
    meta_table.add_row("Current User", str(os_info.get("current_user")))
    meta_table.add_row(
        "Privilege Level",
        "[green]Elevated (Administrator)[/green]"
        if os_info.get("is_elevated")
        else "[red]Standard (Non-Elevated)[/red]",
    )

    console.print(meta_table)
    console.print()

    # Event Logs Preview Table
    total_events = logs_summary.get("total_events_captured", 0)
    query_err = logs_summary.get("query_error")

    if query_err:
        console.print(
            Panel(
                f"[yellow]Log extraction notice: {query_err}[/yellow]",
                title="[yellow]Event Log Query Status[/yellow]",
                border_style="yellow",
            )
        )

    log_table = Table(
        title=f"[bold]Captured Event Logs (Total: {total_events})[/bold]",
        border_style="magenta",
    )
    log_table.add_column("Time", style="dim", width=19)
    log_table.add_column("Channel", style="blue", width=15)
    log_table.add_column("Level", style="bold red", width=10)
    log_table.add_column("Event ID", style="cyan", width=8)
    log_table.add_column("Summary Message", style="white")

    if not events:
        log_table.add_row("-", "-", "[yellow]None[/yellow]", "-", "No recent critical/error events recorded.")
    else:
        for evt in events[:5]:  # Preview first 5 in terminal
            msg = evt.get("Message", "")
            if len(msg) > 90:
                msg = msg[:87] + "..."
            log_table.add_row(
                str(evt.get("TimeCreated", "")),
                str(evt.get("Channel", "")),
                str(evt.get("Level", "Error")),
                str(evt.get("Id", "")),
                msg,
            )

    console.print(log_table)
    if total_events > 5:
        console.print(f"[dim italic]... and {total_events - 5} more events included in AI context payload.[/dim italic]\n")
    else:
        console.print()


def print_initial_diagnosis(data: dict) -> None:
    """Print the AI initial diagnostic assessment with threat severity and device harm analysis."""
    error_code = data.get("error_code", "Unknown")
    error_name = data.get("error_name", "SYSTEM_ERROR")
    problem = data.get("problem_statement") or data.get("diagnosis", "No diagnosis provided.")
    likely_causes = data.get("likely_causes", [])
    threat_level = data.get("threat_level", "HIGH (Threat Level 4/5)")
    device_harm = data.get("device_harm", [])
    consequences = data.get("consequence_if_unfixed")

    # Determine Threat Level badge color
    t_upper = str(threat_level).upper()
    if "CRITICAL" in t_upper or "5/5" in t_upper:
        threat_badge = f"[bold red]🔴 {threat_level}[/bold red]"
        box_color = "red"
    elif "HIGH" in t_upper or "4/5" in t_upper or "3.5" in t_upper:
        threat_badge = f"[bold yellow]🟠 {threat_level}[/bold yellow]"
        box_color = "yellow"
    elif "MEDIUM" in t_upper or "3/5" in t_upper:
        threat_badge = f"[bold yellow]🟡 {threat_level}[/bold yellow]"
        box_color = "yellow"
    else:
        threat_badge = f"[bold green]🟢 {threat_level}[/bold green]"
        box_color = "cyan"

    content = f"[bold yellow]{error_code}[/bold yellow] - [bold cyan]{error_name}[/bold cyan]\n"
    content += f"[bold white]Threat Severity Rating:[/bold white] {threat_badge}\n\n"
    content += f"[bold red]► PROBLEM FACING SYSTEM:[/bold red]\n[bold white]{problem}[/bold white]\n"

    if device_harm:
        content += "\n[bold red]⚠️ HOW THIS ERROR HARMS YOUR LAPTOP / SYSTEM:[/bold red]\n"
        if isinstance(device_harm, list):
            for h in device_harm:
                content += f"  [bold red]•[/bold red] [white]{h}[/white]\n"
        else:
            content += f"  [white]{device_harm}[/white]\n"

    if consequences:
        content += f"\n[bold yellow]► RISK IF LEFT UNFIXED:[/bold yellow]\n[dim white]{consequences}[/dim white]\n"

    if likely_causes:
        content += "\n[bold cyan]► Suspected Root Causes:[/bold cyan]\n"
        for cause in likely_causes:
            content += f"  • [dim white]{cause}[/dim white]\n"

    warning = data.get("llm_warning")
    if warning:
        content += f"\n[yellow]Note: {warning}[/yellow]\n"

    console.print(
        Panel(
            content.strip(),
            title="[bold red]🛡️ AI Diagnostic Assessment & Security Threat Analysis[/bold red]",
            border_style=box_color,
        )
    )
    console.print()


def print_diagnostic_commands(commands: list) -> None:
    """Display the AI-generated read-only diagnostic command suite."""
    table = Table(title="[bold]AI Proposed Read-Only Diagnostic Commands[/bold]", border_style="cyan")
    table.add_column("#", style="dim", width=4)
    table.add_column("Purpose", style="bold cyan", width=36)
    table.add_column("Command (PowerShell)", style="yellow")

    for i, item in enumerate(commands, 1):
        cmd = item.get("command", "") if isinstance(item, dict) else str(item)
        purpose = item.get("purpose", "") if isinstance(item, dict) else ""
        table.add_row(str(i), purpose, cmd)

    console.print(table)
    console.print()


def print_command_execution(result: dict, index: int, total: int) -> None:
    """Print stdout/stderr output from a diagnostic command execution."""
    cmd = result.get("command", "")
    purpose = result.get("purpose", "")
    success = result.get("success", False)
    exit_code = result.get("exit_code", 0)
    stdout = result.get("stdout", "")
    stderr = result.get("stderr", "")
    duration = result.get("duration_sec", 0.0)

    status_icon = "[green]✓ SUCCESS[/green]" if success else "[red]✗ FAILED[/red]"
    title = f"[{index}/{total}] {purpose} ({status_icon} | Code: {exit_code} | {duration}s)"

    output_text = ""
    if stdout:
        output_text += f"[bold dim]STDOUT:[/bold dim]\n{stdout}\n"
    if stderr:
        output_text += f"[bold red]STDERR:[/bold red]\n{stderr}\n"
    if not stdout and not stderr:
        output_text += "[dim](No output returned)[/dim]\n"

    console.print(
        Panel(
            output_text.strip(),
            title=f"[cyan]{title}[/cyan]",
            border_style="green" if success else "red",
            subtitle=f"[dim yellow]{cmd}[/dim yellow]",
            subtitle_align="left",
        )
    )
    console.print()


def print_root_cause_analysis(data: dict) -> None:
    """Print the AI confirmed root cause analysis panel."""
    confirmed = data.get("root_cause_confirmed", True)
    analysis = data.get("root_cause_analysis", "")
    evidence = data.get("evidence", [])
    remediation_summary = data.get("remediation_summary", "")

    status_str = "[bold green]CONFIRMED[/bold green]" if confirmed else "[bold yellow]INCONCLUSIVE[/bold yellow]"
    content = f"Root Cause Status: {status_str}\n\n"
    content += f"[bold]Analysis:[/bold]\n{analysis}\n"

    if evidence:
        content += "\n[bold]Key Evidence Detected:[/bold]\n"
        for ev in evidence:
            content += f" • [cyan]{ev}[/cyan]\n"

    if remediation_summary:
        content += f"\n[bold]Remediation Strategy:[/bold]\n[white]{remediation_summary}[/white]\n"

    console.print(
        Panel(
            content.strip(),
            title="[bold magenta]AI Root Cause Confirmation (Step 3 Complete)[/bold magenta]",
            border_style="magenta",
        )
    )
    console.print()


def print_fix_proposal(proposal: dict) -> None:
    """Display the AI proposed remediation plan with syntax-highlighted script."""
    title = proposal.get("title", "Proposed Remediation Plan")
    problem = proposal.get("problem_statement", "System error requires remediation.")
    summary = proposal.get("summary", "No summary provided.")
    steps = proposal.get("steps", [])
    script_content = proposal.get("script_content", "")
    script_type = proposal.get("script_type", "powershell")
    requires_reboot = proposal.get("requires_reboot", False)

    # Explanation Panel
    info_text = f"[bold red]Problem Facing System:[/bold red] [white]{problem}[/white]\n\n"
    info_text += f"[bold]Fix Overview:[/bold] [white]{summary}[/white]\n\n"
    if steps:
        info_text += "[bold]Remediation Actions Executed by Script:[/bold]\n"
        for i, step in enumerate(steps, 1):
            info_text += f" [cyan]{i}.[/cyan] {step}\n"

    if requires_reboot:
        info_text += "\n[bold yellow]⚠ Note: A system reboot may be recommended after applying this fix.[/bold yellow]"

    console.print(
        Panel(
            info_text.strip(),
            title=f"[bold green]Proposed Fix: {title}[/bold green]",
            border_style="green",
        )
    )

    # Syntax Highlighted Code Box
    from rich.syntax import Syntax
    syntax_view = Syntax(
        script_content,
        script_type,
        theme="monokai",
        line_numbers=True,
        word_wrap=True,
    )

    console.print(
        Panel(
            syntax_view,
            title="[bold cyan]Remediation Script Preview (PowerShell)[/bold cyan]",
            border_style="cyan",
        )
    )
    console.print()


def print_fix_execution(result: dict) -> None:
    """Print the execution output of the remediation script."""
    success = result.get("success", False)
    exit_code = result.get("exit_code", 0)
    stdout = result.get("stdout", "")
    stderr = result.get("stderr", "")
    duration = result.get("duration_sec", 0.0)

    status_tag = "[bold green]COMPLETED[/bold green]" if success else "[bold red]FAILED[/bold red]"
    title = f"Remediation Execution Output ({status_tag} | Exit code: {exit_code} | {duration}s)"

    output_text = ""
    if stdout:
        output_text += f"[bold dim]STDOUT:[/bold dim]\n{stdout}\n"
    if stderr:
        output_text += f"[bold red]STDERR:[/bold red]\n{stderr}\n"
    if not stdout and not stderr:
        output_text += "[dim](No output returned)[/dim]\n"

    console.print(
        Panel(
            output_text.strip(),
            title=title,
            border_style="green" if success else "red",
        )
    )
    console.print()


def print_final_report(eval_data: dict) -> None:
    """Print the final verification and diagnosis outcome report."""
    status = eval_data.get("status", "SUCCESS").upper()
    summary = eval_data.get("summary", "")
    details = eval_data.get("verification_details", "")
    next_steps = eval_data.get("next_steps", "")

    if status == "SUCCESS":
        badge = "[bold white on green]  STATUS: RESOLUTION VERIFIED (SUCCESS)  [/bold white on green]"
        border_color = "green"
    elif status == "PARTIAL":
        badge = "[bold black on yellow]  STATUS: PARTIAL REMEDIATION  [/bold black on yellow]"
        border_color = "yellow"
    else:
        badge = "[bold white on red]  STATUS: REMEDIATION FAILED  [/bold white on red]"
        border_color = "red"

    content = f"{badge}\n\n"
    content += f"[bold]Outcome Summary:[/bold]\n{summary}\n"

    if details:
        content += f"\n[bold]Verification Findings:[/bold]\n[dim]{details}[/dim]\n"

    if next_steps:
        content += f"\n[bold green]Recommended Next Steps:[/bold green]\n[cyan]{next_steps}[/cyan]\n"

    warning = eval_data.get("llm_warning")
    if warning:
        content += f"\n[yellow]Note: {warning}[/yellow]\n"

    console.print(
        Panel(
            content.strip(),
            title="[bold cyan]Autonomous OS Debugging Agent - Final Report[/bold cyan]",
            border_style=border_color,
            padding=(1, 2),
        )
    )
    console.print()


def print_command_history(history_entries: List[Dict[str, Any]], log_file_path: Optional[str] = None) -> None:
    """Display comprehensive history of every command and action hit by the user."""
    table = Table(
        title="[bold cyan]⚡ Autonomous Agent: Unified Command & Action Execution History ⚡[/bold cyan]",
        border_style="cyan",
        header_style="bold magenta",
        show_lines=True,
    )
    table.add_column("#", style="dim", justify="center", width=4)
    table.add_column("Timestamp", style="cyan", width=19)
    table.add_column("Command Hit", style="bold green", width=22)
    table.add_column("Category", style="bold yellow", width=22)
    table.add_column("Action Taken / Outcome", style="white")
    table.add_column("Status", justify="center", width=14)

    if not history_entries:
        table.add_row("-", "-", "No command history found", "-", "Run any command (e.g. fix checkup, fix junk, fix 0x80070005) to start recording.", "[dim]EMPTY[/dim]")
    else:
        for idx, entry in enumerate(history_entries, 1):
            cmd = entry.get("command", "command")
            cat = entry.get("category", "General")
            action = entry.get("action_summary", "")
            ts = str(entry.get("timestamp", ""))[:19]
            st = str(entry.get("status", "SUCCESS")).upper()

            if "SUCCESS" in st or "COMPLETED" in st or "CLEANED" in st or "SOLVED" in st:
                status_str = f"[bold green]{st}[/bold green]"
            elif "CANCEL" in st or "SKIP" in st:
                status_str = f"[bold yellow]{st}[/bold yellow]"
            elif "FAIL" in st or "ERROR" in st:
                status_str = f"[bold red]{st}[/bold red]"
            elif "ROLLBACK" in st:
                status_str = f"[bold magenta]{st}[/bold magenta]"
            else:
                status_str = f"[bold cyan]{st}[/bold cyan]"

            table.add_row(str(idx), ts, f"[bold green]{cmd}[/bold green]", cat, action, status_str)

    console.print(table)
    if log_file_path:
        console.print(f"[dim]📁 All command activities permanently logged in: [cyan]{log_file_path}[/cyan][/dim]\n")
    else:
        console.print()


def print_sessions_history(sessions: list) -> None:
    """Display history of past diagnostic and remediation sessions."""
    table = Table(title="[bold]Historical Remediation Sessions & Baseline Snapshots[/bold]", border_style="cyan")
    table.add_column("Session ID", style="bold cyan", width=34)
    table.add_column("Error Code", style="bold yellow", width=14)
    table.add_column("Fix Applied", style="white", width=30)
    table.add_column("Date / Time", style="dim", width=19)
    table.add_column("Status", width=16)

    if not sessions:
        table.add_row("-", "-", "No historical sessions found.", "-", "-")
    else:
        for s in sessions:
            status = s.get("status", "APPLIED")
            is_rolled_back = s.get("rollback_executed", False)
            if is_rolled_back:
                status_str = "[bold magenta]ROLLED BACK[/bold magenta]"
            elif status == "SUCCESS":
                status_str = "[bold green]APPLIED (OK)[/bold green]"
            else:
                status_str = f"[yellow]{status}[/yellow]"

            created = s.get("created_at", "")[:19].replace("T", " ")
            table.add_row(
                s.get("session_id", ""),
                s.get("error_code", ""),
                s.get("fix_title", "Fix")[:28],
                created,
                status_str,
            )

    console.print(table)
    console.print()



def print_rollback_proposal(session_meta: dict, rollback_script: str) -> None:
    """Display the rollback plan with syntax highlighted script."""
    session_id = session_meta.get("session_id", "")
    error_code = session_meta.get("error_code", "")
    fix_title = session_meta.get("fix_title", "")

    summary_text = (
        f"Target Session: [bold cyan]{session_id}[/bold cyan]\n"
        f"Original Error: [bold yellow]{error_code}[/bold yellow]\n"
        f"Original Fix: [white]{fix_title}[/white]\n\n"
        "[bold red]This will execute the inverse rollback script to safely revert system changes.[/bold red]"
    )

    console.print(
        Panel(
            summary_text,
            title="[bold magenta]Rollback Execution Plan[/bold magenta]",
            border_style="magenta",
        )
    )

    from rich.syntax import Syntax
    syntax_view = Syntax(
        rollback_script,
        "powershell",
        theme="monokai",
        line_numbers=True,
        word_wrap=True,
    )

    console.print(
        Panel(
            syntax_view,
            title="[bold cyan]Rollback Script Preview (PowerShell)[/bold cyan]",
            border_style="cyan",
        )
    )
    console.print()


def print_reboot_notice(session_id: str, is_registered: bool) -> None:
    """Print reboot requirement and automatic resume registration status."""
    content = (
        "[bold yellow]System Restart Recommended[/bold yellow]\n\n"
        "Some components or service changes will fully activate upon system reboot.\n"
    )
    if is_registered:
        content += (
            f"\n[bold green]✓ Automatic Post-Reboot Verification is Active[/bold green]\n"
            f"When you restart and log back in, the agent will automatically launch to verify health.\n"
            f"[dim]Manual trigger: 'python agent.py resume {session_id}'[/dim]"
        )

    console.print(
        Panel(
            content.strip(),
            title="[bold yellow]Reboot & Verification Status[/bold yellow]",
            border_style="yellow",
        )
    )
    console.print()


def print_resume_header(session_id: str) -> None:
    """Print header for resumed post-reboot verification session."""
    content = (
        f"[bold green]Post-Reboot Verification Wakeup[/bold green]\n\n"
        f"Resuming diagnostic session: [bold cyan]{session_id}[/bold cyan]\n"
        "[dim]System reboot detected. Running final system health and service verification...[/dim]"
    )
    console.print(
        Panel(
            content,
            title="[bold cyan]Autonomous Agent Session Resumed[/bold cyan]",
            border_style="cyan",
        )
    )
    console.print()


def print_active_and_solved_issues(
    active_issues: List[Dict[str, Any]],
    solved_issues: List[Dict[str, Any]],
    live_services: Optional[str] = None,
) -> None:
    """Display clearly separated sections for Currently Active Problems vs Solved Problems."""
    # 1. Active Problems Section
    active_text = ""
    if active_issues:
        for idx, item in enumerate(active_issues, 1):
            code = item.get("error_code", "UNKNOWN")
            desc = item.get("description") or item.get("problem_statement", "Unresolved system issue")
            action = item.get("recommended_action", f"Run 'python agent.py diagnose {code}'")
            active_text += f"[bold red]  {idx}. [ACTIVE ERROR][/bold red] [bold yellow]{code}[/bold yellow] — [white]{desc}[/white]\n"
            active_text += f"     [dim]Action Required: {action}[/dim]\n"
    else:
        active_text = "  [bold green]✓ None (0 Active Problems Detected — System 100% Healthy)[/bold green]\n"

    # 2. Solved Problems Section
    solved_text = ""
    if solved_issues:
        for idx, item in enumerate(solved_issues, 1):
            code = item.get("error_code", "SOLVED")
            title = item.get("fix_title") or item.get("title", "Service Repair")
            sid = item.get("session_id", "")
            solved_text += f"[bold green]  {idx}. [SOLVED][/bold green] [bold yellow]{code}[/bold yellow] — [white]{title}[/white]\n"
            solved_text += f"     [dim]Status: Permanently Solved & Verified (Session: {sid})[/dim]\n"
    else:
        solved_text = "  [dim]No previous repaired sessions on record.[/dim]\n"

    # Combine into Clean Rich Panel
    content = "[bold red]🔴 CURRENTLY ACTIVE PROBLEMS:[/bold red]\n"
    content += active_text + "\n"
    content += "───────────────────────────────────────────────────────────────────────────────\n\n"
    content += "[bold green]🟢 SOLVED & RESOLVED PROBLEMS:[/bold green]\n"
    content += solved_text

    if live_services:
        content += "\n───────────────────────────────────────────────────────────────────────────────\n"
        content += f"[bold cyan]Live Core Services Health:[/bold cyan]\n[dim green]{live_services.strip()}[/dim green]\n"

    console.print(
        Panel(
            content.strip(),
            title="[bold cyan]Autonomous Agent: Active vs Solved System Health Monitor[/bold cyan]",
            border_style="cyan",
        )
    )
    console.print()


def print_blockchain_anchor_card(result: dict) -> None:
    """Print the Algorand TestNet on-chain anchor receipt with AlgoKit Lora Explorer links."""
    if not result.get("success", False):
        error_msg = result.get("error", "Unknown error")
        address = result.get("address", "")
        faucet_url = result.get("faucet_url", "")
        lora_account = result.get("lora_account_url", "")

        content = f"[bold red]✗ Blockchain Anchor Incomplete[/bold red]\n\n{error_msg}\n"
        if address:
            content += f"\n[bold white]Your TestNet Address:[/bold white]\n[cyan]{address}[/cyan]\n"
        if lora_account:
            content += f"\n[bold white]View on AlgoKit Lora Explorer:[/bold white]\n[dim underline cyan]{lora_account}[/dim underline cyan]\n"
        if faucet_url:
            content += f"\n[bold yellow]Get Free TestNet ALGO from Dispenser:[/bold yellow]\n[underline yellow]{faucet_url}[/underline yellow]\n"

        console.print(
            Panel(
                content.strip(),
                title="[bold yellow]Algorand TestNet Audit Anchor[/bold yellow]",
                border_style="yellow",
            )
        )
        console.print()
        return

    tx_id = result.get("tx_id", "")
    lora_tx_url = result.get("lora_tx_url", "")
    address = result.get("address", "")
    round_num = result.get("confirmed_round", "")
    digest = result.get("sha256", "")

    content = (
        f"[bold green]✓ Immutable On-Chain Audit Proof Confirmed![/bold green]\n\n"
        f"[bold white]Algorand TestNet Round:[/bold white] [green]{round_num}[/green]\n"
        f"[bold white]Transaction ID:[/bold white] [bold cyan]{tx_id}[/bold cyan]\n"
        f"[bold white]Signer Address:[/bold white] [dim]{address}[/dim]\n"
        f"[bold white]Session SHA-256 Digest:[/bold white] [yellow]{digest}[/yellow]\n\n"
        f"───────────────────────────────────────────────────────────────────────────────\n"
        f"[bold magenta]🔗 View Live On-Chain Proof on AlgoKit Lora Explorer:[/bold magenta]\n"
        f"[bold underline cyan]{lora_tx_url}[/bold underline cyan]\n"
        f"[dim]Timestamp, session ID, error code, and repair hash are permanently sealed on Algorand TestNet.[/dim]"
    )

    console.print(
        Panel(
            content.strip(),
            title="[bold magenta]Algorand TestNet Audit Anchor (AlgoKit Lora)[/bold magenta]",
            border_style="magenta",
        )
    )
    console.print()


def print_blockchain_status(wallet_info: dict) -> None:
    """Print Algorand TestNet wallet status and Lora Explorer links."""
    address = wallet_info.get("address", "")
    balance = wallet_info.get("balance_algo", 0.0)
    lora_url = wallet_info.get("lora_url", "")
    faucet_url = wallet_info.get("faucet_url", "")
    is_new = wallet_info.get("is_new", False)

    content = f"[bold cyan]Network:[/bold cyan] Algorand TestNet (Algod Node: testnet-api.algonode.cloud)\n\n"
    content += f"[bold white]Wallet Address:[/bold white]\n[bold cyan]{address}[/bold cyan]\n\n"
    content += f"[bold white]TestNet Balance:[/bold white] [bold green]{balance:.4f} ALGO[/bold green]\n\n"
    content += f"[bold magenta]AlgoKit Lora Account Explorer:[/bold magenta]\n[underline cyan]{lora_url}[/underline cyan]\n\n"
    content += f"[bold yellow]Free TestNet Dispenser / Faucet:[/bold yellow]\n[underline yellow]{faucet_url}[/underline yellow]\n"

    if is_new:
        content += "\n[bold green]★ Newly Generated Account:[/bold green] Seed saved to '.backups/algorand_wallet.json'.\n"

    console.print(
        Panel(
            content.strip(),
            title="[bold magenta]Algorand TestNet & AlgoKit Lora Wallet[/bold magenta]",
            border_style="magenta",
        )
    )
    console.print()


def print_resolved_issues_table(issues: List[Dict[str, Any]], archive_path: Optional[str] = None) -> None:
    """Print clean formatted table of all solved and resolved issues loaded from archive file."""
    table = Table(
        title="[bold green]Archived Solved & Resolved Problems[/bold green]",
        border_style="green",
        header_style="bold green",
    )
    table.add_column("#", style="dim", width=4)
    table.add_column("Error Code", style="bold yellow", width=14)
    table.add_column("Remediation / Fix Applied", style="white")
    table.add_column("Status", style="bold green", width=12)
    table.add_column("Resolved At", style="cyan", width=20)
    table.add_column("Session ID", style="dim cyan", width=34)

    if not issues:
        table.add_row("-", "-", "No resolved issues currently recorded in archive file.", "-", "-", "-")
    else:
        for idx, item in enumerate(issues, 1):
            code = item.get("error_code", "UNKNOWN")
            title = item.get("fix_title") or item.get("title", "System Repair")
            st = item.get("status", "SOLVED")
            resolved_at = str(item.get("resolved_at", item.get("created_at", "")))[:19]
            sid = item.get("session_id", "")
            table.add_row(str(idx), code, title, f"[bold green]{st}[/bold green]", resolved_at, sid)

    console.print(table)
    if archive_path:
        console.print(f"[dim]📁 Saved to dedicated archive file: [cyan]{archive_path}[/cyan][/dim]\n")
    else:
        console.print()


def print_junk_and_duplicates_summary(junk_data: Dict[str, Any], dup_data: Dict[str, Any]) -> None:
    """Print comprehensive summary table of junk files and duplicate copies."""
    # 1. Junk Files Table
    junk_table = Table(
        title="[bold yellow]🧹 System Junk & Temporary Cache Audit[/bold yellow]",
        border_style="yellow",
        header_style="bold yellow",
    )
    junk_table.add_column("Category", style="bold white", width=30)
    junk_table.add_column("Location", style="dim cyan")
    junk_table.add_column("Files", style="cyan", justify="right", width=8)
    junk_table.add_column("Size", style="bold green", justify="right", width=12)

    categories = junk_data.get("categories", [])
    if not categories:
        junk_table.add_row("Clean", "No significant junk files detected", "0", "0 B")
    else:
        for cat in categories:
            junk_table.add_row(
                cat["category"],
                cat["folder"],
                str(cat["file_count"]),
                cat["total_formatted"],
            )

    console.print(junk_table)
    console.print(f"[bold white]Total Junk Found:[/bold white] [bold yellow]{junk_data.get('total_files', 0)} files[/bold yellow] ([bold green]{junk_data.get('total_formatted', '0 B')}[/bold green] reclaimable)\n")

    # 2. Duplicate Files Table
    dup_table = Table(
        title="[bold cyan]📑 Duplicate Files Audit (System Drives & User Folders)[/bold cyan]",
        border_style="cyan",
        header_style="bold cyan",
    )
    dup_table.add_column("#", style="dim", width=4)
    dup_table.add_column("Duplicate Copies Detected", style="white")
    dup_table.add_column("File Size", style="yellow", justify="right", width=12)
    dup_table.add_column("Wasted Space", style="bold red", justify="right", width=14)

    groups = dup_data.get("groups", [])
    if not groups:
        dup_table.add_row("-", "No duplicate files detected across scanned drives and folders.", "-", "0 B")
    else:
        for idx, grp in enumerate(groups[:15], 1):  # Show top 15 groups
            orig_path = grp["original"]["path"]
            copies_text = f"[bold green]Original:[/bold green] {orig_path}\n"
            for c in grp["copies"]:
                copies_text += f"[bold red]Copy:[/bold red] {c['path']}\n"
            dup_table.add_row(str(idx), copies_text.strip(), grp["file_size_formatted"], grp["wasted_formatted"])

    console.print(dup_table)
    console.print(f"[bold white]Total Redundant Copies:[/bold white] [bold red]{dup_data.get('total_duplicate_copies', 0)} copies[/bold red] across {dup_data.get('total_groups', 0)} file groups ([bold green]{dup_data.get('total_wasted_formatted', '0 B')}[/bold green] reclaimable)\n")


def print_web_threats_summary(threat_data: Dict[str, Any]) -> None:
    """Print comprehensive summary of malicious web notification permissions and adware hooks."""
    all_threats = threat_data.get("all_threats", [])
    trusted = threat_data.get("trusted_notifications", [])

    table = Table(
        title="[bold red]🛡️ Malicious Web Notification & Adware Popup Audit[/bold red]",
        border_style="red",
        header_style="bold red",
    )
    table.add_column("#", style="dim", width=4)
    table.add_column("Threat Origin / Hook", style="bold yellow", width=34)
    table.add_column("Browser / Target", style="cyan", width=18)
    table.add_column("Severity", style="bold red", width=16)
    table.add_column("Description", style="white")

    if not all_threats:
        table.add_row("✓", "No malicious push notifications or adware hooks detected", "All Browsers", "[bold green]CLEAN[/bold green]", "Browser profiles are safe and free from rogue popup spammers.")
    else:
        for idx, t in enumerate(all_threats, 1):
            origin = t.get("origin") or t.get("name", "Unknown Hook")
            target = t.get("browser") or t.get("type", "System")
            sev = t.get("severity", "HIGH")
            desc = t.get("description") or t.get("command", "Suspicious execution")
            table.add_row(str(idx), origin, target, f"[bold red]{sev}[/bold red]", desc)

    console.print(table)
    if trusted:
        console.print(f"[dim]Verified [bold green]{len(trusted)} trusted notification origin(s)[/bold green] (Google, Microsoft, YouTube, Teams) kept safe.[/dim]\n")
    else:
        console.print()


def print_full_checkup_header() -> None:
    """Print banner for Full PC Security & System Checkup."""
    content = (
        "[bold white]⚡ FULL PC SECURITY, HEALTH & STORAGE DOCTOR ⚡[/bold white]\n\n"
        "[cyan]1. System File & Binary Integrity Check[/cyan] (SFC / DISM / Kernel verification)\n"
        "[cyan]2. Event Viewer Crash Log Audit[/cyan] (System, Application, WindowsUpdate, Security)\n"
        "[cyan]3. Core Security & System Services Health[/cyan] (wuauserv, bits, cryptsvc, WinDefend)\n"
        "[cyan]4. Malicious Web Push & Adware Popup Audit[/cyan] (Chrome, Edge, Brave, Firefox notification spammers)\n"
        "[cyan]5. Storage & Duplicate File Manager[/cyan] (Scans junk caches & duplicate copies with user permission)\n"
        "[cyan]6. Autonomous AI Auto-Heal Engine[/cyan] (Detects root cause & generates verified fix)"
    )
    console.print(
        Panel(
            content,
            title="[bold green]🛡️ Complete Laptop Security & Health Scan[/bold green]",
            border_style="green",
        )
    )
    console.print()


def print_interactive_menu() -> None:
    """Print clear numbered interactive command selector menu."""
    menu_table = Table(
        title="[bold cyan]⚡ Autonomous OS Debugging Agent — Interactive Command Selector ⚡[/bold cyan]",
        border_style="cyan",
        header_style="bold magenta",
        show_lines=True,
    )
    menu_table.add_column("No.", style="bold yellow", justify="center", width=6)
    menu_table.add_column("Command Action", style="bold white", width=24)
    menu_table.add_column("Category", style="cyan", width=18)
    menu_table.add_column("Description", style="dim white")

    options = [
        ("1", "full-checkup", "🛡️ Security & Health", "Full PC scan — auto-heals errors, cleans adware & scans storage"),
        ("2", "diagnose", "🔵 Targeted Diagnostic", "Diagnose a specific OS error code (e.g. 0x80070005, 0x80240020)"),
        ("3", "clean-junk", "🧹 Storage Cleaner", "Scan and delete OS temp caches, crash dumps, and prefetch clutter"),
        ("4", "scan-duplicates", "📑 Duplicate Finder", "Find duplicate files in user folders with permission-gated deletion"),
        ("5", "scan-web-threats", "🛡️ Web & Adware", "Scan and remove rogue browser push notifications & adware popups"),
        ("6", "rollback", "🛡️ Recovery Engine", "1-Click instant system rollback to pre-fix baseline snapshot"),
        ("7", "solved-issues", "🟢 Archive & Audit", "Display all solved & resolved problems saved in separate archive file"),
        ("8", "startup-monitor", "📊 Live Health Monitor", "Real-time active vs resolved issues and live OS services check"),
        ("9", "resume", "🔄 Post-Reboot Wakeup", "Resume and verify diagnostic session after computer restart"),
        ("10", "history", "📜 Session History", "View complete historical table of all diagnostic/fix sessions"),
        ("11", "blockchain status", "🟣 Web3 / Algorand", "View Algorand TestNet wallet, balance, and AlgoKit Lora link"),
        ("12", "blockchain anchor", "🟣 Web3 / Algorand", "Commit cryptographic SHA-256 proof of repair to blockchain"),
        ("13", "check-env", "⚙️ System Config", "Verify environment, LLM configuration, and Administrator/root rights"),
        ("14", "enable-autostart", "🚀 Startup Setup", "Register agent to automatically monitor system health on boot"),
        ("15", "disable-autostart", "🚀 Startup Setup", "Remove automatic boot monitor from startup tasks"),
        ("16", "startup-log", "📜 Boot History Log", "View timestamped log of all automatic startup health runs"),
        ("17", "install-shortcut", "⚡ 1-Word 'fix' Cmd", "Install permanent 1-word 'fix' shortcut in Command Prompt (cmd)"),
        ("0", "exit", "❌ Exit", "Exit interactive command menu"),
    ]

    for num, cmd, cat, desc in options:
        menu_table.add_row(f"[bold yellow][{num}][/bold yellow]", f"[bold green]{cmd}[/bold green]", cat, desc)

    console.print(menu_table)
    console.print()


