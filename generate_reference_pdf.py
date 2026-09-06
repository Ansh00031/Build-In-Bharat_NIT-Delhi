"""Generate a professional PDF with flowcharts and 200 questions for OS Debugger."""

from reportlab.lib.pagesizes import A4
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.units import cm, inch
from reportlab.lib import colors
from reportlab.platypus import (
    SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle,
    PageBreak, HRFlowable
)
from reportlab.platypus.flowables import Flowable
from reportlab.graphics.shapes import (
    Drawing, Rect, String, Line, Polygon, Circle
)
from reportlab.graphics import renderPDF
from reportlab.lib.enums import TA_CENTER, TA_LEFT, TA_RIGHT
import os

# ─────────────────────────────────────────────────────────────
# COLORS
# ─────────────────────────────────────────────────────────────
DARK_BG     = colors.HexColor("#0D1117")
BLUE        = colors.HexColor("#1F6FEB")
GREEN       = colors.HexColor("#2EA043")
RED         = colors.HexColor("#DA3633")
YELLOW      = colors.HexColor("#D29922")
PURPLE      = colors.HexColor("#8957E5")
TEAL        = colors.HexColor("#0E8A8A")
WHITE       = colors.white
LIGHT_GRAY  = colors.HexColor("#F0F4F8")
CARD_BG     = colors.HexColor("#161B22")
BORDER      = colors.HexColor("#30363D")
TEXT_DARK   = colors.HexColor("#1A1A2E")
SECTION_BG  = colors.HexColor("#E8F4FD")

# ─────────────────────────────────────────────────────────────
# STYLES
# ─────────────────────────────────────────────────────────────
styles = getSampleStyleSheet()

title_style = ParagraphStyle("Title", parent=styles["Title"],
    fontSize=28, textColor=BLUE, spaceAfter=6, alignment=TA_CENTER,
    fontName="Helvetica-Bold")

subtitle_style = ParagraphStyle("Sub", parent=styles["Normal"],
    fontSize=13, textColor=colors.HexColor("#555555"),
    spaceAfter=20, alignment=TA_CENTER)

section_style = ParagraphStyle("Section", parent=styles["Heading1"],
    fontSize=16, textColor=WHITE, spaceAfter=8, spaceBefore=16,
    fontName="Helvetica-Bold", backColor=BLUE,
    leftIndent=-10, rightIndent=-10, borderPad=8)

subsection_style = ParagraphStyle("SubSection", parent=styles["Heading2"],
    fontSize=13, textColor=BLUE, spaceAfter=6, spaceBefore=10,
    fontName="Helvetica-Bold")

body_style = ParagraphStyle("Body", parent=styles["Normal"],
    fontSize=10, textColor=TEXT_DARK, spaceAfter=4, leading=15)

question_style = ParagraphStyle("Q", parent=styles["Normal"],
    fontSize=10, textColor=TEXT_DARK, spaceAfter=3,
    leftIndent=10, leading=14)

answer_style = ParagraphStyle("A", parent=styles["Normal"],
    fontSize=9.5, textColor=colors.HexColor("#1A5276"),
    spaceAfter=8, leftIndent=22, leading=13,
    fontName="Helvetica-Oblique")

category_style = ParagraphStyle("Cat", parent=styles["Heading3"],
    fontSize=12, textColor=WHITE, spaceAfter=6, spaceBefore=12,
    fontName="Helvetica-Bold", backColor=TEAL,
    leftIndent=-6, borderPad=5)

# ─────────────────────────────────────────────────────────────
# FLOWCHART HELPER: Box + Arrow Drawing
# ─────────────────────────────────────────────────────────────
def make_box(d, x, y, w, h, text, fill=BLUE, text_color=WHITE,
             font_size=8, radius=6, border=None):
    border_color = border or fill
    d.add(Rect(x, y, w, h, rx=radius, ry=radius,
               fillColor=fill, strokeColor=border_color, strokeWidth=1.5))
    # word wrap manually
    words = text.split("\n")
    line_h = font_size + 3
    total_h = len(words) * line_h
    start_y = y + h / 2 + total_h / 2 - line_h
    for i, line in enumerate(words):
        d.add(String(x + w / 2, start_y - i * line_h,
                     line, fontSize=font_size,
                     fillColor=text_color,
                     textAnchor="middle",
                     fontName="Helvetica-Bold"))

def arrow_down(d, x, y, length=22, color=colors.HexColor("#555")):
    d.add(Line(x, y, x, y - length, strokeColor=color, strokeWidth=1.5))
    d.add(Polygon([x - 5, y - length, x + 5, y - length, x, y - length - 8],
                  fillColor=color, strokeColor=color))

def arrow_right(d, x, y, length=30, color=colors.HexColor("#555")):
    d.add(Line(x, y, x + length, y, strokeColor=color, strokeWidth=1.5))
    d.add(Polygon([x + length, y + 4, x + length, y - 4, x + length + 8, y],
                  fillColor=color, strokeColor=color))

