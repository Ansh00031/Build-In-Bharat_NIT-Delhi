"""Generate the complete CODEARAMBH 2.0 Presentation matching the official Halloween-theme template.

Features distinct dynamic layouts across all 9 slides:
- 1-line clear problem statement in easy language
- Interactive interconnected visual flowchart with arrows & tech matrix
- Big stat number callouts, 2x2 quadrant grids, terminal mockup, and distinct badges
"""

import os
import sys
import subprocess
from pathlib import Path

# Auto-install required packages if missing
for pkg in ["python-pptx", "pypdf", "pillow"]:
    try:
        __import__(pkg.replace("-", "_"))
    except ImportError:
        try:
            subprocess.check_call([sys.executable, "-m", "pip", "install", pkg, "--break-system-packages", "--quiet"])
        except Exception:
            subprocess.check_call([sys.executable, "-m", "pip", "install", pkg, "--quiet"])

HAS_FITZ = False
try:
    import fitz  # PyMuPDF
    HAS_FITZ = True
except ImportError:
    try:
        subprocess.check_call([sys.executable, "-m", "pip", "install", "pymupdf", "--break-system-packages", "--quiet"])
        import fitz
        HAS_FITZ = True
    except Exception:
        HAS_FITZ = False

import pptx
from pptx import Presentation
from pptx.util import Inches, Pt
from pptx.enum.text import PP_ALIGN, MSO_ANCHOR
from pptx.dml.color import RGBColor
from pptx.enum.shapes import MSO_SHAPE


def extract_pdf_backgrounds(pdf_path: Path, output_dir: Path):
    """Render each page of the template PDF as a high-resolution PNG image."""
    output_dir.mkdir(parents=True, exist_ok=True)
    images = []
    if HAS_FITZ:
        doc = fitz.open(str(pdf_path))
        for page_idx in range(len(doc)):
            page = doc[page_idx]
            pix = page.get_pixmap(dpi=200)
            img_path = output_dir / f"slide_bg_{page_idx + 1}.png"
            pix.save(str(img_path))
            images.append(img_path)
        doc.close()
    return images


