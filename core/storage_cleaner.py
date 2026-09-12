"""Junk file and duplicate file scanner & cleaner with explicit user permission."""

import hashlib
import os
import platform
import stat
import string
from pathlib import Path
from typing import Any, Dict, List, Optional, Set, Tuple


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


def get_partial_file_hash(file_path: Path, sample_size: int = 32768) -> Optional[str]:
    """Fast partial hash of header + footer for quick duplicate filtering on large files."""
    try:
        sz = file_path.stat().st_size
        if sz <= sample_size * 2:
            return get_file_hash(file_path)
        hasher = hashlib.sha256()
        with open(file_path, "rb") as f:
            hasher.update(f.read(sample_size))
            f.seek(max(0, sz - sample_size))
            hasher.update(f.read(sample_size))
        return hasher.hexdigest()
    except (PermissionError, OSError, FileNotFoundError):
        return None


def get_all_system_drives() -> List[Path]:
    """Discover all available drives and storage volumes across the entire PC."""
    drives = []
    if platform.system() == "Windows":
        for letter in string.ascii_uppercase:
            drive_path = Path(f"{letter}:\\")
            try:
                if drive_path.exists():
                    drives.append(drive_path)
            except (PermissionError, OSError):
                continue
    else:
        drives.append(Path("/"))
        for mount in [Path("/media"), Path("/mnt"), Path("/Volumes")]:
            if mount.exists():
                try:
                    for sub in mount.iterdir():
                        if sub.is_dir():
                            drives.append(sub)
                except (PermissionError, OSError):
                    continue
    return drives


def get_system_wide_duplicate_scan_directories() -> List[Path]:
    """Return comprehensive list of user data folders and storage volumes across the entire PC."""
    scan_dirs: List[Path] = []
    seen: Set[str] = set()

    def _add_dir(d: Path):
        try:
            res = str(d.resolve())
            if d.exists() and d.is_dir() and res not in seen:
                scan_dirs.append(d)
                seen.add(res)
        except (PermissionError, OSError):
            pass

    home = Path.home()
    # 1. Standard user directories
    user_folders = [
        "Downloads",
        "Documents",
        "Desktop",
        "Pictures",
        "Music",
        "Videos",
        "OneDrive",
        "Projects",
        "workspace",
        "Workspace",
    ]
    for sub in user_folders:
        _add_dir(home / sub)

    # 2. Add full user home directory
    _add_dir(home)

    # 3. Add root of all secondary drives (D:\, E:\, F:\, etc.)
    all_drives = get_all_system_drives()
    for drive in all_drives:
        # Avoid scanning entire C:\ root to protect Windows system binaries, but scan all secondary drives
        if str(drive).upper().startswith("C:") and len(str(drive)) <= 3:
            # For C:\, scan all user profiles in C:\Users
            users_dir = Path("C:\\Users")
            if users_dir.exists():
                try:
                    for u in users_dir.iterdir():
                        if u.is_dir() and u.name.lower() not in ["all users", "default", "default user", "public"]:
                            _add_dir(u)
                except (PermissionError, OSError):
                    pass
        else:
            _add_dir(drive)

    return scan_dirs


def get_junk_scan_locations() -> List[Dict[str, Any]]:
    """Return live dynamic OS junk, cache, error report, and temporary log directories."""
    locations = []
    is_win = platform.system() == "Windows"

    if is_win:
        user_temp = os.environ.get("TEMP") or os.environ.get("TMP")
        if user_temp and Path(user_temp).exists():
            locations.append({"category": "User Temp Caches & Files", "path": Path(user_temp), "recursive": True})

        sys_temp = Path(r"C:\Windows\Temp")
        if sys_temp.exists():
            locations.append({"category": "Windows System Temp Logs", "path": sys_temp, "recursive": True})

        prefetch = Path(r"C:\Windows\Prefetch")
        if prefetch.exists():
            locations.append({"category": "Windows Prefetch Cache", "path": prefetch, "recursive": False})

        crash_dumps = Path(os.environ.get("LOCALAPPDATA", "")) / "CrashDumps"
        if crash_dumps.exists():
            locations.append({"category": "Application Crash Dumps", "path": crash_dumps, "recursive": True})

        sw_dist = Path(r"C:\Windows\SoftwareDistribution\Download")
        if sw_dist.exists():
            locations.append({"category": "Windows Update Download Cache", "path": sw_dist, "recursive": True})

        wer_dir = Path(os.environ.get("LOCALAPPDATA", "")) / "Microsoft" / "Windows" / "WER"
        if wer_dir.exists():
            locations.append({"category": "Windows Error Reports (WER)", "path": wer_dir, "recursive": True})

        pip_cache = Path(os.environ.get("LOCALAPPDATA", "")) / "pip" / "cache"
        if pip_cache.exists():
            locations.append({"category": "Python Pip Package Cache", "path": pip_cache, "recursive": True})

        npm_cache = Path(os.environ.get("APPDATA", "")) / "npm-cache"
        if npm_cache.exists():
            locations.append({"category": "Node NPM Package Cache", "path": npm_cache, "recursive": True})
    else:
        locations.append({"category": "System /tmp Files", "path": Path("/tmp"), "recursive": True})
        locations.append({"category": "User Cache (~/.cache)", "path": Path.home() / ".cache", "recursive": True})
        locations.append({"category": "System Crash Reports", "path": Path("/var/crash"), "recursive": True})

    return locations