def diamond(d, x, y, w, h, text, fill=YELLOW):
    cx, cy = x + w / 2, y + h / 2
    pts = [cx, y + h, x + w, cy, cx, y, x, cy]
    d.add(Polygon(pts, fillColor=fill, strokeColor=colors.HexColor("#8a6d00"),
                  strokeWidth=1.5))
    lines = text.split("\n")
    line_h = 8
    start_y = cy + (len(lines) - 1) * line_h / 2
    for i, line in enumerate(lines):
        d.add(String(cx, start_y - i * line_h, line,
                     fontSize=7.5, fillColor=TEXT_DARK,
                     textAnchor="middle", fontName="Helvetica-Bold"))

# ─────────────────────────────────────────────────────────────
# FLOWCHART 1: Main System Workflow
# ─────────────────────────────────────────────────────────────
def build_main_flowchart():
    W, H = 475, 700
    d = Drawing(W, H)
    d.add(Rect(0, 0, W, H, fillColor=colors.HexColor("#F8FBFF"),
               strokeColor=BORDER, strokeWidth=1))

    # Title
    d.add(String(W/2, H - 18, "System Workflow Flowchart",
                 fontSize=12, fillColor=BLUE, textAnchor="middle",
                 fontName="Helvetica-Bold"))

    cx = W / 2
    bw = 190  # box width
    bh = 28   # box height

    # Step 1 — Start
    y = H - 50
    make_box(d, cx - bw/2, y, bw, bh,
             "User: python agent.py diagnose 0x80070005",
             fill=BLUE, font_size=7.5)
    arrow_down(d, cx, y, length=18)

    # Step 2 — Admin Check Diamond
    y -= 62
    diamond(d, cx - 52, y, 104, 40, "Admin /\nElevated?", fill=YELLOW)
    arrow_down(d, cx, y - 8, length=18)

    # No branch (left)
    d.add(Line(cx - 52, y + 20, cx - 115, y + 20,
               strokeColor=RED, strokeWidth=1.5))
    d.add(Line(cx - 115, y + 20, cx - 115, y - 16,
               strokeColor=RED, strokeWidth=1.5))
    make_box(d, cx - 190, y - 26, 75, 20,
             "Show Warning\nContinue?", fill=RED, font_size=6.5)
    d.add(String(cx - 75, y + 24, "No", fontSize=7,
                 fillColor=RED, textAnchor="middle"))
    d.add(String(cx + 8, y - 14, "Yes", fontSize=7,
                 fillColor=GREEN, textAnchor="middle"))

    # Step 3 — Gather Context
    y -= 60
    make_box(d, cx - bw/2, y, bw, bh,
             "Gather OS Metadata & System Context",
             fill=TEAL, font_size=7.5)
    arrow_down(d, cx, y, length=18)

    # Step 4 — Ingest Logs
    y -= 50
    make_box(d, cx - bw/2, y, bw, bh,
             "Ingest Live Windows Event Viewer Logs\n(System / Application / WindowsUpdate)",
             fill=TEAL, font_size=7)
    arrow_down(d, cx, y, length=18)

    # Step 5 — AI Stage 1
    y -= 50
    make_box(d, cx - bw/2, y, bw, bh,
             "AI Stage 1: Hypothesis Formulation\nAnalyze error + generate diagnostic plan",
             fill=PURPLE, font_size=7)
    arrow_down(d, cx, y, length=18)

    # Step 6 — Probe Commands
    y -= 50
    make_box(d, cx - bw/2, y, bw, bh,
             "Generate Read-Only Diagnostic Probes\nicacls  Get-Service  Get-WinEvent",
             fill=PURPLE, font_size=7)
    arrow_down(d, cx, y, length=18)

    # Step 7 — Security Filter Diamond
    y -= 62
    diamond(d, cx - 56, y, 112, 40, "Security Blacklist\nFilter Check?", fill=YELLOW)
    d.add(String(cx - 8, y - 14, "Safe", fontSize=7,
                 fillColor=GREEN, textAnchor="middle"))
    d.add(String(cx + 64, y + 24, "Dangerous!", fontSize=7,
                 fillColor=RED, textAnchor="start"))
    d.add(Line(cx + 56, y + 20, cx + 140, y + 20,
               strokeColor=RED, strokeWidth=1.5))
    make_box(d, cx + 98, y + 6, 80, 20,
             "Block & Skip", fill=RED, font_size=6.5)
    arrow_down(d, cx, y - 8, length=18)

    # Step 8 — Execute Commands
    y -= 52
    make_box(d, cx - bw/2, y, bw, bh,
             "Execute Diagnostic Commands Safely\nRead-Only  Sandboxed",
             fill=GREEN, font_size=7)
    arrow_down(d, cx, y, length=18)

    # Step 9 — AI Stage 2
    y -= 50
    make_box(d, cx - bw/2, y, bw, bh,
             "AI Stage 2: Root Cause Confirmation\nIngest command output evidence",
             fill=PURPLE, font_size=7)
    arrow_down(d, cx, y, length=18)

    # Step 10 — Generate Fix
    y -= 50
    make_box(d, cx - bw/2, y, bw, bh,
             "AI Stage 3: Generate Fix Script\nTargeted PowerShell Remediation",
             fill=PURPLE, font_size=7)
    arrow_down(d, cx, y, length=18)

    # Step 11 — Show & Gate Diamond
    y -= 62
    diamond(d, cx - 52, y, 104, 40, "User Approves\nFix? (Y/N)", fill=YELLOW)
    d.add(String(cx - 8, y - 14, "Yes", fontSize=7,
                 fillColor=GREEN, textAnchor="middle"))
    d.add(String(cx + 62, y + 24, "No -> Exit Safely", fontSize=7,
                 fillColor=RED, textAnchor="start"))
    arrow_down(d, cx, y - 8, length=18)

    # Step 12 — Snapshot + Execute + Verify
    y -= 50
    make_box(d, cx - bw/2, y, bw, bh,
             "Pre-Fix Snapshot -> Execute Fix -> Verify\n.backups/  rollback.ps1 saved",
             fill=GREEN, font_size=7)
    arrow_down(d, cx, y, length=18)

    # Step 13 — Final Report
    y -= 50
    make_box(d, cx - bw/2, y, bw, bh,
             "Final Report + Blockchain Anchor\nAlgorand TestNet + AlgoKit Lora",
             fill=BLUE, font_size=7)

    return d


