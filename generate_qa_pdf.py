"""Generate a clean Q&A PDF with all 200 questions and easy-language answers."""

from reportlab.lib.pagesizes import A4
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.units import cm
from reportlab.lib import colors
from reportlab.platypus import (
    SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle,
    PageBreak, HRFlowable, KeepTogether
)
from reportlab.lib.enums import TA_CENTER, TA_LEFT

# ── Colors ──────────────────────────────────────────────────
BLUE   = colors.HexColor("#1A73E8")
GREEN  = colors.HexColor("#1E8C45")
RED    = colors.HexColor("#C0392B")
PURPLE = colors.HexColor("#7D3C98")
TEAL   = colors.HexColor("#117A65")
ORANGE = colors.HexColor("#D35400")
DARK   = colors.HexColor("#1A1A2E")
WHITE  = colors.white
LGRAY  = colors.HexColor("#F4F6F8")
BORDER = colors.HexColor("#D0D3D4")
ANS_BG = colors.HexColor("#EAF4FB")
CAT_COLORS = [BLUE, PURPLE, TEAL, GREEN, ORANGE, RED,
              colors.HexColor("#1ABC9C"), colors.HexColor("#E67E22"),
              colors.HexColor("#2980B9"), colors.HexColor("#8E44AD")]

# ── Styles ───────────────────────────────────────────────────
styles = getSampleStyleSheet()

title_s = ParagraphStyle("T", fontSize=26, textColor=BLUE,
    alignment=TA_CENTER, fontName="Helvetica-Bold", spaceAfter=4)
sub_s = ParagraphStyle("S", fontSize=12, textColor=colors.HexColor("#555"),
    alignment=TA_CENTER, spaceAfter=16)
cat_s = ParagraphStyle("C", fontSize=13, textColor=WHITE,
    fontName="Helvetica-Bold", spaceAfter=6, spaceBefore=14,
    leftIndent=0, borderPad=7)
q_s = ParagraphStyle("Q", fontSize=10.5, textColor=DARK,
    fontName="Helvetica-Bold", spaceAfter=3, spaceBefore=6, leading=15)
a_s = ParagraphStyle("A", fontSize=10, textColor=colors.HexColor("#1A5276"),
    spaceAfter=2, leading=14, leftIndent=14)
body_s = ParagraphStyle("B", fontSize=10, textColor=DARK,
    spaceAfter=4, leading=14)
num_s = ParagraphStyle("N", fontSize=10, textColor=WHITE,
    fontName="Helvetica-Bold", alignment=TA_CENTER)

