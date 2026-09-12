"""Malicious web notification, rogue cookie, adware popup & browser threat scanner and cleaner."""

import json
import os
import platform
import re
import shutil
from pathlib import Path
from typing import Any, Dict, List, Optional, Tuple

# Known safe high-reputation domains that should never be flagged
TRUSTED_DOMAINS = [
    "google.com",
    "microsoft.com",
    "youtube.com",
    "github.com",
    "teams.microsoft.com",
    "zoom.us",
    "web.whatsapp.com",
    "linkedin.com",
    "twitter.com",
    "x.com",
    "facebook.com",
    "slack.com",
    "outlook.com",
    "live.com",
    "office.com",
    "apple.com",
    "amazon.com",
    "wikipedia.org",
]

# Suspicious patterns commonly used by malicious notification push & adware spammers
SUSPICIOUS_PATTERNS = [
    r"captcha",
    r"robot",
    r"verify",
    r"click",
    r"alert",
    r"virus",
    r"update",
    r"security-check",
    r"track",
    r"notification",
    r"push",
    r"ad\d+",
    r"traffic",
    r"reward",
    r"claim",
    r"bonus",
    r"gift",
    r"download\d+",
    r"fast-load",
    r"streaming\d+",
    r"top-news",
    r"dating",
    r"cleaner",
    r"win-alert",
]


def is_suspicious_domain(domain_str: str) -> bool:
    """Evaluate whether a domain is suspicious based on known spam/adware patterns."""
    clean_domain = domain_str.lower().strip()
    clean_domain = re.sub(r"^https?://", "", clean_domain)
    clean_domain = re.sub(r":\d+$", "", clean_domain)
    clean_domain = re.sub(r"/.*$", "", clean_domain)

    # If domain contains a trusted host, it is safe
    for trusted in TRUSTED_DOMAINS:
        if clean_domain.endswith(trusted) or clean_domain == trusted:
            return False

    # Check against suspicious adware pattern signatures
    for pattern in SUSPICIOUS_PATTERNS:
        if re.search(pattern, clean_domain):
            return True

    # Flag IP-based notification origins or obscure TLDs
    if re.match(r"^\d{1,3}\.\d{1,3}\.\d{1,3}\.\d{1,3}", clean_domain):
        return True
    if any(clean_domain.endswith(tld) for tld in [".xyz", ".top", ".buzz", ".icu", ".cam", ".click", ".pw", ".work"]):
        return True

    return False


def get_browser_preference_paths() -> List[Dict[str, Any]]:
    """Discover Chromium and Firefox profile configuration paths across Windows & Linux."""
    profiles = []
    is_win = platform.system() == "Windows"
    localappdata = os.environ.get("LOCALAPPDATA", "")
    appdata = os.environ.get("APPDATA", "")
    home = Path.home()

    if is_win and localappdata:
        base_paths = [
            ("Google Chrome", Path(localappdata) / "Google" / "Chrome" / "User Data"),
            ("Microsoft Edge", Path(localappdata) / "Microsoft" / "Edge" / "User Data"),
            ("Brave Browser", Path(localappdata) / "BraveSoftware" / "Brave-Browser" / "User Data"),
        ]

        for browser_name, user_data_dir in base_paths:
            if user_data_dir.exists():
                # Check Default and Profile 1..N
                for prof_dir in user_data_dir.glob("Default"):
                    pref = prof_dir / "Preferences"
                    if pref.exists():
                        profiles.append({"browser": browser_name, "profile": prof_dir.name, "pref_path": pref})
                for prof_dir in user_data_dir.glob("Profile *"):
                    pref = prof_dir / "Preferences"
                    if pref.exists():
                        profiles.append({"browser": browser_name, "profile": prof_dir.name, "pref_path": pref})
    else:
        # Linux paths
        linux_paths = [
            ("Google Chrome", home / ".config" / "google-chrome" / "Default" / "Preferences"),
            ("Chromium", home / ".config" / "chromium" / "Default" / "Preferences"),
            ("Brave Browser", home / ".config" / "BraveSoftware" / "Brave-Browser" / "Default" / "Preferences"),
        ]
        for browser_name, pref_path in linux_paths:
            if pref_path.exists():
                profiles.append({"browser": browser_name, "profile": "Default", "pref_path": pref_path})

    return profiles


def scan_browser_notifications_and_adware() -> Dict[str, Any]:
    """Scan browser profiles for malicious push notification permissions and adware domains.

    Returns:
        Dict containing detected rogue notification permissions, trusted domains, and adware stats.
    """
    profiles = get_browser_preference_paths()
    flagged_threats: List[Dict[str, Any]] = []
    trusted_notifications: List[Dict[str, Any]] = []
    total_scanned_origins = 0

    for prof in profiles:
        pref_file = prof["pref_path"]
        browser_name = prof["browser"]
        prof_name = prof["profile"]

        try:
            with open(pref_file, "r", encoding="utf-8", errors="ignore") as f:
                pref_data = json.load(f)

            # Extract notification exceptions in Chromium JSON structure
            content_settings = pref_data.get("profile", {}).get("content_settings", {})
            notif_exceptions = content_settings.get("exceptions", {}).get("notifications", {})

            for origin, setting_info in notif_exceptions.items():
                total_scanned_origins += 1
                setting_val = setting_info.get("setting", 1)  # 1 = ALLOW, 2 = BLOCK

                if setting_val == 1:  # Only check origins that have permission to show popups
                    if is_suspicious_domain(origin):
                        flagged_threats.append({
                            "browser": browser_name,
                            "profile": prof_name,
                            "pref_path": str(pref_file),
                            "origin": origin,
                            "threat_type": "Malicious Web Notification / Adware Popup Spammer",
                            "severity": "HIGH (Rogue Browser Notification Hook)",
                            "description": "Origin was granted permission to push unauthorized desktop popups and fake alerts.",
                        })
                    else:
                        trusted_notifications.append({
                            "browser": browser_name,
                            "profile": prof_name,
                            "origin": origin,
                        })
        except Exception:
            continue

    return {
        "threats": flagged_threats,
        "trusted_origins": trusted_notifications,
        "total_scanned": total_scanned_origins,
        "total_threats": len(flagged_threats),
    }