# ─────────────────────────────────────────────────────────────
# FLOWCHART 2: AI Agent Architecture
# ─────────────────────────────────────────────────────────────
def build_ai_flowchart():
    W, H = 470, 340
    d = Drawing(W, H)
    d.add(Rect(0, 0, W, H, fillColor=colors.HexColor("#F8FBFF"),
               strokeColor=BORDER, strokeWidth=1))
    d.add(String(W/2, H - 18, "AI Agent Architecture Flow",
                 fontSize=12, fillColor=PURPLE, textAnchor="middle",
                 fontName="Helvetica-Bold"))

    # 4 columns: INPUT | AI ENGINE | SAFETY | OUTPUT
    cols = [("📥 INPUT", TEAL, 10),
            ("🧠 AI ENGINE", PURPLE, 135),
            ("🛡️ SAFETY", RED, 265),
            ("📤 OUTPUT", GREEN, 385)]

    for label, col, x in cols:
        make_box(d, x, H - 52, 110, 24, label, fill=col, font_size=9)

    # Input items
    items_in = ["Error Code\n0x80070005",
                "Windows Event\nLogs",
                "OS Metadata",
                "Live Service\nStates"]
    for i, txt in enumerate(items_in):
        make_box(d, 10, H - 90 - i * 52, 110, 38,
                 txt, fill=colors.HexColor("#E8F4FD"),
                 text_color=TEAL, border=TEAL, font_size=7)

    # AI Engine items
    ai_items = ["Stage 1: Hypothesis\nFormulation",
                "Stage 2: Diagnostic\nCommand Gen",
                "Stage 3: Root Cause\nConfirmation",
                "Stage 4: Fix Script\nSynthesis"]
    for i, txt in enumerate(ai_items):
        make_box(d, 135, H - 90 - i * 52, 110, 38,
                 txt, fill=colors.HexColor("#F3E8FF"),
                 text_color=PURPLE, border=PURPLE, font_size=7)

    # Safety items
    safety_items = ["Regex Command\nBlacklist",
                    "Read-Only\nEnforcement",
                    "Human Y/N\nApproval Gate",
                    "Temp File\nSandbox"]
    for i, txt in enumerate(safety_items):
        make_box(d, 265, H - 90 - i * 52, 110, 38,
                 txt, fill=colors.HexColor("#FFEAEA"),
                 text_color=RED, border=RED, font_size=7)

    # Output items
    out_items = ["Syntax-Highlighted\nFix Script",
                 "Pre-Fix Snapshot\n.backups/",
                 "Algorand Proof\nLora Explorer",
                 "1-Click Rollback\nrollback.ps1"]
    for i, txt in enumerate(out_items):
        make_box(d, 385, H - 90 - i * 52, 110, 38,
                 txt, fill=colors.HexColor("#E8FFE8"),
                 text_color=GREEN, border=GREEN, font_size=7)

    # Arrows between columns
    for i in range(4):
        y_mid = H - 90 - i * 52 + 19
        arrow_right(d, 120, y_mid, 15)
        arrow_right(d, 245, y_mid, 20)
        arrow_right(d, 375, y_mid, 10)

    return d


