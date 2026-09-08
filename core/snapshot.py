"""System state snapshot, session tracking, and rollback engine."""

import datetime
import json
import os
import shutil
from pathlib import Path
from typing import Any, Dict, List, Optional

from core.system_paths import find_powershell_executable, get_system_env

BACKUPS_DIR = Path(__file__).resolve().parent.parent / ".backups"


def get_backups_dir() -> Path:
    """Ensure and return the backups directory path."""
    BACKUPS_DIR.mkdir(parents=True, exist_ok=True)
    return BACKUPS_DIR


def generate_session_id(error_code: str) -> str:
    """Generate a unique timestamped session identifier."""
    clean_code = error_code.replace("0x", "").replace(":", "_").replace(" ", "_")
    timestamp = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
    return f"session_{timestamp}_{clean_code}"


def create_pre_fix_snapshot(
    session_id: str,
    error_code: str,
    proposal: Dict[str, Any],
    rollback_script: str,
    system_context: Dict[str, Any],
) -> Path:
    """Capture pre-fix system configuration, backup scripts, and metadata.

    Args:
        session_id: Unique session ID.
        error_code: Target error code.
        proposal: The approved remediation proposal.
        rollback_script: The inverse PowerShell script to undo the fix.
        system_context: Gathered OS metadata and diagnostics.

    Returns:
        Path: Path to the created session backup directory.
    """
    session_dir = get_backups_dir() / session_id
    session_dir.mkdir(parents=True, exist_ok=True)

    # 1. Save fix script
    fix_path = session_dir / "fix.ps1"
    fix_path.write_text(proposal.get("script_content", ""), encoding="utf-8")

    # 2. Save rollback script
    rollback_path = session_dir / "rollback.ps1"
    rollback_path.write_text(rollback_script, encoding="utf-8")

    # 3. Save comprehensive session metadata
    metadata = {
        "session_id": session_id,
        "error_code": error_code,
        "created_at": datetime.datetime.now().isoformat(),
        "fix_title": proposal.get("title", "Remediation Fix"),
        "fix_summary": proposal.get("summary", ""),
        "threat_level": proposal.get("threat_level", "HIGH"),
        "verification_command": proposal.get("verification_command", ""),
        "os_info": system_context.get("os_info", {}),
        "status": "APPLIED",
        "rollback_executed": False,
    }

    meta_path = session_dir / "metadata.json"
    meta_path.write_text(json.dumps(metadata, indent=2), encoding="utf-8")

    return session_dir


def update_session_status(session_id: str, status: str, rollback_executed: bool = False) -> None:
    """Update execution status in session metadata."""
    session_dir = get_backups_dir() / session_id
    meta_path = session_dir / "metadata.json"
    if meta_path.exists():
        try:
            data = json.loads(meta_path.read_text(encoding="utf-8"))
            data["status"] = status
            if rollback_executed:
                data["rollback_executed"] = True
                data["rolled_back_at"] = datetime.datetime.now().isoformat()
            meta_path.write_text(json.dumps(data, indent=2), encoding="utf-8")
        except Exception:
            pass


def list_sessions() -> List[Dict[str, Any]]:
    """Retrieve all historical remediation sessions ordered from newest to oldest."""
    backups_dir = get_backups_dir()
    sessions = []

    for item in backups_dir.iterdir():
        if item.is_dir():
            meta_file = item / "metadata.json"
            if meta_file.exists():
                try:
                    meta = json.loads(meta_file.read_text(encoding="utf-8"))
                    sessions.append(meta)
                except Exception:
                    continue

    # Sort newest first
    sessions.sort(key=lambda s: s.get("created_at", ""), reverse=True)
    return sessions


def get_resolved_issues_file() -> Path:
    """Return path to the separate resolved issues JSON file."""
    return get_backups_dir() / "resolved_issues.json"


def get_resolved_log_file() -> Path:
    """Return path to the persistent resolved history text log."""
    return get_backups_dir() / "resolved_history.log"


def save_resolved_issue(session_data: Dict[str, Any]) -> None:
    """Save a solved/resolved problem into the dedicated resolved issues archive."""
    resolved_file = get_resolved_issues_file()
    resolved_log = get_resolved_log_file()
    
    issues: List[Dict[str, Any]] = []
    if resolved_file.exists():
        try:
            issues = json.loads(resolved_file.read_text(encoding="utf-8"))
        except Exception:
            issues = []

    # Check if already present by session_id
    session_id = session_data.get("session_id", "")
    existing_idx = next((i for i, item in enumerate(issues) if item.get("session_id") == session_id), None)

    entry = {
        "session_id": session_id,
        "error_code": session_data.get("error_code", "RESOLVED_ERROR"),
        "fix_title": session_data.get("fix_title") or session_data.get("title", "Service Remediation"),
        "summary": session_data.get("summary") or session_data.get("fix_summary", ""),
        "verification_command": session_data.get("verification_command", ""),
        "status": session_data.get("status", "SOLVED"),
        "resolved_at": datetime.datetime.now().isoformat(),
        "blockchain_tx_id": session_data.get("blockchain_tx_id"),
        "blockchain_lora_url": session_data.get("blockchain_lora_url"),
    }

    if existing_idx is not None:
        issues[existing_idx] = entry
    else:
        issues.insert(0, entry)

    # Save to dedicated JSON file
    try:
        resolved_file.write_text(json.dumps(issues, indent=2), encoding="utf-8")
    except Exception:
        pass

    # Append to human-readable log
    try:
        log_line = f"[{entry['resolved_at']}] SOLVED: {entry['error_code']} - {entry['fix_title']} (Session: {entry['session_id']})\n"
        with open(resolved_log, "a", encoding="utf-8") as f:
            f.write(log_line)
    except Exception:
        pass


def load_resolved_issues() -> List[Dict[str, Any]]:
    """Load all saved resolved and solved problems from the dedicated separate file."""
    resolved_file = get_resolved_issues_file()
    if resolved_file.exists():
        try:
            return json.loads(resolved_file.read_text(encoding="utf-8"))
        except Exception:
            pass

    # Fallback: scan existing sessions in .backups/ to populate if file was deleted
    sessions = list_sessions()
    resolved = []
    for s in sessions:
        st = str(s.get("status", "")).upper()
        if any(k in st for k in ["COMPLETED", "SUCCESS", "VERIFIED"]) and not s.get("rollback_executed", False):
            resolved.append(s)
            save_resolved_issue(s)
    return resolved


def get_session(session_id: str) -> Optional[Dict[str, Any]]:
    """Get metadata and file paths for a specific session."""
    session_dir = get_backups_dir() / session_id
    meta_file = session_dir / "metadata.json"
    if not meta_file.exists():
        return None

    try:
        data = json.loads(meta_file.read_text(encoding="utf-8"))
        data["dir_path"] = str(session_dir)
        data["rollback_script_path"] = str(session_dir / "rollback.ps1")
        data["fix_script_path"] = str(session_dir / "fix.ps1")
        return data
    except Exception:
        return None