def scan_junk_files() -> Dict[str, Any]:
    """Scan the system dynamically for live junk files, temp caches, and crash dumps."""
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
                try:
                    if p.is_file():
                        sz = p.stat().st_size
                        cat_bytes += sz
                        total_junk_bytes += sz
                        total_junk_count += 1
                        if len(files_found) < 100:
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
                "file_count": total_junk_count if not recursive else len(files_found),
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


def delete_junk_files(junk_data: Optional[Dict[str, Any]] = None, confirmed: bool = False) -> Tuple[int, int, int, List[str]]:
    """Clean live junk files dynamically with graceful handling of OS-locked in-use files.

    Returns:
        Tuple[int, int, int, List[str]]: (deleted_count, reclaimed_bytes, locked_in_use_count, errors)
    """
    if not confirmed:
        return 0, 0, 0, ["Action canceled: User permission was not granted."]

    deleted_count = 0
    reclaimed_bytes = 0
    locked_in_use_count = 0
    errors: List[str] = []

    locations = get_junk_scan_locations()
    for loc in locations:
        folder_path = loc["path"]
        recursive = loc["recursive"]

        try:
            if not folder_path.exists():
                continue

            # Iterate through all files in location
            file_list = list(folder_path.rglob("*") if recursive else folder_path.glob("*"))
            for p in file_list:
                if p.is_file():
                    try:
                        sz = p.stat().st_size
                        # Clear read-only attribute if set
                        try:
                            os.chmod(p, stat.S_IWRITE | stat.S_IREAD)
                        except Exception:
                            pass

                        p.unlink()
                        deleted_count += 1
                        reclaimed_bytes += sz
                    except (PermissionError, OSError) as ex:
                        # File is locked / in-use by an active running OS process (e.g. Asus / Windows log)
                        locked_in_use_count += 1
                    except Exception as ex:
                        errors.append(f"{p.name}: {str(ex)}")

            # Clean empty subfolders if recursive
            if recursive:
                for sub in sorted(list(folder_path.rglob("*")), key=lambda x: len(str(x)), reverse=True):
                    if sub.is_dir():
                        try:
                            sub.rmdir()
                        except (PermissionError, OSError):
                            pass
        except (PermissionError, OSError):
            continue

    return deleted_count, reclaimed_bytes, locked_in_use_count, errors


