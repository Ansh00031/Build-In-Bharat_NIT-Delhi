"""Junk file and duplicate file scanner & cleaner with explicit user permission."""

import hashlib
import os
import platform
import shutil
from pathlib import Path
from typing import Any, Dict, List, Optional, Tuple


def format_size(size_bytes: int) -> str:
    """Format bytes to human readable string (KB, MB, GB)."""
    if size_bytes < 1024:
        return f"{size_bytes} B"
    elif size_bytes < 1024 * 1024:
        return f"{size_bytes / 1024:.2f} KB"
    elif size_bytes < 1024 * 1024 * 1024:
        return f"{size_bytes / (1024 * 1024):.2f} MB"
    else:
        return f"{size_bytes / (1024 * 1024 * 1024):.2f} GB"


def get_file_hash(file_path: Path, block_size: int = 65536) -> Optional[str]:
    """Calculate SHA-256 hash of a file for exact duplicate verification."""
    try:
        hasher = hashlib.sha256()
        with open(file_path, "rb") as f:
            for block in iter(lambda: f.read(block_size), b""):
                hasher.update(block)
        return hasher.hexdigest()
    except (PermissionError, OSError, FileNotFoundError):
        return None


def get_junk_scan_locations() -> List[Dict[str, Any]]:
    """Return standard OS junk, cache, and temporary log directories."""
    locations = []
    is_win = platform.system() == "Windows"

    if is_win:
        user_temp = os.environ.get("TEMP") or os.environ.get("TMP")
        if user_temp and Path(user_temp).exists():
            locations.append({"category": "User Temp Files", "path": Path(user_temp), "recursive": True})

        sys_temp = Path(r"C:\Windows\Temp")
        if sys_temp.exists():
            locations.append({"category": "Windows System Temp", "path": sys_temp, "recursive": True})

        prefetch = Path(r"C:\Windows\Prefetch")
        if prefetch.exists():
            locations.append({"category": "Windows Prefetch Cache", "path": prefetch, "recursive": False})

        crash_dumps = Path(os.environ.get("LOCALAPPDATA", "")) / "CrashDumps"
        if crash_dumps.exists():
            locations.append({"category": "Application Crash Dumps", "path": crash_dumps, "recursive": True})

        sw_dist = Path(r"C:\Windows\SoftwareDistribution\Download")
        if sw_dist.exists():
            locations.append({"category": "Windows Update Download Cache", "path": sw_dist, "recursive": True})

        log_dir = Path(os.environ.get("LOCALAPPDATA", "")) / "Temp"
        if log_dir.exists() and log_dir != Path(user_temp or ""):
            locations.append({"category": "Local App Logs", "path": log_dir, "recursive": True})
    else:
        locations.append({"category": "System /tmp Files", "path": Path("/tmp"), "recursive": True})
        locations.append({"category": "User Cache (~/.cache)", "path": Path.home() / ".cache", "recursive": True})
        locations.append({"category": "System Crash Reports", "path": Path("/var/crash"), "recursive": True})

    return locations


def scan_junk_files(max_items_per_category: int = 150) -> Dict[str, Any]:
    """Scan the system for junk files, temp caches, and crash dumps.

    Returns:
        Dict containing categories, file lists with paths and sizes, and total reclaimable bytes.
    """
    junk_categories: List[Dict[str, Any]] = []
    total_junk_bytes = 0
    total_junk_count = 0

    locations = get_junk_scan_locations()
    for loc in locations:
        cat_name = loc["category"]
        folder_path = loc["path"]
        recursive = loc["recursive"]
        files_found = []
        cat_bytes = 0

        try:
            iterator = folder_path.rglob("*") if recursive else folder_path.glob("*")
            for p in iterator:
                if p.is_file():
                    try:
                        sz = p.stat().st_size
                        cat_bytes += sz
                        total_junk_bytes += sz
                        total_junk_count += 1
                        if len(files_found) < max_items_per_category:
                            files_found.append({
                                "path": str(p),
                                "size_bytes": sz,
                                "size_formatted": format_size(sz),
                            })
                    except (PermissionError, OSError):
                        continue
        except (PermissionError, OSError):
            continue

        if files_found or cat_bytes > 0:
            junk_categories.append({
                "category": cat_name,
                "folder": str(folder_path),
                "file_count": len(files_found),
                "total_bytes": cat_bytes,
                "total_formatted": format_size(cat_bytes),
                "files": files_found,
            })

    return {
        "categories": junk_categories,
        "total_files": total_junk_count,
        "total_bytes": total_junk_bytes,
        "total_formatted": format_size(total_junk_bytes),
    }