def build_presentation():
    pdf_source = Path(r"C:\Users\ansh6\.gemini\antigravity\brain\5b2ce08d-36b5-4776-a2bb-2a09ce077d3f\.user_uploaded\media_1788969035253.pdf")
    img_dir = Path(r"C:\Users\ansh6\.gemini\antigravity\scratch\os-debug-agent\slide_backgrounds")
    output_pptx = Path(r"C:\Users\ansh6\.gemini\antigravity\scratch\os-debug-agent\CODEARAMBH_2.0_Presentation.pptx")

    bg_images = []
    if pdf_source.exists():
        try:
            bg_images = extract_pdf_backgrounds(pdf_source, img_dir)
            print(f"[✓] Extracted {len(bg_images)} slide background templates from PDF.")
        except Exception as e:
            print(f"[!] Background extraction failed: {e}")

    prs = Presentation()
    prs.slide_width = Inches(13.333)
    prs.slide_height = Inches(7.5)
    blank_layout = prs.slide_layouts[6]

    # Theme Colors matching CODEARAMBH 2.0
    GOLD = RGBColor(255, 183, 3)        # #FFB703
    ORANGE = RGBColor(251, 133, 0)      # #FB8500
    NEON_CYAN = RGBColor(0, 245, 212)   # #00F5D4
    NEON_GREEN = RGBColor(56, 239, 125) # #38EF7D
    NEON_RED = RGBColor(255, 75, 75)    # #FF4B4B
    WHITE = RGBColor(255, 255, 255)
    LIGHT_GRAY = RGBColor(215, 215, 225)
    DARK_CARD = RGBColor(18, 10, 32)    # Deep translucent purple
    DARK_CARD_ALT = RGBColor(28, 15, 48)
    BORDER_PURPLE = RGBColor(140, 60, 200)
    BORDER_GOLD = RGBColor(255, 183, 3)
    BORDER_ORANGE = RGBColor(251, 133, 0)
    BORDER_CYAN = RGBColor(0, 245, 212)
    BORDER_RED = RGBColor(255, 75, 75)
    BORDER_GREEN = RGBColor(56, 239, 125)

    def set_slide_bg(slide, slide_num: int):
        if bg_images and slide_num <= len(bg_images):
            bg_img = bg_images[slide_num - 1]
            if bg_img.exists():
                slide.shapes.add_picture(str(bg_img), Inches(0), Inches(0), Inches(13.333), Inches(7.5))

    def add_card(slide, left, top, width, height, border_color=BORDER_PURPLE, bg_color=DARK_CARD, shape_type=MSO_SHAPE.ROUNDED_RECTANGLE):
        shape = slide.shapes.add_shape(shape_type, left, top, width, height)
        shape.fill.solid()
        shape.fill.fore_color.rgb = bg_color
        shape.line.color.rgb = border_color
        shape.line.width = Pt(1.5)
        return shape

    # =========================================================================
    # SLIDE 1: TITLE SLIDE (CODEARAMBH 2.0) - Hero Dual-Column Layout
    # =========================================================================
    s1 = prs.slides.add_slide(blank_layout)
    set_slide_bg(s1, 1)

    # Left Column: Project Identity
    c1_left = add_card(s1, Inches(1.0), Inches(1.8), Inches(6.8), Inches(4.8), border_color=BORDER_GOLD)
    tf1_l = c1_left.text_frame
    tf1_l.word_wrap = True

    p = tf1_l.paragraphs[0]
    p.text = "⚡ AUTONOMOUS OS DEBUGGING &\nSELF-HEALING AGENT"
    p.font.size = Pt(22)
    p.font.bold = True
    p.font.color.rgb = GOLD
    p.space_after = Pt(10)

    p = tf1_l.add_paragraph()
    p.text = "An intelligent, closed-loop diagnostic and auto-repair system that detects OS errors, snapshots system states, and heals Windows & Linux machines autonomously."
    p.font.size = Pt(12.5)
    p.font.color.rgb = LIGHT_GRAY
    p.space_after = Pt(14)

    p = tf1_l.add_paragraph()
    r = p.add_run()
    r.text = "🚀 Core Vision: "
    r.font.bold = True
    r.font.color.rgb = ORANGE
    r = p.add_run()
    r.text = "Turn complex 3-hour IT troubleshooting into a 30-second 1-word command ('fix') with 0% risk of bricking."
    r.font.color.rgb = WHITE
    r.font.size = Pt(12)

    # Right Column: Team & Track Meta
    c1_right = add_card(s1, Inches(8.0), Inches(1.8), Inches(4.333), Inches(4.8), border_color=BORDER_CYAN)
    tf1_r = c1_right.text_frame
    tf1_r.word_wrap = True

    p = tf1_r.paragraphs[0]
    p.text = "📋 PROJECT DETAILS"
    p.font.size = Pt(16)
    p.font.bold = True
    p.font.color.rgb = NEON_CYAN
    p.alignment = PP_ALIGN.CENTER
    p.space_after = Pt(12)

    team_meta = [
        ("🏆 Track / Theme", "AI & Autonomous Systems / Systems Reliability"),
        ("👥 Team Name", "KernelHealers"),
        ("👤 Team Leader & Dev", "Ansh Prajapati"),
        ("🏫 College", "Sanjay Ghodawat University (SGU)"),
        ("✉️ Email", "ansh.prajapati@example.com"),
        ("⚡ Emergency Trigger", "1-Word Command: 'fix' in cmd/WinRE")
    ]

    for label, val in team_meta:
        p = tf1_r.add_paragraph()
        r = p.add_run()
        r.text = f"{label}\n"
        r.font.bold = True
        r.font.color.rgb = ORANGE
        r.font.size = Pt(11)
        r2 = p.add_run()
        r2.text = f"{val}\n"
        r2.font.color.rgb = WHITE
        r2.font.size = Pt(11.5)
        p.space_after = Pt(3)

    # =========================================================================
    # SLIDE 2: PROBLEM STATEMENT (1-Line Clear Problem + 3 Threat Pillars)
    # =========================================================================
    s2 = prs.slides.add_slide(blank_layout)
    set_slide_bg(s2, 2)

    # Top Full-Width 1-Line Problem Statement Banner
    c2_top = add_card(s2, Inches(0.8), Inches(1.7), Inches(11.733), Inches(1.15), border_color=BORDER_GOLD, bg_color=DARK_CARD_ALT)
    tf2_top = c2_top.text_frame
    tf2_top.word_wrap = True

    p = tf2_top.paragraphs[0]
    p.text = "🎯 THE CORE PROBLEM (In Plain Words):"
    p.font.size = Pt(12)
    p.font.bold = True
    p.font.color.rgb = ORANGE

    p = tf2_top.add_paragraph()
    p.text = "\"When a computer crashes or shows cryptic error codes like 0x80070005, users and IT teams are stranded with useless built-in tools (SFC/DISM) and dangerous manual scripts that risk bricking the entire operating system.\""
    p.font.size = Pt(13)
    p.font.bold = True
    p.font.color.rgb = WHITE

    # 3 Problem Breakdown Cards
    prob_cards = [
        (
            "🔴 1. Cryptic Error Codes",
            "Symptoms, Not Causes",
            "• Codes like 0x80070005 or BSODs hide what actually failed.\n• Windows Event Viewer is flooded with thousands of unindexed logs.\n• Non-technical users cannot decipher hex memory addresses.",
            BORDER_RED
        ),
        (
            "⚠️ 2. Fragile Native Tools",
            "Static File Replacers",
            "• Built-in SFC & DISM only replace missing static system files.\n• Completely blind to ACL permission locks, DCOM deadlocks, or registry corruption.\n• Often fail silently with generic error messages.",
            BORDER_GOLD
        ),
        (
            "💥 3. High Risk of Bricking",
            "Dangerous Manual Hacks",
            "• Users follow random registry forum hacks without pre-fix backups.\n• High probability of unbootable system states and permanent data loss.\n• Enterprise IT wastes 40%+ of support hours on manual OS triage.",
            BORDER_ORANGE
        )
    ]

    for i, (title, sub, body, border) in enumerate(prob_cards):
        left_pos = 0.8 + (i * 4.0)
        c = add_card(s2, Inches(left_pos), Inches(3.0), Inches(3.733), Inches(3.7), border_color=border)
        tf = c.text_frame
        tf.word_wrap = True

        p = tf.paragraphs[0]
        p.text = title
        p.font.size = Pt(15)
        p.font.bold = True
        p.font.color.rgb = GOLD

        p = tf.add_paragraph()
        p.text = sub
        p.font.size = Pt(11)
        p.font.italic = True
        p.font.color.rgb = NEON_CYAN
        p.space_after = Pt(8)

        p = tf.add_paragraph()
        p.text = body
        p.font.size = Pt(11.5)
        p.font.color.rgb = WHITE

    # =========================================================================
    # SLIDE 3: OUR SOLUTION (Staggered 4-Pillar Feature Layout)
    # =========================================================================
    s3 = prs.slides.add_slide(blank_layout)
    set_slide_bg(s3, 3)

    sol_cards = [
        (
            "🤖 1. Autonomous Self-Healing Pipeline",
            "Closed-Loop OS Doctor",
            "Automatically ingests Event Viewer logs & WMI metrics ➔ Diagnoses root causes with AI ➔ Synthesizes safe read-only probes ➔ Executes verified remediations ➔ Confirms post-fix stability.",
            BORDER_GOLD
        ),
        (
            "🛡️ 2. Atomic Pre-Fix Snapshot & 1-Click Rollback",
            "100% Zero-Bricking Guarantee",
            "Before modifying a single registry key or file ACL, the agent captures an atomic differential snapshot into '.backups/'. Typing 'fix rollback' instantly restores the initial system state.",
            BORDER_GREEN
        ),
        (
            "🔄 3. Dual-Engine Intelligence (Online + 100% Offline)",
            "Resilient Hybrid AI",
            "Uses GPT-4.0 for deep cloud reasoning when online. If network drivers crash or the PC is air-gapped, it automatically falls back to local deterministic heuristic rules or Ollama.",
            BORDER_CYAN
        ),
        (
            "⚡ 4. 1-Word Zero-Friction Shortcut ('fix')",
            "Universal Emergency Access",
            "Pre-installed in C:\\Windows\\fix.bat and WindowsApps. Users simply open Command Prompt or WinRE and type 'fix' or 'fix checkup'—no memorizing URLs or paths.",
            BORDER_ORANGE
        )
    ]

    top_pos = 1.7
    for title, sub, desc, border in sol_cards:
        c = add_card(s3, Inches(0.8), Inches(top_pos), Inches(11.733), Inches(1.15), border_color=border)
        tf = c.text_frame
        tf.word_wrap = True

        p = tf.paragraphs[0]
        r1 = p.add_run()
        r1.text = f"{title}  "
        r1.font.bold = True
        r1.font.size = Pt(14)
        r1.font.color.rgb = GOLD

        r2 = p.add_run()
        r2.text = f"[{sub}]"
        r2.font.bold = True
        r2.font.size = Pt(11)
        r2.font.color.rgb = NEON_CYAN
        p.space_after = Pt(2)

        p = tf.add_paragraph()
        p.text = desc
        p.font.size = Pt(11.5)
        p.font.color.rgb = WHITE
        top_pos += 1.25

    # =========================================================================
    # SLIDE 4: TECH STACK AND FLOW (Visual Step-by-Step Flowchart + Matrix)
    # =========================================================================
    s4 = prs.slides.add_slide(blank_layout)
    set_slide_bg(s4, 4)

    # Top Half: 5 Step-by-Step Visual Flowchart Nodes connected with Arrows
    flow_steps = [
        ("Step 1: Ingest", "Event Logs, WMI, ACLs, Services", BORDER_CYAN),
        ("Step 2: Reason", "GPT-4.0 / Local Heuristic Rules", BORDER_GOLD),
        ("Step 3: Snapshot", "Atomic Registry & ACL Differential", BORDER_GREEN),
        ("Step 4: Heal", "Guarded Script Execution (300s)", BORDER_ORANGE),
        ("Step 5: Verify", "Post-Boot RunOnce & Web3 Anchor", BORDER_PURPLE),
    ]

    for i, (stitle, sdesc, sborder) in enumerate(flow_steps):
        left_pos = 0.8 + (i * 2.4)
        c = add_card(s4, Inches(left_pos), Inches(1.7), Inches(2.1), Inches(1.85), border_color=sborder, bg_color=DARK_CARD_ALT)
        tf = c.text_frame
        tf.word_wrap = True
        p = tf.paragraphs[0]
        p.text = stitle
        p.font.size = Pt(13)
        p.font.bold = True
        p.font.color.rgb = GOLD
        p.alignment = PP_ALIGN.CENTER
        p.space_after = Pt(4)

        p = tf.add_paragraph()
        p.text = sdesc
        p.font.size = Pt(10.5)
        p.font.color.rgb = WHITE
        p.alignment = PP_ALIGN.CENTER

        # Add Connector Arrow between steps
        if i < len(flow_steps) - 1:
            arrow = s4.shapes.add_shape(MSO_SHAPE.RIGHT_ARROW, Inches(left_pos + 2.12), Inches(2.4), Inches(0.24), Inches(0.35))
            arrow.fill.solid()
            arrow.fill.fore_color.rgb = GOLD
            arrow.line.color.rgb = GOLD

    # Bottom Half: 4-Pillar Tech Matrix
    tech_matrix = [
        ("⚙️ Core Systems", "Python 3.12, Typer CLI, Rich UI, Win32 API, WMI, PowerShell 5.1/7, systemd", BORDER_CYAN),
        ("🧠 AI Reasoning", "OpenAI GPT-4.0 (Cloud API) + Ollama (Llama-3, Mistral) & Offline Heuristics", BORDER_GOLD),
        ("🛡️ Safety & Sandbox", "Pre-Fix Differential Snapshots, Command Blacklists, 300s Execution Guard", BORDER_GREEN),
        ("🔗 Web3 & Auditing", "Algorand TestNet Blockchain (py-algorand-sdk), AlgoKit Lora SHA-256 Ledger", BORDER_ORANGE),
    ]

    for i, (cat, stack, border) in enumerate(tech_matrix):
        row = i // 2
        col = i % 2
        left_pos = 0.8 + (col * 5.95)
        top_pos = 3.8 + (row * 1.5)
        c = add_card(s4, Inches(left_pos), Inches(top_pos), Inches(5.78), Inches(1.35), border_color=border)
        tf = c.text_frame
        tf.word_wrap = True

        p = tf.paragraphs[0]
        p.text = cat
        p.font.size = Pt(13)
        p.font.bold = True
        p.font.color.rgb = GOLD
        p.space_after = Pt(2)

        p = tf.add_paragraph()
        p.text = stack
        p.font.size = Pt(11)
        p.font.color.rgb = WHITE

    # =========================================================================
    # SLIDE 5: OUR USP (2x2 Quadrant Grid Matrix with Number Badges)
    # =========================================================================
    s5 = prs.slides.add_slide(blank_layout)
    set_slide_bg(s5, 5)

    usps = [
        (
            "#1",
            "⚡ 1-Word Emergency Shortcut ('fix')",
            "Pre-installed permanent shortcut in C:\\Windows\\fix.bat and %LOCALAPPDATA%\\Microsoft\\WindowsApps. When a crash occurs, users type 'fix' without memorizing commands or URLs.",
            BORDER_GOLD
        ),
        (
            "#2",
            "📶 True 100% Offline Resilience",
            "Network drivers often crash during OS failures. Unlike cloud-only tools, our built-in heuristic engine and local Ollama support resolve critical errors completely offline.",
            BORDER_CYAN
        ),
        (
            "#3",
            "🛡️ Zero-Bricking Rollback Guarantee",
            "Every single registry tweak, service restart, and file ACL modification is pre-snapshotted. One command ('fix rollback') restores the exact initial machine state.",
            BORDER_GREEN
        ),
        (
            "#4",
            "🔗 Cryptographic Proof of Repair (Web3)",
            "Generates immutable SHA-256 state hashes of every repair and anchors them onto the Algorand blockchain for tamper-proof enterprise change-management compliance.",
            BORDER_ORANGE
        )
    ]

    for i, (badge, title, desc, border) in enumerate(usps):
        row = i // 2
        col = i % 2
        left_pos = 0.8 + (col * 5.95)
        top_pos = 1.7 + (row * 2.55)
        c = add_card(s5, Inches(left_pos), Inches(top_pos), Inches(5.78), Inches(2.35), border_color=border)
        tf = c.text_frame
        tf.word_wrap = True

        p = tf.paragraphs[0]
        r1 = p.add_run()
        r1.text = f"[{badge}] "
        r1.font.bold = True
        r1.font.size = Pt(15)
        r1.font.color.rgb = ORANGE

        r2 = p.add_run()
        r2.text = title
        r2.font.bold = True
        r2.font.size = Pt(14)
        r2.font.color.rgb = GOLD
        p.space_after = Pt(6)

        p = tf.add_paragraph()
        p.text = desc
        p.font.size = Pt(11.5)
        p.font.color.rgb = WHITE

    # =========================================================================
    # SLIDE 6: FEASIBILITY AND VIABILITY (3-Pillar Architectural Cards)
    # =========================================================================
    s6 = prs.slides.add_slide(blank_layout)
    set_slide_bg(s6, 6)

    viability_pillars = [
        (
            "🪶 Ultra-Lightweight & Non-Intrusive",
            "Status: 100% User-Space",
            "• Total package footprint < 15MB with standalone portable Python support.\n• Zero permanent background daemons draining CPU, RAM, or battery.\n• Runs entirely in user-space using standard Win32 / POSIX APIs without kernel bloat.",
            BORDER_CYAN
        ),
        (
            "💻 Cross-Platform & Kernel Safe",
            "Status: Zero BSOD Risk",
            "• Unified codebase supporting Windows 10/11 and Linux distributions.\n• Zero third-party kernel driver installation—completely eliminates driver crash risks.\n• Full compatibility with standard Python, uv package manager, and WindowsApps.",
            BORDER_GOLD
        ),
        (
            "🏢 Enterprise Fleet Scalable",
            "Status: Enterprise Ready",
            "• Readily deployable via Microsoft Intune, SCCM, Group Policy, or 1-line script.\n• Built-in multi-instance lock manager prevents concurrent script conflicts.\n• Ready for enterprise IT fleets, cloud virtual machines, and consumer PCs.",
            BORDER_GREEN
        )
    ]

    for i, (title, tag, desc, border) in enumerate(viability_pillars):
        left_pos = 0.8 + (i * 4.0)
        c = add_card(s6, Inches(left_pos), Inches(1.7), Inches(3.733), Inches(5.0), border_color=border)
        tf = c.text_frame
        tf.word_wrap = True

        p = tf.paragraphs[0]
        p.text = title
        p.font.size = Pt(15)
        p.font.bold = True
        p.font.color.rgb = GOLD

        p = tf.add_paragraph()
        p.text = tag
        p.font.size = Pt(11)
        p.font.bold = True
        p.font.color.rgb = NEON_GREEN
        p.space_after = Pt(10)

        p = tf.add_paragraph()
        p.text = desc
        p.font.size = Pt(12)
        p.font.color.rgb = WHITE

    # =========================================================================
    # SLIDE 7: IMPACT AND BENEFITS (Big Stat Numbers + Impact Cards)
    # =========================================================================
    s7 = prs.slides.add_slide(blank_layout)
    set_slide_bg(s7, 7)

    # Top Row: 4 Big Stat Metric Callouts
    stats = [
        ("90%", "MTTR Reduction", BORDER_GOLD),
        ("<30s", "Avg Healing Time", BORDER_CYAN),
        ("0%", "Bricking Risk (Rollback)", BORDER_GREEN),
        ("1-Word", "Emergency Trigger ('fix')", BORDER_ORANGE)
    ]

    for i, (num, label, border) in enumerate(stats):
        left_pos = 0.8 + (i * 3.0)
        c = add_card(s7, Inches(left_pos), Inches(1.7), Inches(2.733), Inches(1.5), border_color=border, bg_color=DARK_CARD_ALT)
        tf = c.text_frame
        tf.word_wrap = True
        p = tf.paragraphs[0]
        p.text = num
        p.font.size = Pt(26)
        p.font.bold = True
        p.font.color.rgb = GOLD
        p.alignment = PP_ALIGN.CENTER

        p = tf.add_paragraph()
        p.text = label
        p.font.size = Pt(11)
        p.font.bold = True
        p.font.color.rgb = WHITE
        p.alignment = PP_ALIGN.CENTER

    # Bottom Row: 2 High-Impact Comparison Panels
    impact_panels = [
        (
            "🏢 Enterprise & IT Helpdesk Value",
            "• Eliminates 40%+ of repetitive Tier 1 & 2 support tickets.\n• Saves enterprise IT teams thousands of hours of manual troubleshooting.\n• Guarantees compliance and immutable change-management auditing via Algorand blockchain.",
            BORDER_CYAN
        ),
        (
            "👥 Consumer & Non-Technical User Safety",
            "• Turns cryptic BSODs and error codes into simple, plain English diagnostics.\n• Anyone can type 'fix' or select a number [1-14] in the interactive menu without technical training.\n• Atomic pre-fix snapshots guarantee complete peace of mind with 1-click rollback.",
            BORDER_GREEN
        )
    ]

    for i, (title, desc, border) in enumerate(impact_panels):
        left_pos = 0.8 + (i * 5.95)
        c = add_card(s7, Inches(left_pos), Inches(3.45), Inches(5.78), Inches(3.25), border_color=border)
        tf = c.text_frame
        tf.word_wrap = True

        p = tf.paragraphs[0]
        p.text = title
        p.font.size = Pt(15)
        p.font.bold = True
        p.font.color.rgb = GOLD
        p.space_after = Pt(8)

        p = tf.add_paragraph()
        p.text = desc
        p.font.size = Pt(12)
        p.font.color.rgb = WHITE

    # =========================================================================
    # SLIDE 8: RESEARCH AND REFERENCE (4 Academic Research Citation Cards)
    # =========================================================================
    s8 = prs.slides.add_slide(blank_layout)
    set_slide_bg(s8, 8)

    refs = [
        (
            "📖 1. Microsoft Windows Internals & Servicing Architecture",
            "• Deep analysis of Component-Based Servicing (CBS), TrustedInstaller permissions, and DCOM RPC security.\n• Reference: Windows Internals (Part 1 & 2) by Pavel Yosifovich, Mark Russinovich, David Solomon.",
            BORDER_GOLD
        ),
        (
            "🔬 2. Autonomous Systems & Heuristic Failure Recovery",
            "• Research on closed-loop self-adaptive software systems, bounded-safety execution sandboxes, and root cause isolation.\n• Reference: IEEE Transactions on Software Engineering & ACM Computing Surveys on Self-Healing Systems.",
            BORDER_CYAN
        ),
        (
            "🔗 3. Algorand Pure Proof-of-Stake (PPoS) & Immutable Auditing",
            "• Decentralized cryptographic audit trails for operating system compliance, change management, and DevOps integrity.\n• Reference: Algorand Consensus Protocol by Silvio Micali; AlgoKit Lora TestNet Documentation.",
            BORDER_GREEN
        ),
        (
            "🛡️ 4. NIST Special Publication 800-53 (Rev. 5)",
            "• Security and Privacy Controls for Information Systems — System and Information Integrity (SI-2 Flaw Remediation & SI-7 Integrity Monitoring).",
            BORDER_ORANGE
        )
    ]

    top_pos = 1.7
    for title, desc, border in refs:
        c = add_card(s8, Inches(0.8), Inches(top_pos), Inches(11.733), Inches(1.18), border_color=border)
        tf = c.text_frame
        tf.word_wrap = True

        p = tf.paragraphs[0]
        p.text = title
        p.font.size = Pt(14)
        p.font.bold = True
        p.font.color.rgb = GOLD
        p.space_after = Pt(2)

        p = tf.add_paragraph()
        p.text = desc
        p.font.size = Pt(11)
        p.font.color.rgb = WHITE
        top_pos += 1.28

    # =========================================================================
    # SLIDE 9: OUR LINKS (Terminal Window Mockup Card)
    # =========================================================================
    s9 = prs.slides.add_slide(blank_layout)
    set_slide_bg(s9, 9)

    # Main Terminal Box
    c9 = add_card(s9, Inches(1.0), Inches(1.7), Inches(11.333), Inches(5.0), border_color=BORDER_GOLD, bg_color=DARK_CARD_ALT)
    tf9 = c9.text_frame
    tf9.word_wrap = True

    p = tf9.paragraphs[0]
    p.text = "🔴 🟡 🟢  TERMINAL RECOVERY & PROJECT LINKS"
    p.font.size = Pt(15)
    p.font.bold = True
    p.font.color.rgb = GOLD
    p.space_after = Pt(10)

    terminal_links = [
        ("📦 GitHub Source Code Repository:", "https://github.com/Ansh00031/Build-In-Bharat_NIT-Delhi"),
        ("⚡ 1-Line Cloud Bootstrapper (PowerShell):", "irm https://raw.githubusercontent.com/Ansh00031/Build-In-Bharat_NIT-Delhi/main/bootstrap.ps1 | iex"),
        ("💻 1-Line Cloud Bootstrapper (CMD):", "powershell -ep bypass -c \"irm https://raw.githubusercontent.com/Ansh00031/Build-In-Bharat_NIT-Delhi/main/bootstrap.ps1 | iex\""),
        ("🚀 Local Emergency Fix Trigger:", "fix  (or 'fix checkup' / 'fix 0x80070005')"),
        ("📜 Interactive Command Menu:", "python agent.py menu  (Options [1] to [14])"),
        ("🟣 Algorand Blockchain Explorer:", "https://lora.algokit.io/testnet/account/...")
    ]

    for label, cmd_text in terminal_links:
        p = tf9.add_paragraph()
        r1 = p.add_run()
        r1.text = f"{label}\n"
        r1.font.bold = True
        r1.font.color.rgb = ORANGE
        r1.font.size = Pt(12)

        r2 = p.add_run()
        r2.text = f"  $ {cmd_text}\n"
        r2.font.color.rgb = NEON_CYAN
        r2.font.size = Pt(11.5)
        p.space_after = Pt(3)

    # Graceful save handling (in case PowerPoint has the file currently open)
    try:
        prs.save(str(output_pptx))
        print(f"\n[✓] Presentation successfully built and saved to:\n    {output_pptx}")
        return output_pptx
    except PermissionError:
        alt_pptx = output_pptx.parent / "CODEARAMBH_2.0_Presentation_New.pptx"
        try:
            prs.save(str(alt_pptx))
            print(f"\n[!] Notice: 'CODEARAMBH_2.0_Presentation.pptx' is currently open in PowerPoint.")
            print(f"[✓] Saved updated presentation with all new layouts to:\n    {alt_pptx}")
            return alt_pptx
        except Exception as ex:
            import time
            ts_pptx = output_pptx.parent / f"CODEARAMBH_2.0_Presentation_{int(time.time())}.pptx"
            prs.save(str(ts_pptx))
            print(f"[✓] Saved to:\n    {ts_pptx}")
            return ts_pptx


if __name__ == "__main__":
    build_presentation()