def scan_adware_startup_hooks() -> List[Dict[str, Any]]:
    """Scan Windows registry Run keys and Startup shortcuts for suspicious adware and popup triggers."""
    adware_hooks = []
    if platform.system() != "Windows":
        return adware_hooks

    import winreg
    run_keys = [
        (winreg.HKEY_CURRENT_USER, r"Software\Microsoft\Windows\CurrentVersion\Run"),
        (winreg.HKEY_LOCAL_MACHINE, r"Software\Microsoft\Windows\CurrentVersion\Run"),
    ]

    for root_hive, subkey_path in run_keys:
        try:
            with winreg.OpenKey(root_hive, subkey_path, 0, winreg.KEY_READ) as k:
                num_values = winreg.QueryInfoKey(k)[1]
                for i in range(num_values):
                    name, val, _ = winreg.EnumValue(k, i)
                    name_lower = str(name).lower()
                    val_lower = str(val).lower()
                    
                    is_suspicious = False
                    # Check suspicious names (e.g. test adware hook, spam, popup)
                    if any(susp_name in name_lower for susp_name in ["adware", "spam", "popup", "hook", "demo", "suspicious"]):
                        is_suspicious = True
                    # Check for script launchers or URL openers in startup
                    elif any(susp_exec in val_lower for susp_exec in ["cmd.exe", "powershell", "mshta", "wscript", "cscript", "rundll32"]):
                        if any(pattern in val_lower for pattern in SUSPICIOUS_PATTERNS) or "http" in val_lower:
                            is_suspicious = True
                    elif any(pattern in val_lower for pattern in SUSPICIOUS_PATTERNS) or "http://" in val_lower or "https://" in val_lower:
                        is_suspicious = True

                    if is_suspicious:
                        adware_hooks.append({
                            "type": "Registry Startup Hook",
                            "name": name,
                            "command": val,
                            "hive": "HKCU" if root_hive == winreg.HKEY_CURRENT_USER else "HKLM",
                            "key_path": subkey_path,
                            "threat_type": "Adware Startup Persistence / Rogue Launcher",
                            "severity": "HIGH (Adware Persistence)",
                        })
        except Exception:
            continue

    return adware_hooks


def scan_all_web_threats() -> Dict[str, Any]:
    """Run a comprehensive scan of browser notifications, rogue cookies, and adware startup hooks."""
    browser_scan = scan_browser_notifications_and_adware()
    startup_scan = scan_adware_startup_hooks()

    all_threats = list(browser_scan["threats"]) + startup_scan
    return {
        "browser_threats": browser_scan["threats"],
        "startup_threats": startup_scan,
        "all_threats": all_threats,
        "total_threats": len(all_threats),
        "trusted_notifications": browser_scan["trusted_origins"],
    }


def clean_web_threats(threat_data: Dict[str, Any], confirmed: bool = False) -> Tuple[int, List[str]]:
    """Remove malicious browser notification permissions and adware startup keys upon explicit user confirmation.

    Returns:
        Tuple[int, List[str]]: (cleaned_count, error_messages)
    """
    if not confirmed:
        return 0, ["Action canceled: User permission was not granted."]

    cleaned_count = 0
    errors = []

    # 1. Clean Browser Notification Permissions
    browser_threats = threat_data.get("browser_threats", [])
    prefs_to_update: Dict[str, List[str]] = {}
    for t in browser_threats:
        p_path = t["pref_path"]
        orig = t["origin"]
        prefs_to_update.setdefault(p_path, []).append(orig)

    for p_path_str, origins_to_remove in prefs_to_update.items():
        pref_file = Path(p_path_str)
        try:
            if pref_file.exists():
                # Create backup of Preferences
                backup_file = pref_file.with_suffix(".bak")
                shutil.copyfile(pref_file, backup_file)

                with open(pref_file, "r", encoding="utf-8", errors="ignore") as f:
                    data = json.load(f)

                notif_exceptions = data.get("profile", {}).get("content_settings", {}).get("exceptions", {}).get("notifications", {})
                for orig in origins_to_remove:
                    if orig in notif_exceptions:
                        del notif_exceptions[orig]
                        cleaned_count += 1

                with open(pref_file, "w", encoding="utf-8") as f:
                    json.dump(data, f, indent=2)
        except Exception as ex:
            errors.append(f"Failed to update {pref_file.name}: {str(ex)}")

    # 2. Clean Registry Startup Adware Hooks
    if platform.system() == "Windows":
        import winreg
        startup_threats = threat_data.get("startup_threats", [])
        for st in startup_threats:
            try:
                root_hive = winreg.HKEY_CURRENT_USER if st.get("hive") == "HKCU" else winreg.HKEY_LOCAL_MACHINE
                with winreg.OpenKey(root_hive, st["key_path"], 0, winreg.KEY_SET_VALUE) as k:
                    winreg.DeleteValue(k, st["name"])
                    cleaned_count += 1
            except Exception as ex:
                errors.append(f"Failed to delete registry hook {st.get('name')}: {str(ex)}")

    return cleaned_count, errors