def scan_duplicate_files(target_dirs: Optional[List[Path]] = None, min_size_bytes: int = 512, max_depth: int = 15) -> Dict[str, Any]:
    """Scan the entire PC across all drives and user directories for duplicate files using multi-tier SHA-256 matching."""
    if not target_dirs:
        target_dirs = get_system_wide_duplicate_scan_directories()

    # System directories and build directories to skip
    excluded_names = {
        "windows", "winnt", "program files", "program files (x86)",
        "$recycle.bin", "$winre_backup_partition.marker", "system volume information",
        "appdata", "localappdata", "node_modules", ".git", ".venv", "venv",
        "site-packages", "__pycache__", "winsxs", "assembly", "package cache",
        ".gemini", ".vscode", ".idea"
    }

    # Step 1: Discover candidate files and group by exact byte size
    size_map: Dict[int, List[Path]] = {}

    for folder in target_dirs:
        try:
            if not folder.exists():
                continue

            for root, dirs, files in os.walk(folder, topdown=True):
                # Filter out excluded system and cache directories
                dirs[:] = [d for d in dirs if d.lower() not in excluded_names and not d.startswith("$")]

                for fname in files:
                    if fname.startswith("~$") or fname.lower() == "desktop.ini" or fname.lower() == "thumbs.db":
                        continue
                    p = Path(root) / fname
                    try:
                        if p.is_file() and not p.is_symlink():
                            sz = p.stat().st_size
                            if sz >= min_size_bytes:
                                size_map.setdefault(sz, []).append(p)
                    except (PermissionError, OSError):
                        continue
        except (PermissionError, OSError):
            continue

    # Step 2: Multi-stage hashing (Partial Hash for large files -> Full SHA-256)
    duplicate_groups: List[Dict[str, Any]] = []
    total_wasted_bytes = 0
    total_duplicate_copies = 0

    for sz, paths in size_map.items():
        if len(paths) < 2:
            continue

        # Fast partial hash filter for large files (> 2MB)
        candidate_buckets: Dict[str, List[Path]] = {}
        if sz > 2 * 1024 * 1024:
            for p in paths:
                ph = get_partial_file_hash(p)
                if ph:
                    candidate_buckets.setdefault(ph, []).append(p)
        else:
            candidate_buckets["all"] = paths

        # Full SHA-256 verification
        for bucket_paths in candidate_buckets.values():
            if len(bucket_paths) < 2:
                continue

            hash_map: Dict[str, List[Path]] = {}
            for p in bucket_paths:
                h = get_file_hash(p)
                if h:
                    hash_map.setdefault(h, []).append(p)

            for f_hash, dup_paths in hash_map.items():
                if len(dup_paths) >= 2:
                    # Sort by modification time (oldest is original) then by path length
                    def sort_key(x: Path):
                        try:
                            mtime = x.stat().st_mtime
                        except Exception:
                            mtime = 0
                        return (mtime, len(str(x)))

                    sorted_paths = sorted(dup_paths, key=sort_key)
                    original = sorted_paths[0]
                    copies = sorted_paths[1:]

                    wasted_for_group = sz * len(copies)
                    total_wasted_bytes += wasted_for_group
                    total_duplicate_copies += len(copies)

                    duplicate_groups.append({
                        "hash": f_hash[:16],
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

    # Sort groups by largest wasted bytes first
    duplicate_groups.sort(key=lambda g: g["wasted_bytes"], reverse=True)

    return {
        "groups": duplicate_groups,
        "total_groups": len(duplicate_groups),
        "total_duplicate_copies": total_duplicate_copies,
        "total_wasted_bytes": total_wasted_bytes,
        "total_wasted_formatted": format_size(total_wasted_bytes),
    }


def delete_duplicate_copies(duplicate_data: Dict[str, Any], keep_original: bool = True, confirmed: bool = False) -> Tuple[int, int, int, List[str]]:
    """Delete redundant duplicate copies across the entire PC (preserving the original) with explicit permission.

    Returns:
        Tuple[int, int, int, List[str]]: (deleted_count, reclaimed_bytes, locked_count, errors)
    """
    if not confirmed:
        return 0, 0, 0, ["Action canceled: User permission was not granted."]

    deleted_count = 0
    reclaimed_bytes = 0
    locked_count = 0
    errors: List[str] = []

    for group in duplicate_data.get("groups", []):
        sz = group.get("file_size", 0)
        orig_path_str = group.get("original", {}).get("path", "")

        for copy_info in group.get("copies", []):
            c_path_str = copy_info["path"]
            if c_path_str == orig_path_str:
                continue  # Never touch the original

            c_path = Path(c_path_str)
            try:
                if c_path.exists() and c_path.is_file():
                    try:
                        os.chmod(c_path, stat.S_IWRITE | stat.S_IREAD)
                    except Exception:
                        pass

                    c_path.unlink()
                    deleted_count += 1
                    reclaimed_bytes += sz
            except (PermissionError, OSError) as ex:
                locked_count += 1
            except Exception as ex:
                errors.append(f"{c_path.name}: {str(ex)}")

    return deleted_count, reclaimed_bytes, locked_count, errors