# ─────────────────────────────────────────────────────────────
# FLOWCHART 3: WinRE Cloud Recovery
# ─────────────────────────────────────────────────────────────
def build_winre_flowchart():
    W, H = 470, 330
    d = Drawing(W, H)
    d.add(Rect(0, 0, W, H, fillColor=colors.HexColor("#F8FBFF"),
               strokeColor=BORDER, strokeWidth=1))
    d.add(String(W/2, H - 18, "WinRE Cloud Recovery Flow",
                 fontSize=12, fillColor=RED, textAnchor="middle",
                 fontName="Helvetica-Bold"))

    cx = W / 2
    bw = 280
    bh = 30
    steps = [
        ("💻 PC Stuck — Boot Loop / Won't Start", RED),
        ("User Boots into Windows Recovery (WinRE)", RED),
        ("Opens WinRE Command Prompt", colors.HexColor("#8B4513")),
        ("Runs: irm .../bootstrap.ps1 | iex", BLUE),
        ("bootstrap.ps1 Downloads from GitHub", BLUE),
        ("Detects Offline C:\\ Windows Drive", TEAL),
        ("Downloads Portable Python (~15MB)", TEAL),
        ("Downloads agent.py + core/*.py", TEAL),
        ("Auto-Installs: typer, rich, pydantic", GREEN),
        ("✅ Launches startup-monitor → Machine Diagnosed!", GREEN),
    ]

    y = H - 55
    for txt, col in steps:
        make_box(d, cx - bw/2, y, bw, bh, txt,
                 fill=col, font_size=7.5)
        if txt != steps[-1][0]:
            arrow_down(d, cx, y, length=16)
        y -= 28

    return d