def delete_junk_files(junk_data: Dict[str, Any], confirmed: bool = False) -> Tuple[int, int, List[str]]:
    """Delete scanned junk files only if user confirmation is explicitly granted.

    Returns:
        Tuple[int, int, List[str]]: (deleted_count, reclaimed_bytes, errors)
    """
    if not confirmed:
        return 0, 0, ["Action canceled: User permission was not granted."]

    deleted_count = 0
    reclaimed_bytes = 0
    errors = []

    for cat in junk_data.get("categories", []):
        for f_info in cat.get("files", []):
            f_path = Path(f_info["path"])
            try:
                if f_path.exists() and f_path.is_file():
                    sz = f_info.get("size_bytes", 0)
                    f_path.unlink()
                    deleted_count += 1
                    reclaimed_bytes += sz
            except Exception as ex:
                errors.append(f"Failed to delete {f_path.name}: {str(ex)}")

    return deleted_count, reclaimed_bytes, errors


def get_user_scan_directories() -> List[Path]:
    """Return standard user data directories where duplicates commonly accumulate."""
    home = Path.home()
    dirs = [
        home / "Downloads",
        home / "Documents",
        home / "Desktop",
    ]
    return [d for d in dirs if d.exists()]


def scan_duplicate_files(target_dirs: Optional[List[Path]] = None, min_size_bytes: int = 1024) -> Dict[str, Any]:
    """Scan user folders for duplicate files using size grouping followed by SHA-256 hash matching.

    Returns:
        Dict containing duplicate groups with file paths, sizes, and potential space savings.
    """
    if not target_dirs:
        target_dirs = get_user_scan_directories()

    # Step 1: Group files by file size
    size_map: Dict[int, List[Path]] = {}
    for folder in target_dirs:
        try:
            for p in folder.rglob("*"):
                if p.is_file() and not p.is_symlink():
                    try:
                        sz = p.stat().st_size
                        if sz >= min_size_bytes:
                            size_map.setdefault(sz, []).append(p)
                    except (PermissionError, OSError):
                        continue
        except (PermissionError, OSError):
            continue

    # Step 2: Hash files that share the exact same size
    duplicate_groups: List[Dict[str, Any]] = []
    total_wasted_bytes = 0
    total_duplicate_copies = 0

    for sz, paths in size_map.items():
        if len(paths) < 2:
            continue

        hash_map: Dict[str, List[Path]] = {}
        for p in paths:
            h = get_file_hash(p)
            if h:
                hash_map.setdefault(h, []).append(p)

        for f_hash, dup_paths in hash_map.items():
            if len(dup_paths) >= 2:
                # Sort by modification time (oldest is considered original)
                sorted_paths = sorted(dup_paths, key=lambda x: x.stat().st_mtime if x.exists() else 0)
                original = sorted_paths[0]
                copies = sorted_paths[1:]

                wasted_for_group = sz * len(copies)
                total_wasted_bytes += wasted_for_group
                total_duplicate_copies += len(copies)

                duplicate_groups.append({
                    "hash": f_hash[:12],
                    "file_size": sz,
                    "file_size_formatted": format_size(sz),
                    "wasted_bytes": wasted_for_group,
                    "wasted_formatted": format_size(wasted_for_group),
                    "original": {
                        "path": str(original),
                        "modified_at": original.stat().st_mtime if original.exists() else 0,
                    },
                    "copies": [
                        {
                            "path": str(c),
                            "modified_at": c.stat().st_mtime if c.exists() else 0,
                        }
                        for c in copies
                    ],
                })

    return {
        "groups": duplicate_groups,
        "total_groups": len(duplicate_groups),
        "total_duplicate_copies": total_duplicate_copies,
        "total_wasted_bytes": total_wasted_bytes,
        "total_wasted_formatted": format_size(total_wasted_bytes),
    }


def delete_duplicate_copies(duplicate_data: Dict[str, Any], keep_original: bool = True, confirmed: bool = False) -> Tuple[int, int, List[str]]:
    """Delete redundant duplicate copies (preserving the original) upon explicit user permission.

    Returns:
        Tuple[int, int, List[str]]: (deleted_count, reclaimed_bytes, errors)
    """
    if not confirmed:
        return 0, 0, ["Action canceled: User permission was not granted."]

    deleted_count = 0
    reclaimed_bytes = 0
    errors = []

    for group in duplicate_data.get("groups", []):
        sz = group.get("file_size", 0)
        for copy_info in group.get("copies", []):
            c_path = Path(copy_info["path"])
            try:
                if c_path.exists() and c_path.is_file():
                    c_path.unlink()
                    deleted_count += 1
                    reclaimed_bytes += sz
            except Exception as ex:
                errors.append(f"Failed to remove duplicate {c_path.name}: {str(ex)}")

    return deleted_count, reclaimed_bytes, errors