# ── All 200 Q&A ──────────────────────────────────────────────
QA_DATA = [
    {
        "title": "CATEGORY 1: Basic Project Understanding",
        "emoji": "🔵",
        "color": BLUE,
        "questions": [
            ("What is the Autonomous OS Debugging Agent?",
             "It is an AI-powered tool that runs in your terminal. When your Windows PC gets an error, this agent automatically figures out what went wrong, suggests a fix, and applies it safely — just like having a computer expert sitting inside your laptop."),
            ("What problem does this project solve?",
             "When a PC gets OS errors like '0x80070005', most people spend 30–45 minutes Googling random fixes and running risky commands. This tool solves the problem in under 15 seconds by doing all that work automatically."),
            ("Why can't users just use ChatGPT to fix OS errors?",
             "ChatGPT guesses commands without actually checking what is wrong on YOUR machine. It can suggest a fix that breaks your PC further. Our agent first reads real live data from your system, then suggests a fix — so there are no guesses."),
            ("What does the term 'autonomous' mean in this context?",
             "Autonomous means the agent works on its own. It collects data, runs safe checks, generates a fix, and verifies it worked — all without you having to tell it each step. You only need to approve the fix before it runs."),
            ("What is an OS error code like 0x80070005?",
             "It is a code that Windows shows when something goes wrong. The numbers and letters represent a specific type of error. '0x80070005' specifically means 'Access Denied' — some permission or security setting is blocking an operation."),
            ("What does '0x80070005: Access Denied' mean on Windows?",
             "It means Windows tried to do something (like update itself or start a service) but was blocked because the required permissions were missing or broken. Usually caused by damaged NTFS ACL (Access Control List) settings."),
            ("Who is the target user for this tool?",
             "Anyone who uses Windows — from home users whose PC crashes, to IT teams in companies managing hundreds of computers. No technical knowledge is required to use it."),
            ("Is this project open-source? Where is the code?",
             "Yes, it is 100% open-source. The full code is available on GitHub at: github.com/Ansh00031/Build-In-Bharat_NIT-Delhi"),
            ("What operating systems does it support?",
             "Currently it fully supports Windows 10 and Windows 11. Linux and macOS support is planned for future versions."),
            ("What programming language is the project built in?",
             "The entire project is built in Python 3.10+. The CLI uses the 'Typer' library and the terminal display uses 'Rich' for colored tables and panels."),
            ("What is the 'AI mechanic inside your terminal' analogy?",
             "Think of it like calling a car mechanic. Instead of you guessing what is wrong with your car, the mechanic plugs in a diagnostic tool, reads the error codes, and fixes the specific problem. Our agent does the same for your PC."),
            ("How is this different from a standard antivirus tool?",
             "Antivirus tools scan for viruses and malware. Our tool fixes OS-level errors like broken permissions, failed Windows Updates, stopped services, and registry issues. These are system health problems, not security threats."),
            ("How long does a traditional IT support ticket take vs. your tool?",
             "A traditional IT ticket takes 30–45 minutes to hours. Our agent diagnoses and fixes the same error in under 15 seconds with full AI reasoning and safe execution."),
            ("What is the main CLI command to start diagnosis?",
             "You open a terminal and type: python agent.py diagnose 0x80070005 (replace 0x80070005 with your actual error code). That is all you need to type."),
            ("Does the user need to know PowerShell to use this tool?",
             "No. The agent generates and runs all PowerShell commands internally. You just approve or reject the fix by pressing Y or N. No scripting knowledge needed."),
            ("What is the minimum Python version required?",
             "Python 3.10 or higher is required. The project uses modern Python features like union types and improved pattern matching."),
            ("Does the tool require internet to work?",
             "For the AI reasoning (GPT-4o or similar), yes — internet is needed. However, it can also run in offline mode using a local AI model like Ollama (Llama 3.1) without any internet."),
            ("Can it work fully offline?",
             "Yes. By configuring a local AI model via Ollama, the agent can diagnose and fix errors completely offline. The only internet-requiring feature is the Algorand blockchain anchor."),
            ("What is the GitHub repository link for this project?",
             "github.com/Ansh00031/Build-In-Bharat_NIT-Delhi — contains full source code, documentation, PDF, presentation, and the 1-line WinRE rescue command."),
            ("What was the inspiration behind building this?",
             "The team experienced Windows Update failures and OS errors that wasted hours of time. The idea was to build an autonomous AI agent that solves these problems the same way an expert IT engineer would — but in seconds."),
        ]
    },
    {
        "title": "CATEGORY 2: AI Engine & Reasoning Loop",
        "emoji": "🧠",
        "color": PURPLE,
        "questions": [
            ("What AI model powers the diagnostic reasoning?",
             "By default it uses OpenAI GPT-4o. But it can be configured to use any OpenAI-compatible model including Ollama (Llama 3.1, Mistral, DeepSeek) for fully local/offline operation."),
            ("What is 'hallucination' in AI and why is it dangerous for OS repair?",
             "Hallucination is when AI confidently gives wrong answers. In OS repair, this is very dangerous — if the AI suggests a wrong PowerShell command, it could delete system files or break Windows completely."),
            ("How does the agent avoid hallucinations?",
             "Before suggesting any fix, the agent first reads REAL live data from your system (Event logs, service status, permissions). The fix is grounded in actual evidence — not guesswork. This is called Active Telemetry Grounding."),
            ("What is the Active Telemetry Reasoning Loop?",
             "It is the 5-step process where the agent: (1) reads system data, (2) forms a hypothesis, (3) runs safe diagnostic probes, (4) confirms the root cause from real evidence, then (5) generates a targeted fix."),
            ("What are the 5 stages of the AI reasoning pipeline?",
             "Stage 1: Hypothesis Formulation. Stage 2: Diagnostic Command Generation. Stage 3: Root Cause Confirmation. Stage 4: Remediation Script Synthesis. Stage 5: Verification Evaluation."),
            ("What is 'hypothesis formulation' in Stage 1?",
             "The AI looks at your error code and system data and makes an educated guess about the possible causes. For example, '0x80070005 could be caused by broken NTFS permissions on the Windows Update folder'."),
            ("What are read-only diagnostic probes?",
             "These are safe commands that only READ information from your system — they never change anything. For example, 'icacls C:\\Windows\\System32' only checks permissions but never modifies them."),
            ("What is icacls and what does it check?",
             "icacls is a Windows built-in command that shows file and folder permissions (who can read, write, or execute a file). The agent uses it to check if important Windows folders have correct permissions."),
            ("What is Get-Service used for in diagnostics?",
             "Get-Service is a PowerShell command that lists the status of Windows services (like Windows Update, BITS, Cryptographic Services). The agent uses it to see if critical services are running or stopped."),
            ("What is Get-WinEvent and which logs does it read?",
             "Get-WinEvent reads Windows Event Viewer logs. The agent reads from System, Application, and WindowsUpdateClient channels to see exactly what errors occurred and when."),
            ("How does the AI confirm the root cause in Stage 3?",
             "After the safe diagnostic commands run, their output is fed back to the AI. The AI reads this evidence and narrows down the exact cause. For example: 'The WindowsUpdate service is stopped AND the BITS service has Access Denied errors — root cause confirmed.'"),
            ("What information is fed back to the AI after probes run?",
             "The command output (text results), exit codes (success/failure numbers), any error messages, and the purpose of each command are all sent back to the AI for analysis."),
            ("What is a 'remediation script' in Stage 4?",
             "It is a PowerShell script that fixes the confirmed root cause. For example, if permissions are broken, the script runs 'icacls' to reset them. The script is targeted — it only fixes what is actually broken."),
            ("What language are remediation scripts written in?",
             "PowerShell (.ps1 scripts) for Windows. PowerShell is Windows' built-in scripting language and has full access to system settings, services, and registry without needing extra software."),
            ("How does the AI structure its JSON output for fix proposals?",
             "The AI returns a structured JSON object containing: title (fix name), script_content (the actual PowerShell code), verification_command (to check if fix worked), requires_reboot (true/false), and risk_level."),
            ("What is the verification command in Stage 5?",
             "After the fix runs, the agent automatically runs a verification command (like 'Get-Service wuauserv | Select Status') to confirm the problem is actually solved. The AI then evaluates if the result shows success."),
            ("Can the AI work without an OpenAI API key?",
             "Yes. You can configure it to use a local AI model via Ollama. Set OPENAI_BASE_URL=http://localhost:11434/v1 in the .env file and it will use your local Llama or Mistral model completely offline."),
            ("What happens in offline/heuristic mode without an API key?",
             "The agent falls back to built-in expert heuristic rules that cover the most common Windows error patterns. It is less intelligent than AI mode but still functional for standard errors."),
            ("Can you use a local LLM like Ollama or Llama 3.1?",
             "Yes. Install Ollama, pull a model (ollama pull llama3.1), then set OPENAI_BASE_URL=http://localhost:11434/v1 in the .env file. The agent will use your local model for 100% private offline operation."),
            ("How do you configure Ollama as the AI backend?",
             "In the .env file: OPENAI_BASE_URL=http://localhost:11434/v1 and LLM_MODEL=llama3.1. No API key needed for local Ollama models."),
            ("What is the OPENAI_BASE_URL setting used for?",
             "It tells the agent where to send AI requests. By default it goes to OpenAI's servers. Change it to point to your local Ollama, Azure OpenAI, or any other OpenAI-compatible endpoint."),
            ("What is the LLM_MODEL environment variable?",
             "It specifies which AI model to use. Default is 'gpt-4o'. For local models you'd set it to 'llama3.1' or 'mistral' depending on what you have installed."),
            ("How does the agent handle LLM rate limits or timeouts?",
             "If the AI service is slow or rate-limited, the agent will display an error and fall back to the heuristic offline mode so the diagnosis can still proceed."),
            ("What is a JSON Schema prompt and why use strict JSON?",
             "The agent tells the AI to return answers in a strict JSON format (like a form). This prevents the AI from returning random text and ensures the fix proposal is always machine-readable and safe to process."),
            ("What happens if the AI returns malformed JSON?",
             "The agent has a fallback JSON extractor that searches for JSON-like structures in the AI response. If it still cannot parse it, the agent displays a warning and asks the user to retry."),
            ("How does the agent ensure the AI stays on topic?",
             "The system prompt explicitly tells the AI its role (OS diagnostic expert), what tools it has (safe probes only), what is forbidden (destructive commands), and what format to respond in. This constrains the AI to safe, relevant responses."),
            ("Can the AI diagnose Linux errors too?",
             "Not yet. Currently it is Windows-only. Linux support (systemd, journalctl, apt errors) is planned for the next version."),
            ("What Windows Event Viewer channels does the agent read?",
             "System (hardware and OS errors), Application (software errors), and Microsoft-Windows-WindowsUpdateClient/Operational (Windows Update specific errors)."),
            ("How many event log entries does it collect by default?",
             "50 entries by default. You can change this with the --max-events flag (e.g., python agent.py diagnose 0x80070005 --max-events 100)."),
            ("What is the --max-events flag used for?",
             "It controls how many recent error log entries the agent reads from Windows Event Viewer. More entries = more context for AI = better diagnosis, but also slightly slower."),
        ]
    },
    {
        "title": "CATEGORY 3: Security & Safety",
        "emoji": "🛡️",
        "color": RED,
        "questions": [
            ("What is the Security Guardrail / Command Blacklist?",
             "It is a built-in filter that automatically blocks any dangerous command before it can run. The agent checks every single command against a list of forbidden patterns. If a command matches, it is blocked immediately."),
            ("Which commands are blocked by the blacklist?",
             "Commands like: del, rmdir, format, Remove-Item, reg delete, net user /delete, rd /s, cipher /w, and any command that could delete files, wipe drives, remove accounts, or damage the system."),
            ("How is the blacklist implemented technically?",
             "Using Python regular expressions (regex). Each command is tested against patterns like r'\\bdel\\b' or r'\\bformat\\b'. If any pattern matches, the command is rejected and logged."),
            ("Can the blacklist be bypassed?",
             "During the safe diagnostic probe phase, no — the blacklist always runs. During the remediation phase, the AI is instructed to never include blacklisted commands, and even if it did, the user sees the script before execution and can reject it."),
            ("What is the Human-in-the-Loop (HITL) gate?",
             "Before any fix runs, the agent shows you the complete PowerShell script with syntax highlighting and asks 'Do you want to execute this fix? [Y/n]'. Nothing happens unless you type Y and press Enter."),
            ("What exactly is shown to the user before executing a fix?",
             "The full PowerShell script is displayed with colored syntax highlighting (Monokai theme), along with the fix title, risk level, what it will change, and what verification command will run afterward."),
            ("What happens if the user selects 'N' at the approval gate?",
             "The agent exits cleanly. No changes are made to the system. The generated script is shown on screen so the user can copy it manually if they want to review or run it themselves."),
            ("What is a 'read-only diagnostic probe' vs. a 'write command'?",
             "A read-only probe only reads information (like checking file permissions or service status). A write command changes something (like modifying a registry key). All diagnostic probes are strictly read-only. Only user-approved fix scripts can write."),
            ("How are diagnostic commands sandboxed?",
             "Each command runs as a separate child process with a timeout limit. The output is captured and returned to the agent. The command cannot access the agent's memory or files."),
            ("What is the temp file sandbox execution model?",
             "The fix script is saved to a temporary file (in %TEMP%), executed, and then immediately deleted after execution completes — win or lose. This prevents scripts from lingering on the system."),
            ("Are fix scripts auto-deleted after execution?",
             "Yes. Using Python's NamedTemporaryFile with delete=True, the script file is guaranteed to be deleted even if the execution crashes or the user presses Ctrl+C."),
            ("What is a pre-fix snapshot?",
             "Before any fix runs, the agent saves a copy of the current system state — including the fix script, a rollback script, session metadata, and the verification command — into a .backups folder."),
            ("Where are snapshots stored on disk?",
             "In the .backups/ folder inside your project directory. Each session gets its own subfolder named by session ID, e.g.: .backups/session_20260818_224722_80070005/"),
            ("What does a snapshot contain?",
             "Four files: metadata.json (session info), fix.ps1 (the applied fix script), rollback.ps1 (the reversal script), and later blockchain_receipt.json (if anchored to Algorand)."),
            ("What is a rollback script?",
             "It is a PowerShell script that does the OPPOSITE of the fix. If the fix added a registry key, the rollback deletes it. If the fix reset permissions, the rollback restores the original values."),
            ("How is the rollback script generated?",
             "The AI generates it at the same time as the fix script. It is specifically designed to undo every change the fix makes, in reverse order."),
            ("How long does a rollback take to execute?",
             "Usually under 1 second for simple fixes. More complex fixes (like DISM repairs) might take a few seconds. The rollback is designed to be fast."),
            ("What is 'python agent.py rollback' and when do you use it?",
             "Run this command if a fix made your PC worse or you changed your mind. It automatically finds the most recent session and runs its rollback script to undo all changes."),
            ("Can you rollback multiple sessions?",
             "Yes. Use: python agent.py rollback session_ID to specify which session to roll back. Run python agent.py history to see all session IDs."),
            ("What happens if the rollback script itself fails?",
             "The agent shows the error, displays the rollback script on screen, and suggests manual steps. The original fix script is also available in .backups/ so you can analyze what was changed."),
            ("What is Administrator privilege and why is it required?",
             "Administrator (admin) privilege means the program has permission to change system settings. Without it, the agent cannot read certain protected Event Viewer logs or apply fixes to system folders."),
            ("What is --skip-admin-check flag and when should it be used?",
             "This flag lets you run the agent WITHOUT admin rights — useful for testing or demos. In this mode, some system log access may be limited. Use: python agent.py diagnose 0x80070005 --skip-admin-check"),
            ("What is dry-run mode?",
             "Running with --skip-admin-check activates a limited dry-run mode where the agent reads what it can and generates fix proposals but may not be able to execute them on protected system areas."),
            ("Can a standard (non-admin) user run the agent?",
             "Yes, with --skip-admin-check. But for full functionality — reading all Event Viewer logs and applying fixes — running as Administrator is recommended."),
            ("What are the most common dangerous commands blocked?",
             "del, rmdir, format, Remove-Item -Recurse, reg delete, net user /delete, cipher /w (secure wipe), rd /s /q, and any command containing 'wipe', 'erase', or 'destroy'."),
            ("Does the agent access the internet during diagnosis?",
             "Only to call the AI API (OpenAI/Ollama). All system diagnostic commands run locally. No system data is sent to the internet except what is sent to the AI for analysis."),
            ("Can the agent modify the Windows Registry?",
             "Yes, but only through user-approved fix scripts. Diagnostic probes use Get-ItemProperty (read-only). Fix scripts may use Set-ItemProperty or reg add — but only after you approve them."),
            ("What is the difference between diagnosis phase and remediation phase?",
             "Diagnosis = only reading/observing (100% safe, no changes). Remediation = applying the fix (requires admin, requires Y/N approval). These two phases are strictly separated."),
            ("How does the agent handle timeouts on diagnostic commands?",
             "Each command has a 30-second timeout. If it doesn't finish in time, the agent marks it as timed out, skips it, and continues with other diagnostic commands."),
            ("What is the execute_diagnostic_command function?",
             "It is the core function in core/executor.py that safely runs any diagnostic command: validates it against the blacklist, executes it with a timeout, captures output, and returns structured results."),
        ]
    },
    {
        "title": "CATEGORY 4: Sessions, Snapshots & Rollback",
        "emoji": "💾",
        "color": TEAL,
        "questions": [
            ("What is a session ID and how is it generated?",
             "A session ID is a unique name for each diagnosis run. It is generated from the current date, time, and error code. Example: session_20260818_224722_80070005"),
            ("Where are all sessions stored?",
             "In the .backups/ folder inside your project directory. Each session has its own subfolder."),
            ("What is the .backups/ directory structure?",
             ".backups/ contains one folder per session. Inside each session folder: metadata.json, fix.ps1, rollback.ps1, and optionally blockchain_receipt.json."),
            ("What files are inside a session's backup folder?",
             "metadata.json (who, what, when), fix.ps1 (the PowerShell fix that was applied), rollback.ps1 (the undo script), blockchain_receipt.json (Algorand TX proof if anchored)."),
            ("What is metadata.json in a session?",
             "It stores all information about the session: error code, session ID, timestamp, fix title, status (completed/failed), verification command, and whether a rollback was executed."),
            ("What is fix.ps1 in a session?",
             "It is the exact PowerShell script that was applied to fix the error. It is saved permanently so you can review exactly what changed on your system."),
            ("What is rollback.ps1 in a session?",
             "It is the undo script. Running it reverses everything that fix.ps1 did. It is saved immediately when the fix is created, before any changes happen."),
            ("What is the 'history' command used for?",
             "python agent.py history shows a table of all past diagnosis sessions — their ID, error code, fix title, status, and timestamp."),
            ("How do you view all past sessions?",
             "Run: python agent.py history. You will see a formatted table with all sessions sorted by newest first."),
            ("What session statuses exist?",
             "COMPLETED (fix applied successfully), FAILED (fix did not work), ROLLED_BACK (fix was reversed), VERIFIED_POST_REBOOT (verified after restart), PARTIAL (partially fixed), AWAITING_REBOOT (waiting for restart)."),
            ("What is VERIFIED_POST_REBOOT status?",
             "After a fix requires a restart, the agent automatically runs a verification check on the next boot. If it passes, the session status is updated to VERIFIED_POST_REBOOT."),
            ("What is blockchain_receipt.json inside a session?",
             "If you used the --anchor flag or python agent.py blockchain anchor, this file stores the Algorand transaction ID, Lora Explorer URL, SHA-256 hash, and confirmation round."),
            ("Can you delete a session's backup manually?",
             "Technically yes, but it is not recommended. Deleting it means you lose the rollback script and cannot undo that fix if something goes wrong later."),
            ("What happens to the session if rollback is executed?",
             "The session status is updated to ROLLED_BACK and a rollback_executed: true flag is set in metadata.json. The session record is kept for audit purposes."),
            ("How many sessions are stored by default?",
             "All sessions are stored indefinitely. There is no automatic cleanup or limit. You can manually delete old session folders from .backups/ if you want to free up space."),
            ("Is there a cleanup or expiry for old sessions?",
             "Not currently. A cleanup command (python agent.py cleanup --older-than 30d) is planned for a future version."),
            ("What is the update_session_status function?",
             "It is the function in core/snapshot.py that updates the status field in a session's metadata.json file. Called after fix execution and after rollback."),
            ("What is the get_session function?",
             "It reads a session's metadata.json by session ID and returns the session data as a Python dictionary for the agent to work with."),
            ("What is the list_sessions function?",
             "It scans the .backups/ directory, reads all session metadata files, and returns them as a sorted list (newest first) for display in the history command."),
            ("How does the rollback command find the most recent session?",
             "It calls list_sessions() which returns sessions sorted by timestamp. The first item in the list is the most recent session. If no session ID is specified, it uses this one."),
        ]
    },
    {
        "title": "CATEGORY 5: Auto-Start & Reboot Management",
        "emoji": "🔄",
        "color": ORANGE,
        "questions": [
            ("What is the enable-autostart command?",
             "python agent.py enable-autostart adds a batch file to the Windows Startup folder so the agent automatically runs startup-monitor every time the PC starts or restarts."),
            ("Where is the startup batch file created on Windows?",
             "At: %APPDATA%\\Microsoft\\Windows\\Start Menu\\Programs\\Startup\\OS_Debug_Agent_Startup.bat — Windows automatically runs all files in this folder on boot."),
            ("What does the startup batch file do on boot?",
             "It runs 'python agent.py startup-monitor' which checks for active system problems and shows a health report in a Command Prompt window that stays open for the user to see."),
            ("What is the disable-autostart command?",
             "python agent.py disable-autostart removes the startup batch file, so the agent no longer runs automatically on boot."),
            ("What is the startup-monitor command?",
             "python agent.py startup-monitor shows a dashboard with two sections: Active Problems (current errors not yet fixed) and Solved Problems (successfully fixed errors). Also shows live service health."),
            ("What is the difference between Active Problems and Solved Problems?",
             "Active Problems = sessions with FAILED or PARTIAL status (still need attention). Solved Problems = sessions with COMPLETED or VERIFIED status (successfully fixed). This gives you a quick health overview on every boot."),
            ("What services does startup-monitor check live?",
             "wuauserv (Windows Update), bits (Background Intelligent Transfer Service), and cryptsvc (Cryptographic Services). These are the three most critical services for Windows health."),
            ("What is the startup-log command?",
             "python agent.py startup-log reads and displays the .backups/startup_log.txt file, which records every time the startup health check ran — with timestamps and results."),
            ("Where is the startup execution log stored?",
             "At: .backups/startup_log.txt inside the project directory. Each startup run appends a new timestamped entry."),
            ("What is the Windows RunOnce registry key?",
             "It is a special registry location (HKLM\\Software\\Microsoft\\Windows\\CurrentVersion\\RunOnce) where you can register a command that runs ONE TIME on the next Windows startup, then automatically deletes itself."),
            ("What is register_reboot_hook used for?",
             "When a fix requires a restart, this function registers a RunOnce registry entry so that after the reboot, the agent automatically runs the verification check for that session."),
            ("What registry path is used for the RunOnce hook?",
             "HKLM\\SOFTWARE\\Microsoft\\Windows\\CurrentVersion\\RunOnce\\OSDebugAgentResume"),
            ("What command is registered in RunOnce after a fix?",
             "python agent.py resume <session_id> — this resumes the session after reboot and runs the verification command to check if the fix worked."),
            ("What is python agent.py resume <session_id>?",
             "This command is used after a reboot. It re-checks the system state for that session, runs the verification command, and updates the session status to VERIFIED_POST_REBOOT or FAILED."),
            ("When does the resume command fire automatically?",
             "After register_reboot_hook is called, the next time Windows starts, the RunOnce entry fires automatically and runs the resume command — no user action needed."),
            ("What is unregister_reboot_hook used for?",
             "It removes the OSDebugAgentResume RunOnce registry entry. Called at the start of the resume command so the hook only fires once and does not repeat on every subsequent boot."),
            ("Why is it important to unregister the hook after it fires?",
             "If you forget to unregister, the resume command would run on EVERY boot, showing old session results every time Windows starts — which would be annoying and confusing."),
            ("What is is_reboot_pending() checking?",
             "It checks specific Windows registry keys that Windows sets when a restart is required. If these keys exist, it means Windows is waiting for a reboot to complete updates or service changes."),
            ("Which Windows registry keys indicate a pending reboot?",
             "HKLM\\SYSTEM\\CurrentControlSet\\Control\\Session Manager\\PendingFileRenameOperations and HKLM\\SOFTWARE\\Microsoft\\Windows\\CurrentVersion\\WindowsUpdate\\Auto Update\\RebootRequired"),
            ("What happens if a reboot is needed but the user declines?",
             "The agent saves the session and explains that the fix may not be fully active until after a restart. The RunOnce hook is NOT registered (since the user declined), so manual resume will be needed after rebooting."),
        ]
    },
    {
        "title": "CATEGORY 6: WinRE Cloud Recovery",
        "emoji": "🌐",
        "color": colors.HexColor("#1ABC9C"),
        "questions": [
            ("What is Windows Recovery Environment (WinRE)?",
             "WinRE is a special minimal version of Windows that loads when your PC cannot start normally. It has basic tools to repair Windows. You can open a Command Prompt inside WinRE to run commands."),
            ("How do you enter WinRE on a Windows machine?",
             "Method 1: Force restart 3 times (hold power button to turn off 3 times). Method 2: Hold Shift while clicking Restart in the Start Menu. Method 3: Boot from a Windows USB drive."),
            ("What is the 1-line cloud rescue command?",
             "irm https://raw.githubusercontent.com/Ansh00031/Build-In-Bharat_NIT-Delhi/main/bootstrap.ps1 | iex — Run this in WinRE PowerShell. It downloads and launches the full agent automatically."),
            ("What is bootstrap.ps1 and what does it do?",
             "It is a PowerShell script hosted on GitHub. When run, it: detects your offline Windows drive, downloads a portable Python runtime, downloads the agent code, installs dependencies, and launches the agent."),
            ("What is rescue.bat used for?",
             "It is a simple batch file (.bat) that contains the 1-line cloud rescue command. Useful for users who are more comfortable with Command Prompt (cmd) than PowerShell."),
            ("How does bootstrap.ps1 find Python on a fresh machine?",
             "It first tries 'python --version' to see if Python is installed. If not found, it downloads the portable Python package (embeddable ZIP) directly from python.org to a temp folder."),
            ("What is Portable Python and how is it downloaded?",
             "It is a lightweight version of Python (~15MB) that does not require installation — it runs directly from a folder. The bootstrap downloads it from python.org and extracts it to the temp directory."),
            ("From where are the core agent files downloaded?",
             "From the GitHub raw content URL: https://raw.githubusercontent.com/Ansh00031/Build-In-Bharat_NIT-Delhi/main/[filename]. Each core file is downloaded individually."),
            ("What files does bootstrap.ps1 download from GitHub?",
             "agent.py and all core/ module files: config.py, collector.py, executor.py, llm.py, remediation.py, security.py, snapshot.py, system_paths.py, reboot_manager.py, autostart.py, ui.py, blockchain.py"),
            ("Does WinRE have internet access by default?",
             "Usually yes, if Wi-Fi drivers are loaded. For wired ethernet connections it almost always works. For Wi-Fi in WinRE, you may need to connect manually using the WinRE network settings."),
            ("How does bootstrap.ps1 detect the offline Windows drive?",
             "It looks for a drive that contains the Windows folder (C:\\Windows or D:\\Windows) but is not the current active boot drive. It uses Get-PSDrive and Test-Path to scan available drives."),
            ("What is Invoke-WebRequest used for in the bootstrap?",
             "Invoke-WebRequest (shortened as irm = Invoke-RestMethod) is a PowerShell command that downloads content from the internet. The bootstrap uses it to download Python, agent files, and dependencies."),
            ("What dependencies are installed by bootstrap.ps1?",
             "typer, rich, pydantic, and python-dotenv — all installed via pip. These are the minimum required packages to run the agent's CLI and display."),
            ("What happens if pip is not available in WinRE?",
             "The bootstrap first tries to use pip with the portable Python. If pip is not bundled, it downloads get-pip.py from pypa.io and runs it to install pip before installing other packages."),
            ("What is the --user fallback in pip installation?",
             "If pip install fails due to permission issues, the agent retries with 'pip install --user' which installs packages to the user's local folder (no admin rights needed)."),
            ("Can the agent fix a PC that won't boot at all?",
             "Yes — if you can get into WinRE (which most PCs allow). The bootstrap handles downloading everything, and the agent can scan offline event logs and attempt repairs."),
            ("What types of errors can WinRE mode fix?",
             "Corrupt Windows Update files (via DISM), broken service configurations, incorrect registry settings, and any error that can be fixed with PowerShell commands applied to the offline Windows drive."),
            ("What is DISM and how would it be used offline?",
             "DISM (Deployment Image Servicing and Management) is a Windows tool that repairs Windows component stores. In WinRE: DISM /Image:C:\\ /Cleanup-Image /RestoreHealth repairs the offline Windows installation."),
            ("What is the rescue.bat shortcut used for in WinRE?",
             "In WinRE Command Prompt, you can run rescue.bat directly. It contains the PowerShell rescue command pre-formatted so users don't have to type the long URL manually."),
            ("What is the network requirement for WinRE recovery to work?",
             "You need internet access in WinRE (either ethernet or Wi-Fi). The total download is about 15-25MB (Python + agent files + dependencies). A mobile hotspot works fine."),
        ]
    },
    {
        "title": "CATEGORY 7: Blockchain & Algorand",
        "emoji": "🔗",
        "color": colors.HexColor("#2980B9"),
        "questions": [
            ("What is Algorand and why was it chosen?",
             "Algorand is a fast, green, and low-cost blockchain. It was chosen because: transactions confirm in ~3.3 seconds, fees are tiny (~0.001 ALGO ≈ ₹0.005), it is environmentally friendly, and it has excellent Python SDK support."),
            ("What is Algorand TestNet vs. MainNet?",
             "TestNet is a practice version of Algorand where you use fake ALGO tokens (free). MainNet is the real blockchain with real ALGO. We use TestNet for the hackathon to demonstrate the concept without real money."),
            ("What is the AlgoKit Lora Explorer?",
             "It is a web explorer for the Algorand blockchain built by the Algorand Foundation. You can view any transaction, account balance, or note content at: lora.algokit.io/testnet"),
            ("What is the URL for AlgoKit Lora TestNet Explorer?",
             "https://lora.algokit.io/testnet — you can view your transaction at: https://lora.algokit.io/testnet/transaction/YOUR_TX_ID"),
            ("What is an Algorand wallet and how is one generated?",
             "A wallet is a pair of keys: public address (like a bank account number) and private key (like a PIN). The agent generates one automatically using algosdk.account.generate_account() and saves it to .backups/algorand_wallet.json"),
            ("Where is the generated wallet stored securely?",
             "In .backups/algorand_wallet.json inside the project folder. The mnemonic phrase (24-word seed phrase) is stored there. You can also save it in the .env file as ALGORAND_MNEMONIC."),
            ("What is ALGO and how much does a transaction cost?",
             "ALGO is Algorand's native currency. Each transaction costs 0.001 ALGO (about ₹0.005 or $0.0001). For TestNet, you get free ALGO from the faucet at bank.testnet.algorand.network"),
            ("What is a free TestNet ALGO faucet?",
             "It is a website that gives you free fake ALGO for testing on TestNet. Visit: bank.testnet.algorand.network, paste your wallet address, and receive 10 free ALGO instantly."),
            ("What is the Algorand Faucet URL used in the project?",
             "https://bank.testnet.algorand.network — paste your wallet address here to receive free TestNet ALGO for testing blockchain features."),
            ("What is a SHA-256 cryptographic hash?",
             "SHA-256 is a mathematical function that converts any data into a unique 64-character fingerprint. The same data always produces the same fingerprint. Even a tiny change produces a completely different fingerprint — making it tamper-proof."),
            ("What exactly is hashed in the audit proof?",
             "The SHA-256 hash is computed from: the fix script (fix.ps1) + the rollback script (rollback.ps1) + session metadata (metadata.json). All three files are read and hashed together."),
            ("What is an ARC-0002 structured note?",
             "ARC-0002 is an Algorand standard for writing structured metadata in transaction notes. The agent writes a JSON object containing: app name, version, session ID, error code, status, SHA-256 hash, and timestamp."),
            ("What JSON fields are included in the blockchain audit note?",
             "standard (arc-0002), app (AutonomousOSDebugAgent), version (1.0.0), session_id, error_code, status, fix_title, sha256 (hash), and timestamp (UTC)."),
            ("What is a zero-ALGO self-transaction?",
             "It is a blockchain transaction that sends 0 ALGO from your wallet back to your own wallet. The purpose is not to transfer money — it is just to write the audit note into the Algorand blockchain permanently."),
            ("Why send a 0 ALGO transaction instead of a real transfer?",
             "Because we only need to write data (the audit note) to the blockchain — not transfer any money. A 0 ALGO self-transaction is the cheapest way to permanently store data on Algorand."),
            ("What is anchor_session_on_chain function?",
             "The main function in core/blockchain.py that: computes the SHA-256 hash, builds the ARC-0002 JSON note, creates a 0-ALGO transaction, signs it with your wallet, submits it to Algorand TestNet, and returns the TX ID and Lora URL."),
            ("What is get_or_create_wallet function?",
             "It checks if you have an existing Algorand wallet (in .env or .backups/algorand_wallet.json). If not, it generates a new one and saves it. Returns: (address, mnemonic, is_newly_created)."),
            ("What is get_wallet_balance function?",
             "It queries the Algorand TestNet Algod API to get the current ALGO balance of your wallet address. Returns the balance in ALGO (not microALGO)."),
            ("What is compute_session_hash function?",
             "It reads the fix.ps1, rollback.ps1, and metadata.json files from a session's .backups/ folder and computes a combined SHA-256 hash of all three files together."),
            ("What is wait_for_confirmation in the blockchain module?",
             "After submitting a transaction, this function waits (up to 5 block rounds) for the Algorand network to confirm the transaction. Returns the confirmed transaction info including the round number."),
            ("How long does it take to confirm a transaction on Algorand?",
             "Usually 3-4 seconds. Algorand has instant finality — once confirmed in a block, the transaction is permanent and can never be reversed or altered."),
            ("What is the Algorand block time?",
             "Approximately 3.3 seconds per block. This means your audit proof is permanently sealed on the blockchain within about 3-4 seconds of submission."),
            ("What is testnet-api.algonode.cloud used for?",
             "It is a free public Algorand TestNet API node maintained by Algonode. The agent connects to it to submit transactions and query account balances — no API key or account needed."),
            ("What Python library is used for Algorand interaction?",
             "py-algorand-sdk (also called algosdk). It provides functions for creating wallets, building transactions, signing them, and submitting to the Algorand network."),
            ("What is py-algorand-sdk?",
             "The official Python SDK for Algorand. Install with: pip install py-algorand-sdk. It is auto-installed by the agent if not found."),
            ("What happens if the TestNet wallet has insufficient ALGO?",
             "The anchor function checks the balance before trying to submit. If less than 0.001 ALGO (1000 microALGO) is available, it shows a message with the faucet URL to get free TestNet ALGO."),
            ("What is the --anchor flag in the diagnose command?",
             "Adding --anchor to the diagnose command automatically anchors the fix proof to Algorand TestNet after a successful fix. Example: python agent.py diagnose 0x80070005 --anchor"),
            ("What is python agent.py blockchain status?",
             "Shows your Algorand TestNet wallet address, current ALGO balance, AlgoKit Lora account explorer link, and the faucet URL to get free TestNet ALGO."),
            ("What is python agent.py blockchain anchor?",
             "Manually anchors a session's cryptographic proof to Algorand TestNet. If no session ID is given, it anchors the most recent session. Returns a Lora Explorer transaction link."),
            ("Can this be moved to Algorand MainNet for production?",
             "Yes. Just change the Algod server URL from testnet-api.algonode.cloud to mainnet-api.algonode.cloud and use real ALGO. Each anchor would cost about 0.001 ALGO (roughly ₹0.05) — very affordable for enterprises."),
        ]
    },
    {
        "title": "CATEGORY 8: Enterprise & Real-World Impact",
        "emoji": "📊",
        "color": colors.HexColor("#E67E22"),
        "questions": [
            ("What industries benefit most from this tool?",
             "IT departments in any company, hospitals (critical medical systems), banks (core banking Windows servers), schools, government offices, and individual home users with Windows PCs."),
            ("Why do enterprises need tamper-proof audit logs?",
             "By law, many industries (banking, healthcare, defense) must prove what changes were made to IT systems and who authorized them. A local log file can be deleted or edited. A blockchain entry cannot."),
            ("What compliance regulations require system change logs?",
             "ISO 27001 (Information Security), SOC 2 (Service Organization Controls), PCI DSS (Payment Card Industry), HIPAA (Healthcare), and India's IT Act all require evidence of system change management."),
            ("How does this tool help IT support teams?",
             "Instead of a Tier-1 support technician spending 45 minutes troubleshooting, the agent diagnoses and fixes the issue in 15 seconds. The support team just reviews the AI-generated fix and approves it."),
            ("How much time does the agent save per incident?",
             "Typically 30-45 minutes per incident becomes 15-30 seconds. For a company with 100 employees getting 10 OS errors per month, this saves 50+ hours of IT support time per month."),
            ("What is the cost of IT downtime for enterprises?",
             "Industry studies show IT downtime costs enterprises an average of $5,600 per minute. Reducing even 1 hour of downtime per month saves tens of thousands of dollars."),
            ("How does this tool prevent unauthorized system changes?",
             "Every fix requires explicit human Y/N approval. Every fix is recorded in .backups/ and optionally on Algorand. Any unauthorized change would show up as a discrepancy in the blockchain audit trail."),
            ("Can this be deployed across a fleet of enterprise PCs?",
             "Yes. The agent can be deployed via Group Policy or Microsoft Intune to all Windows machines in an organization. Each machine runs its own agent instance with centralized session logs."),
            ("What is the business model for commercializing this?",
             "SaaS subscription for IT teams (per-seat or per-device pricing), enterprise on-premise deployment, and an API service where IT ticketing systems can call the agent automatically when errors occur."),
            ("How does this compare to existing tools like SolarWinds?",
             "SolarWinds and similar tools monitor and alert about problems. Our tool actually diagnoses AND fixes the problem autonomously using AI reasoning. Plus our blockchain audit trail is unique in this space."),
            ("What is the competitive advantage of blockchain-backed logs?",
             "No competitor in the OS repair/IT automation space currently offers tamper-proof on-chain audit trails. This is a unique differentiator for compliance-heavy industries."),
            ("Can this tool be integrated with ticketing systems like Jira?",
             "Yes. The agent's Python API can be called programmatically. A Jira webhook could trigger python agent.py diagnose [error_code] when a new ticket is created, auto-diagnosing the issue."),
            ("What is the potential scale of this tool globally?",
             "There are over 1.6 billion Windows PCs worldwide. Even capturing 0.1% of the enterprise IT automation market represents millions of potential users."),
            ("Can this handle Linux servers in future versions?",
             "Yes. The architecture is designed to support multiple OS adapters. A Linux adapter would use journalctl (logs), systemctl (services), and bash scripts instead of PowerShell."),
            ("What are the current limitations of the project?",
             "Windows-only support, requires Python installation, no GUI interface yet, AI reasoning requires API key or local model setup, and WinRE recovery depends on internet access being available."),
        ]
    },
    {
        "title": "CATEGORY 9: Future Scope & Roadmap",
        "emoji": "🚀",
        "color": colors.HexColor("#8E44AD"),
        "questions": [
            ("What is the next planned feature after this hackathon?",
             "Linux support using systemd/journalctl, a web-based dashboard to view session history and blockchain proofs, and automated patch discovery via Windows Package Manager (WinGet)."),
            ("Will the tool support Linux and macOS?",
             "Yes. Linux support via systemd, journalctl, and bash scripts is next. macOS support via launchd and zsh scripts is planned for a later version."),
            ("What is auto patch discovery via WinGet?",
             "WinGet is Windows' built-in package manager. The agent could automatically discover outdated or broken software packages and suggest/apply updates as part of the fix workflow."),
            ("Can the tool integrate with Microsoft Intune or SCCM?",
             "Yes. Both Intune (cloud) and SCCM (on-premise) allow running PowerShell scripts on managed devices. The agent can be triggered remotely from these management platforms."),
            ("What is an enterprise SaaS model for this tool?",
             "A cloud service where enterprises pay per device per month. The service provides: AI diagnostics, session history dashboard, blockchain audit logs, team approval workflows, and compliance reports."),
            ("Can the Algorand anchor move to MainNet for production use?",
             "Yes. Simply change the API endpoint from testnet to mainnet. Each anchor costs ~0.001 ALGO (~₹0.05). For an enterprise with 1000 repairs/month, total blockchain cost is about ₹50/month."),
            ("Will there be a GUI or web dashboard version?",
             "Yes. A React/Next.js web dashboard is planned that shows: session timeline, active vs solved issues, blockchain transaction history with Lora links, and team member access controls."),
            ("Can the tool predict errors before they happen?",
             "Proactive monitoring is planned: the agent runs startup-monitor on a schedule, analyzes warning-level events (not just errors), and alerts users before a warning escalates to a critical failure."),
            ("What is the plan for multi-language support?",
             "The terminal output (Rich panels and tables) will support localization. Hindi, Tamil, Bengali, and other Indian languages are priorities given the Build with Bharat 2.0 focus."),
            ("Could this tool be integrated into a Windows 11 native widget?",
             "Potentially yes. Windows 11 supports widgets and taskbar system tray apps. A lightweight tray icon that shows system health status and alerts on errors is a planned UX improvement."),
        ]
    },
    {
        "title": "CATEGORY 10: Judge Q&A — Top 5 Critical Questions",
        "emoji": "🎤",
        "color": colors.HexColor("#C0392B"),
        "questions": [
            ("What if the AI gives a harmful command and deletes important files?",
             "This cannot happen because of 3 safety layers: (1) All diagnostic probes are read-only — they never change anything. (2) Every command is checked against our regex blacklist that blocks del, format, rmdir and similar destructive commands. (3) Even if somehow a risky fix was proposed, you must type Y to approve it — and you can see the full script before approving. Plus, we auto-create a rollback script before any fix runs."),
            ("Why not just use Windows built-in System Restore?",
             "System Restore has 4 major problems: (1) It doesn't tell you WHY something broke — no AI diagnosis. (2) It restores the ENTIRE system to a past state, which can undo your personal settings and installed software. (3) It has no blockchain audit trail for compliance. (4) It doesn't work in WinRE for boot loop scenarios. Our agent fixes ONLY the broken component, preserves everything else, and provides verifiable proof."),
            ("Is this tool safe to run on a production server?",
             "Yes, completely safe. Here's why: Read-only diagnostic probes run first with zero system changes. Every proposed fix requires mandatory human Y/N approval. Pre-fix snapshots are created automatically before anything changes. Instant rollback is available if needed. The blockchain audit trail proves exactly what was changed, when, and by whom."),
            ("How is this different from just writing a PowerShell script yourself?",
             "To write a fix yourself you'd need to: know which of 1000+ Event Viewer log channels to check, manually read and interpret cryptic error messages, know which specific PowerShell commands fix which specific errors, test the fix safely, write a rollback script, and document everything for compliance. Our agent does all of this in 15 seconds, grounded in real live telemetry, with AI reasoning, automatic safety checks, and blockchain-verified documentation."),
            ("Why does an OS debugging tool need blockchain?",
             "In enterprise IT and regulated industries, 'trust but verify' is not enough — you need 'cryptographic proof'. A local log file can be deleted, edited, or forged. An Algorand blockchain entry is permanent, mathematically tamper-proof, and independently verifiable by anyone with the transaction ID. No IT vendor, no employee, and no hacker can change or delete what is sealed on-chain. This is what makes our tool enterprise-grade."),
        ]
    },
]