# ─────────────────────────────────────────────────────────────
# QUESTIONS DATA
# ─────────────────────────────────────────────────────────────
QUESTIONS = [
    ("🔵 CATEGORY 1: Basic Project Understanding (Q1–Q20)", [
        ("Q1", "What is the Autonomous OS Debugging Agent?", None),
        ("Q2", "What problem does this project solve?", None),
        ("Q3", "Why can't users just use ChatGPT to fix OS errors?", None),
        ("Q4", "What does the term 'autonomous' mean in this context?", None),
        ("Q5", "What is an OS error code like 0x80070005?", None),
        ("Q6", "What does '0x80070005: Access Denied' mean on Windows?", None),
        ("Q7", "Who is the target user for this tool?", None),
        ("Q8", "Is this project open-source? Where is the code?", None),
        ("Q9", "What operating systems does it support?", None),
        ("Q10", "What programming language is the project built in?", None),
        ("Q11", "What is the 'AI mechanic inside your terminal' analogy?", None),
        ("Q12", "How is this different from a standard antivirus tool?", None),
        ("Q13", "How long does a traditional IT support ticket take vs. your tool?", None),
        ("Q14", "What is the main CLI command to start diagnosis?", None),
        ("Q15", "Does the user need to know PowerShell to use this tool?", None),
        ("Q16", "What is the minimum Python version required?", None),
        ("Q17", "Does the tool require internet to work?", None),
        ("Q18", "Can it work fully offline?", None),
        ("Q19", "What is the GitHub repository link for this project?", None),
        ("Q20", "What was the inspiration behind building this?", None),
    ]),
    ("🧠 CATEGORY 2: AI Engine & Reasoning Loop (Q21–Q50)", [
        ("Q21", "What AI model powers the diagnostic reasoning?", None),
        ("Q22", "What is 'hallucination' in AI and why is it dangerous for OS repair?", None),
        ("Q23", "How does the agent avoid hallucinations?", None),
        ("Q24", "What is the Active Telemetry Reasoning Loop?", None),
        ("Q25", "What are the 5 stages of the AI reasoning pipeline?", None),
        ("Q26", "What is 'hypothesis formulation' in Stage 1?", None),
        ("Q27", "What are read-only diagnostic probes?", None),
        ("Q28", "What is icacls and what does it check?", None),
        ("Q29", "What is Get-Service used for in diagnostics?", None),
        ("Q30", "What is Get-WinEvent and which logs does it read?", None),
        ("Q31", "How does the AI confirm the root cause in Stage 3?", None),
        ("Q32", "What information is fed back to the AI after probes run?", None),
        ("Q33", "What is a 'remediation script' in Stage 4?", None),
        ("Q34", "What language are remediation scripts written in?", None),
        ("Q35", "How does the AI structure its JSON output for fix proposals?", None),
        ("Q36", "What is the verification command in Stage 5?", None),
        ("Q37", "Can the AI work without an OpenAI API key?", None),
        ("Q38", "What happens in offline/heuristic mode without an API key?", None),
        ("Q39", "Can you use a local LLM like Ollama or Llama 3.1?", None),
        ("Q40", "How do you configure Ollama as the AI backend?", None),
        ("Q41", "What is the OPENAI_BASE_URL setting used for?", None),
        ("Q42", "What is the LLM_MODEL environment variable?", None),
        ("Q43", "How does the agent handle LLM rate limits or timeouts?", None),
        ("Q44", "What is a JSON Schema prompt and why use strict JSON?", None),
        ("Q45", "What happens if the AI returns malformed JSON?", None),
        ("Q46", "How does the agent ensure the AI stays on topic?", None),
        ("Q47", "Can the AI diagnose Linux errors too?", None),
        ("Q48", "What Windows Event Viewer channels does the agent read?", None),
        ("Q49", "How many event log entries does it collect by default?", None),
        ("Q50", "What is the --max-events flag used for?", None),
    ]),
    ("🛡️ CATEGORY 3: Security & Safety (Q51–Q80)", [
        ("Q51", "What is the Security Guardrail / Command Blacklist?", None),
        ("Q52", "Which commands are blocked by the blacklist?", None),
        ("Q53", "How is the blacklist implemented technically?", None),
        ("Q54", "Can the blacklist be bypassed?", None),
        ("Q55", "What is the Human-in-the-Loop (HITL) gate?", None),
        ("Q56", "What exactly is shown to the user before executing a fix?", None),
        ("Q57", "What happens if the user selects 'N' at the approval gate?", None),
        ("Q58", "What is a 'read-only diagnostic probe' vs. a 'write command'?", None),
        ("Q59", "How are diagnostic commands sandboxed?", None),
        ("Q60", "What is the temp file sandbox execution model?", None),
        ("Q61", "Are fix scripts auto-deleted after execution?", None),
        ("Q62", "What is a pre-fix snapshot?", None),
        ("Q63", "Where are snapshots stored on disk?", None),
        ("Q64", "What does a snapshot contain?", None),
        ("Q65", "What is a rollback script?", None),
        ("Q66", "How is the rollback script generated?", None),
        ("Q67", "How long does a rollback take to execute?", None),
        ("Q68", "What is 'python agent.py rollback' and when do you use it?", None),
        ("Q69", "Can you rollback multiple sessions?", None),
        ("Q70", "What happens if the rollback script itself fails?", None),
        ("Q71", "What is Administrator privilege and why is it required?", None),
        ("Q72", "What is --skip-admin-check flag and when should it be used?", None),
        ("Q73", "What is dry-run mode?", None),
        ("Q74", "Can a standard (non-admin) user run the agent?", None),
        ("Q75", "What are the most common dangerous commands blocked?", None),
        ("Q76", "Does the agent access the internet during diagnosis?", None),
        ("Q77", "Can the agent modify the Windows Registry?", None),
        ("Q78", "What is the difference between diagnosis phase and remediation phase?", None),
        ("Q79", "How does the agent handle timeouts on diagnostic commands?", None),
        ("Q80", "What is the execute_diagnostic_command function?", None),
    ]),
    ("💾 CATEGORY 4: Sessions, Snapshots & Rollback (Q81–Q100)", [
        ("Q81", "What is a session ID and how is it generated?", None),
        ("Q82", "Where are all sessions stored?", None),
        ("Q83", "What is the .backups/ directory structure?", None),
        ("Q84", "What files are inside a session's backup folder?", None),
        ("Q85", "What is metadata.json in a session?", None),
        ("Q86", "What is fix.ps1 in a session?", None),
        ("Q87", "What is rollback.ps1 in a session?", None),
        ("Q88", "What is the 'history' command used for?", None),
        ("Q89", "How do you view all past sessions?", None),
        ("Q90", "What session statuses exist? (COMPLETED, FAILED, ROLLED_BACK...)", None),
        ("Q91", "What is VERIFIED_POST_REBOOT status?", None),
        ("Q92", "What is blockchain_receipt.json inside a session?", None),
        ("Q93", "Can you delete a session's backup manually?", None),
        ("Q94", "What happens to the session if rollback is executed?", None),
        ("Q95", "How many sessions are stored by default?", None),
        ("Q96", "Is there a cleanup or expiry for old sessions?", None),
        ("Q97", "What is the update_session_status function?", None),
        ("Q98", "What is the get_session function?", None),
        ("Q99", "What is the list_sessions function?", None),
        ("Q100", "How does the rollback command find the most recent session?", None),
    ]),
    ("🔄 CATEGORY 5: Auto-Start & Reboot Management (Q101–Q120)", [
        ("Q101", "What is the enable-autostart command?", None),
        ("Q102", "Where is the startup batch file created on Windows?", None),
        ("Q103", "What does the startup batch file do on boot?", None),
        ("Q104", "What is the disable-autostart command?", None),
        ("Q105", "What is the startup-monitor command?", None),
        ("Q106", "What is the difference between Active Problems and Solved Problems?", None),
        ("Q107", "What services does startup-monitor check live?", None),
        ("Q108", "What is the startup-log command?", None),
        ("Q109", "Where is the startup execution log stored?", None),
        ("Q110", "What is the Windows RunOnce registry key?", None),
        ("Q111", "What is register_reboot_hook used for?", None),
        ("Q112", "What registry path is used for the RunOnce hook?", None),
        ("Q113", "What command is registered in RunOnce after a fix?", None),
        ("Q114", "What is python agent.py resume <session_id>?", None),
        ("Q115", "When does the resume command fire automatically?", None),
        ("Q116", "What is unregister_reboot_hook used for?", None),
        ("Q117", "Why is it important to unregister the hook after it fires?", None),
        ("Q118", "What is is_reboot_pending() checking?", None),
        ("Q119", "Which Windows registry keys indicate a pending reboot?", None),
        ("Q120", "What happens if a reboot is needed but the user declines?", None),
    ]),
    ("🌐 CATEGORY 6: WinRE Cloud Recovery (Q121–Q140)", [
        ("Q121", "What is Windows Recovery Environment (WinRE)?", None),
        ("Q122", "How do you enter WinRE on a Windows machine?", None),
        ("Q123", "What is the 1-line cloud rescue command?", None),
        ("Q124", "What is bootstrap.ps1 and what does it do?", None),
        ("Q125", "What is rescue.bat used for?", None),
        ("Q126", "How does bootstrap.ps1 find Python on a fresh machine?", None),
        ("Q127", "What is Portable Python and how is it downloaded?", None),
        ("Q128", "From where are the core agent files downloaded?", None),
        ("Q129", "What files does bootstrap.ps1 download from GitHub?", None),
        ("Q130", "Does WinRE have internet access by default?", None),
        ("Q131", "How does bootstrap.ps1 detect the offline Windows drive?", None),
        ("Q132", "What is Invoke-WebRequest used for in the bootstrap?", None),
        ("Q133", "What dependencies are installed by bootstrap.ps1?", None),
        ("Q134", "What happens if pip is not available in WinRE?", None),
        ("Q135", "What is the --user fallback in pip installation?", None),
        ("Q136", "Can the agent fix a PC that won't boot at all?", None),
        ("Q137", "What types of errors can WinRE mode fix?", None),
        ("Q138", "What is DISM and how would it be used offline?", None),
        ("Q139", "What is the rescue.bat shortcut used for in WinRE?", None),
        ("Q140", "What is the network requirement for WinRE recovery?", None),
    ]),
    ("🔗 CATEGORY 7: Blockchain & Algorand (Q141–Q170)", [
        ("Q141", "What is Algorand and why was it chosen?", None),
        ("Q142", "What is Algorand TestNet vs. MainNet?", None),
        ("Q143", "What is the AlgoKit Lora Explorer?", None),
        ("Q144", "What is the URL for AlgoKit Lora TestNet Explorer?", None),
        ("Q145", "What is an Algorand wallet and how is one generated?", None),
        ("Q146", "Where is the generated wallet stored securely?", None),
        ("Q147", "What is ALGO and how much does a transaction cost?", None),
        ("Q148", "What is a free TestNet ALGO faucet?", None),
        ("Q149", "What is the Algorand Faucet URL used in the project?", None),
        ("Q150", "What is a SHA-256 cryptographic hash?", None),
        ("Q151", "What exactly is hashed in the audit proof?", None),
        ("Q152", "What is an ARC-0002 structured note?", None),
        ("Q153", "What JSON fields are included in the blockchain audit note?", None),
        ("Q154", "What is a zero-ALGO self-transaction?", None),
        ("Q155", "Why send a 0 ALGO transaction instead of a real transfer?", None),
        ("Q156", "What is anchor_session_on_chain function?", None),
        ("Q157", "What is get_or_create_wallet function?", None),
        ("Q158", "What is get_wallet_balance function?", None),
        ("Q159", "What is compute_session_hash function?", None),
        ("Q160", "What is wait_for_confirmation in the blockchain module?", None),
        ("Q161", "How long does it take to confirm a transaction on Algorand?", None),
        ("Q162", "What is the Algorand block time?", None),
        ("Q163", "What is testnet-api.algonode.cloud used for?", None),
        ("Q164", "What Python library is used for Algorand interaction?", None),
        ("Q165", "What is py-algorand-sdk?", None),
        ("Q166", "What happens if the TestNet wallet has insufficient ALGO?", None),
        ("Q167", "What is the --anchor flag in the diagnose command?", None),
        ("Q168", "What is python agent.py blockchain status?", None),
        ("Q169", "What is python agent.py blockchain anchor?", None),
        ("Q170", "Can this be moved to Algorand MainNet for production?", None),
    ]),
    ("📊 CATEGORY 8: Enterprise & Real-World Impact (Q171–Q185)", [
        ("Q171", "What industries benefit most from this tool?", None),
        ("Q172", "Why do enterprises need tamper-proof audit logs?", None),
        ("Q173", "What compliance regulations require system change logs?", None),
        ("Q174", "How does this tool help IT support teams?", None),
        ("Q175", "How much time does the agent save per incident?", None),
        ("Q176", "What is the cost of IT downtime for enterprises?", None),
        ("Q177", "How does this tool prevent unauthorized system changes?", None),
        ("Q178", "Can this be deployed across a fleet of enterprise PCs?", None),
        ("Q179", "What is the business model for commercializing this?", None),
        ("Q180", "How does this compare to existing tools like SolarWinds?", None),
        ("Q181", "What is the competitive advantage of blockchain-backed logs?", None),
        ("Q182", "Can this tool be integrated with ticketing systems like Jira?", None),
        ("Q183", "What is the potential scale of this tool globally?", None),
        ("Q184", "Can this handle Linux servers in future versions?", None),
        ("Q185", "What are the current limitations of the project?", None),
    ]),
    ("🚀 CATEGORY 9: Future Scope (Q186–Q195)", [
        ("Q186", "What is the next planned feature after this hackathon?", None),
        ("Q187", "Will the tool support Linux and macOS?", None),
        ("Q188", "What is auto patch discovery via WinGet?", None),
        ("Q189", "Can the tool integrate with Microsoft Intune or SCCM?", None),
        ("Q190", "What is an enterprise SaaS model for this tool?", None),
        ("Q191", "Can the Algorand anchor move to MainNet for production use?", None),
        ("Q192", "Will there be a GUI or web dashboard version?", None),
        ("Q193", "Can the tool predict errors before they happen?", None),
        ("Q194", "What is the plan for multi-language support?", None),
        ("Q195", "Could this tool be integrated into a Windows 11 native widget?", None),
    ]),
    ("🎤 CATEGORY 10: Judge Q&A — Top 5 Critical Questions (Q196–Q200)", [
        ("Q196", "What if the AI gives a harmful command and deletes important files?",
         "Read-only probes run first. Every command is validated against a strict regex blacklist. Nothing runs without explicit Y/N user approval. And if anything goes wrong, 'python agent.py rollback' restores everything in under 1 second."),
        ("Q197", "Why not just use Windows built-in System Restore?",
         "System Restore doesn't tell you WHY something broke, doesn't use AI reasoning, doesn't generate verified fix scripts, and has no blockchain audit trail. Our tool diagnoses, explains, fixes, AND proves it on-chain."),
        ("Q198", "Is this tool safe to run on a production server?",
         "Yes — read-only probes first, blacklisted destructive commands, mandatory human Y/N approval, and pre-fix snapshots with 1-click rollback guarantee zero unintended risk."),
        ("Q199", "How is this different from just writing a PowerShell script yourself?",
         "You'd need to read logs manually, interpret output, write the correct targeted fix, test it safely, and handle rollback — all manually. Our tool does all of this autonomously, grounded in live telemetry, in 15 seconds."),
        ("Q200", "Why does an OS debugging tool need blockchain?",
         "Enterprise and government IT demands an immutable, third-party-verifiable audit trail. A local log file can be edited or deleted. An Algorand blockchain entry cannot be changed by anyone — ever."),
    ]),
]