# ── Build PDF ────────────────────────────────────────────────
def build_qa_pdf():
    out = "OS_Debugger_Frequently_Asked_Questions.pdf"
    doc = SimpleDocTemplate(
        out, pagesize=A4,
        rightMargin=1.8*cm, leftMargin=1.8*cm,
        topMargin=2*cm, bottomMargin=2*cm
    )
    story = []

    # ── Cover ────────────────────────────────────────────────
    story.append(Spacer(1, 1.5*cm))
    story.append(Paragraph("Autonomous OS Debugging Agent", title_s))
    story.append(Paragraph("Frequently Asked Questions (FAQ) — Comprehensive Technical & Evaluation Guide", sub_s))
    story.append(HRFlowable(width="100%", thickness=2, color=BLUE, spaceAfter=12))

    cover_data = [
        ["Team", "Debug thugs"],
        ["Members", "Ansh (Leader)  ·  Swati  ·  Aman  ·  Shivang"],
        ["Hackathon", "Build With Bharat 2.0"],
        ["Theme", "Blockchain & Web3 — Agentic Solutions (x402)"],
        ["Blockchain", "Algorand TestNet  |  lora.algokit.io/testnet"],
        ["GitHub", "github.com/Ansh00031/Build-In-Bharat_NIT-Delhi"],
        ["Total Questions", "Comprehensive FAQ covering all 10 technical categories with full answers"],
    ]
    ct = Table(cover_data, colWidths=[4*cm, 12.5*cm])
    ct.setStyle(TableStyle([
        ("FONTNAME",  (0,0), (0,-1), "Helvetica-Bold"),
        ("FONTSIZE",  (0,0), (-1,-1), 10),
        ("TEXTCOLOR", (0,0), (0,-1), BLUE),
        ("BACKGROUND",(0,0), (0,-1), colors.HexColor("#EAF4FB")),
        ("ROWBACKGROUNDS", (1,0),(1,-1), [WHITE, LGRAY]),
        ("GRID",      (0,0), (-1,-1), 0.5, BORDER),
        ("TOPPADDING",(0,0), (-1,-1), 6),
        ("BOTTOMPADDING",(0,0),(-1,-1), 6),
        ("LEFTPADDING",(0,0),(-1,-1), 10),
        ("VALIGN",    (0,0), (-1,-1), "MIDDLE"),
    ]))
    story.append(ct)
    story.append(Spacer(1, 0.5*cm))

    # Index
    story.append(Paragraph("📋  Contents", ParagraphStyle("idx",
        fontSize=12, textColor=BLUE, fontName="Helvetica-Bold",
        spaceBefore=10, spaceAfter=6)))
    for i, cat in enumerate(QA_DATA):
        story.append(Paragraph(
            f"  {cat['emoji']}  {cat['title']}  ({len(cat['questions'])} questions)",
            ParagraphStyle("il", fontSize=9.5, textColor=DARK,
                           spaceAfter=2, leftIndent=10)))
    story.append(PageBreak())

    # ── Questions ───────────────────────────────────────────
    q_counter = 1
    for cat_idx, cat in enumerate(QA_DATA):
        col = cat["color"]

        # Category header
        cat_para = Paragraph(
            f"  {cat['emoji']}  {cat['title']}",
            ParagraphStyle(f"c{cat_idx}", fontSize=13, textColor=WHITE,
                fontName="Helvetica-Bold", spaceAfter=8, spaceBefore=14,
                backColor=col, borderPad=8, leftIndent=-10))
        story.append(cat_para)

        for q_text, a_text in cat["questions"]:
            q_block = [
                Paragraph(
                    f"<b>Q{q_counter}.</b>  {q_text}",
                    ParagraphStyle(f"q{q_counter}", fontSize=10.5,
                        textColor=DARK, fontName="Helvetica-Bold",
                        spaceAfter=2, spaceBefore=6, leading=15)
                ),
                Paragraph(
                    f"<b>Ans:</b>  {a_text}",
                    ParagraphStyle(f"a{q_counter}", fontSize=10,
                        textColor=colors.HexColor("#154360"),
                        spaceAfter=4, leading=14, leftIndent=14,
                        backColor=ANS_BG, borderPad=5)
                ),
                HRFlowable(width="100%", thickness=0.4,
                           color=BORDER, spaceAfter=2),
            ]
            story.append(KeepTogether(q_block))
            q_counter += 1

        story.append(Spacer(1, 0.3*cm))
        if cat_idx < len(QA_DATA) - 1:
            story.append(PageBreak())

    # ── Back Cover ──────────────────────────────────────────
    story.append(PageBreak())
    story.append(Spacer(1, 3*cm))
    story.append(Paragraph("Team Debug thugs", title_s))
    story.append(Paragraph(
        "Autonomous OS Debugging Agent\nBlockchain & Web3 — Agentic Solutions Track",
        sub_s))
    story.append(HRFlowable(width="100%", thickness=2, color=BLUE, spaceAfter=10))
    story.append(Paragraph(
        "github.com/Ansh00031/Build-In-Bharat_NIT-Delhi  |  lora.algokit.io/testnet",
        ParagraphStyle("fc", fontSize=11, textColor=TEAL, alignment=TA_CENTER)))

    doc.build(story)
    print(f"\n✅ PDF generated: {out}")

if __name__ == "__main__":
    build_qa_pdf()