# ─────────────────────────────────────────────────────────────
# BUILD PDF
# ─────────────────────────────────────────────────────────────
def build_pdf():
    out_path = "OS_Debugger_Flowchart_and_200_Questions.pdf"
    doc = SimpleDocTemplate(
        out_path,
        pagesize=A4,
        rightMargin=1.8 * cm,
        leftMargin=1.8 * cm,
        topMargin=2 * cm,
        bottomMargin=2 * cm,
    )

    story = []

    # ── Cover ──────────────────────────────────────────────
    story.append(Spacer(1, 1.5 * cm))
    story.append(Paragraph("Autonomous OS Debugging Agent", title_style))
    story.append(Paragraph("Complete Technical Reference: Flowcharts + 200 Q&A", subtitle_style))
    story.append(HRFlowable(width="100%", thickness=2, color=BLUE, spaceAfter=10))

    info_data = [
        ["Team", "KernelHealers"],
        ["Members", "Ansh (Leader)  ·  Swati  ·  Aman  ·  Shivang"],
        ["Hackathon Theme", "Blockchain & Web3 — Agentic Solutions (x402)"],
        ["Blockchain", "Algorand TestNet  |  AlgoKit Lora Explorer"],
        ["GitHub", "github.com/Ansh00031/SGU-AI-Thon"],
    ]
    info_table = Table(info_data, colWidths=[4 * cm, 12 * cm])
    info_table.setStyle(TableStyle([
        ("BACKGROUND", (0, 0), (0, -1), SECTION_BG),
        ("FONTNAME", (0, 0), (0, -1), "Helvetica-Bold"),
        ("FONTSIZE", (0, 0), (-1, -1), 10),
        ("TEXTCOLOR", (0, 0), (0, -1), BLUE),
        ("ROWBACKGROUNDS", (1, 0), (1, -1), [WHITE, LIGHT_GRAY]),
        ("GRID", (0, 0), (-1, -1), 0.5, BORDER),
        ("TOPPADDING", (0, 0), (-1, -1), 6),
        ("BOTTOMPADDING", (0, 0), (-1, -1), 6),
        ("LEFTPADDING", (0, 0), (-1, -1), 10),
    ]))
    story.append(info_table)
    story.append(PageBreak())

    # ── Section 1: Main Flowchart ────────────────────────
    story.append(Paragraph("  📊  SECTION 1: System Workflow Flowchart", section_style))
    story.append(Spacer(1, 0.3 * cm))
    story.append(Paragraph(
        "The flowchart below shows the complete end-to-end pipeline of the Autonomous OS Debugging Agent "
        "— from the moment a user runs the diagnose command to the final blockchain-anchored audit proof.",
        body_style))
    story.append(Spacer(1, 0.3 * cm))
    fc1 = build_main_flowchart()
    story.append(fc1)
    story.append(PageBreak())

    # ── Section 2: AI Architecture Flowchart ────────────
    story.append(Paragraph("  🤖  SECTION 2: AI Agent Architecture", section_style))
    story.append(Spacer(1, 0.3 * cm))
    story.append(Paragraph(
        "The AI Agent operates across 4 layers: Input (telemetry), AI Engine (5-stage reasoning), "
        "Safety (blacklist + human gate), and Output (fix, snapshot, blockchain proof, rollback).",
        body_style))
    story.append(Spacer(1, 0.3 * cm))
    fc2 = build_ai_flowchart()
    story.append(fc2)
    story.append(Spacer(1, 0.5 * cm))

    # ── Section 3: WinRE Recovery Flowchart ─────────────
    story.append(Paragraph("  🌐  SECTION 3: WinRE Cloud Recovery Flow", section_style))
    story.append(Spacer(1, 0.3 * cm))
    story.append(Paragraph(
        "When a PC is completely unbootable (stuck in a boot loop), the agent can be downloaded and run "
        "entirely from the Windows Recovery Environment (WinRE) using a single command line.",
        body_style))
    story.append(Spacer(1, 0.3 * cm))
    fc3 = build_winre_flowchart()
    story.append(fc3)
    story.append(PageBreak())

    # ── Section 4: 200 Questions ─────────────────────────
    story.append(Paragraph("  ❓  SECTION 4: 200 Important Questions", section_style))
    story.append(Spacer(1, 0.3 * cm))

    for cat_title, qs in QUESTIONS:
        story.append(Paragraph(f"  {cat_title}", category_style))
        story.append(Spacer(1, 0.15 * cm))

        q_data = []
        for qnum, qtext, answer in qs:
            q_data.append([
                Paragraph(f"<b>{qnum}</b>", ParagraphStyle("Qnum",
                    fontSize=9, textColor=BLUE, fontName="Helvetica-Bold")),
                Paragraph(qtext, question_style),
            ])
            if answer:
                q_data.append([
                    Paragraph("→", ParagraphStyle("arr",
                        fontSize=9, textColor=GREEN, alignment=TA_CENTER)),
                    Paragraph(f"<i>{answer}</i>", answer_style),
                ])

        q_table = Table(q_data, colWidths=[1.2 * cm, 15 * cm])
        q_table.setStyle(TableStyle([
            ("VALIGN", (0, 0), (-1, -1), "TOP"),
            ("ROWBACKGROUNDS", (0, 0), (-1, -1), [WHITE, colors.HexColor("#F7FBFF")]),
            ("LINEBELOW", (0, 0), (-1, -1), 0.3, colors.HexColor("#E0E0E0")),
            ("TOPPADDING", (0, 0), (-1, -1), 4),
            ("BOTTOMPADDING", (0, 0), (-1, -1), 4),
            ("LEFTPADDING", (0, 0), (-1, -1), 5),
        ]))
        story.append(q_table)
        story.append(Spacer(1, 0.3 * cm))

    # ── Back Cover ───────────────────────────────────────
    story.append(PageBreak())
    story.append(Spacer(1, 3 * cm))
    story.append(Paragraph("Team KernelHealers", title_style))
    story.append(Paragraph(
        "Autonomous OS Debugging Agent — Blockchain & Web3 Track\n"
        "Build With भारत 2.0 Hackathon",
        subtitle_style))
    story.append(Spacer(1, 1 * cm))
    story.append(HRFlowable(width="100%", thickness=2, color=BLUE))
    story.append(Spacer(1, 0.5 * cm))
    story.append(Paragraph(
        "github.com/Ansh00031/SGU-AI-Thon  |  "
        "lora.algokit.io/testnet",
        ParagraphStyle("footer", fontSize=11, textColor=TEAL,
                       alignment=TA_CENTER)))

    doc.build(story)
    print(f"\n✅ PDF successfully generated: {out_path}")
    return out_path


if __name__ == "__main__":
    build_pdf()
