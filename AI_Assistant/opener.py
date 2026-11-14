"""
Universal App & Web Opener Engine for AI Assistant.
Opens any desktop application, system tool, folder, website, or web service on command.
"""

import os
import re
import subprocess
import webbrowser
import requests
import winreg

# Cache for desktop and start menu shortcuts
_SHORTCUTS_CACHE = None

def get_installed_shortcuts():
    global _SHORTCUTS_CACHE
    if _SHORTCUTS_CACHE is not None:
        return _SHORTCUTS_CACHE

    shortcuts = {}
    search_dirs = [
        r"C:\ProgramData\Microsoft\Windows\Start Menu\Programs",
        os.path.expandvars(r"%AppData%\Microsoft\Windows\Start Menu\Programs"),
        os.path.expandvars(r"%USERPROFILE%\OneDrive\Desktop"),
        os.path.expandvars(r"%USERPROFILE%\Desktop")
    ]

    for d in search_dirs:
        if os.path.exists(d):
            try:
                for item in os.listdir(d):
                    p = os.path.join(d, item)
                    if item.lower().endswith(".lnk"):
                        name = item.lower().replace(".lnk", "")
                        shortcuts[name] = p
                    elif os.path.isdir(p):
                        try:
                            for sub in os.listdir(p):
                                if sub.lower().endswith(".lnk"):
                                    name = sub.lower().replace(".lnk", "")
                                    shortcuts[name] = os.path.join(p, sub)
                        except Exception:
                            pass
            except Exception:
                pass

    _SHORTCUTS_CACHE = shortcuts
    return shortcuts

def get_registry_apps():
    apps = {}
    key_paths = [
        r"SOFTWARE\Microsoft\Windows\CurrentVersion\App Paths",
        r"SOFTWARE\WOW6432Node\Microsoft\Windows\CurrentVersion\App Paths"
    ]
    for root_hkey in [winreg.HKEY_LOCAL_MACHINE, winreg.HKEY_CURRENT_USER]:
        for kp in key_paths:
            try:
                with winreg.OpenKey(root_hkey, kp) as k:
                    num_subkeys = winreg.QueryInfoKey(k)[0]
                    for i in range(num_subkeys):
                        try:
                            sub = winreg.EnumKey(k, i)
                            with winreg.OpenKey(k, sub) as sk:
                                val = winreg.QueryValue(sk, "")
                                if val and os.path.exists(val):
                                    name = sub.lower().replace(".exe", "")
                                    apps[name] = val
                        except Exception:
                            pass
            except Exception:
                pass
    return apps

def universal_open(target):
    """
    Tries to open anything requested by the user:
    Apps, system tools, folders, websites, and services.
    Returns: (success_bool, message_string)
    """
    if not target:
        return False, ""

    # Clean target
    clean = target.strip().lower()
    clean = re.sub(r'^(can you|please|assistant|could you)?\s*(open|launch|start|run|go to)\s+', '', clean).strip()
    clean = clean.replace("the ", "")

    if not clean:
        return False, ""

    # 1. System Folders
    userprofile = os.path.expandvars(r"%USERPROFILE%")
    desktop_dir = os.path.join(userprofile, "OneDrive", "Desktop")
    if not os.path.exists(desktop_dir):
        desktop_dir = os.path.join(userprofile, "Desktop")

    folders = {
        "downloads": os.path.join(userprofile, "Downloads"),
        "desktop": desktop_dir,
        "documents": os.path.join(userprofile, "Documents"),
        "pictures": os.path.join(userprofile, "Pictures"),
        "music": os.path.join(userprofile, "Music"),
        "videos": os.path.join(userprofile, "Videos"),
        "recycle bin": "shell:RecycleBinFolder",
        "file explorer": "explorer.exe",
        "files": "explorer.exe",
        "my computer": "explorer.exe",
        "this pc": "explorer.exe"
    }

    for k, v in folders.items():
        if clean == k or clean == f"{k} folder":
            try:
                os.startfile(v)
                return True, f"Opening {k.title()}"
            except Exception:
                subprocess.Popen(["explorer.exe"])
                return True, f"Opening {k.title()}"

    # 2. Windows System Tools & UWP Apps
    system_tools = {
        "camera": ("microsoft.windows.camera:", True),
        "webcam": ("microsoft.windows.camera:", True),
        "calculator": ("calc.exe", False),
        "calc": ("calc.exe", False),
        "notepad": ("notepad.exe", False),
        "paint": ("mspaint.exe", False),
        "mspaint": ("mspaint.exe", False),
        "settings": ("ms-settings:", True),
        "task manager": ("taskmgr.exe", False),
        "taskmgr": ("taskmgr.exe", False),
        "command prompt": ("cmd.exe", False),
        "cmd": ("cmd.exe", False),
        "terminal": ("cmd.exe", False),
        "powershell": ("powershell.exe", False),
        "control panel": ("control", True),
        "snipping tool": ("ms-screenclip:", True),
        "snip": ("ms-screenclip:", True),
        "store": ("ms-windows-store:", True),
        "microsoft store": ("ms-windows-store:", True),
        "clock": ("ms-clock:", True),
        "alarm": ("ms-clock:", True),
        "calendar": ("outlookcal:", True),
        "maps": ("bingmaps:", True),
        "weather": ("bingweather:", True),
        "photos": ("ms-photos:", True),
        "voice recorder": ("soundrecorder:", True),
        "sound recorder": ("soundrecorder:", True),
    }

    for k, (cmd, is_uri) in system_tools.items():
        if clean == k or clean.startswith(f"{k} ") or clean.endswith(f" {k}"):
            try:
                if is_uri:
                    subprocess.Popen(["cmd", "/c", "start", cmd], shell=True)
                else:
                    subprocess.Popen([cmd])
                return True, f"Opening {k.title()}"
            except Exception as e:
                print(f"Error launching {k}: {e}")

    # 3. Known Popular Websites & Web Applications
    websites = {
        "chatgpt": "https://chatgpt.com",
        "chat gpt": "https://chatgpt.com",
        "deepseek": "https://chat.deepseek.com",
        "gemini": "https://gemini.google.com",
        "claude": "https://claude.ai",
        "youtube": "https://www.youtube.com",
        "google": "https://www.google.com",
        "gmail": "https://mail.google.com",
        "github": "https://www.github.com",
        "whatsapp": "https://web.whatsapp.com",
        "instagram": "https://www.instagram.com",
        "facebook": "https://www.facebook.com",
        "twitter": "https://www.x.com",
        "x": "https://www.x.com",
        "linkedin": "https://www.linkedin.com",
        "reddit": "https://www.reddit.com",
        "netflix": "https://www.netflix.com",
        "amazon": "https://www.amazon.in" if "in" in clean else "https://www.amazon.com",
        "flipkart": "https://www.flipkart.com",
        "myntra": "https://www.myntra.com",
        "hotstar": "https://www.hotstar.com",
        "jio cinema": "https://www.jiocinema.com",
        "jiocinema": "https://www.jiocinema.com",
        "prime video": "https://www.primevideo.com",
        "spotify": "https://open.spotify.com",
        "coursera": "https://www.coursera.org",
        "udemy": "https://www.udemy.com",
        "leetcode": "https://leetcode.com",
        "hackerrank": "https://www.hackerrank.com",
        "stackoverflow": "https://stackoverflow.com",
        "stack overflow": "https://stackoverflow.com",
        "canva": "https://www.canva.com",
        "figma": "https://www.figma.com",
        "pinterest": "https://www.pinterest.com",
        "twitch": "https://www.twitch.tv",
        "wikipedia": "https://www.wikipedia.org",
        "drive": "https://drive.google.com",
        "google drive": "https://drive.google.com",
        "google maps": "https://maps.google.com",
        "cricbuzz": "https://www.cricbuzz.com",
        "zoom": "https://zoom.us",
    }

    for k, url in websites.items():
        if clean == k or clean.startswith(f"{k} ") or clean.endswith(f" {k}"):
            webbrowser.open(url)
            return True, f"Opening {k.title()}"

    # 4. Search Local Installed Desktop & Start Menu Shortcuts
    aliases = {
        "vscode": "visual studio code",
        "vs code": "visual studio code",
        "code": "visual studio code",
        "ppt": "powerpoint",
        "doc": "word",
        "browser": "chrome",
        "edge": "microsoft edge",
        "python": "python 3.10",
        "jupyter": "jupyter notebook",
        "spyder": "spyder",
        "tableau": "tableau public",
        "postman": "postman agent",
        "mongodb": "mongodb compass",
        "codeblocks": "codeblocks",
        "zoom": "zoom workplace",
    }
    resolved_target = aliases.get(clean, clean)
    norm_target = re.sub(r'[^a-zA-Z0-9]', '', resolved_target)

    shortcuts = get_installed_shortcuts()
    best_match = None

    for sc_name, sc_path in shortcuts.items():
        if "uninstall" in sc_name.lower():
            continue
        norm_sc = re.sub(r'[^a-zA-Z0-9]', '', sc_name)
        if norm_target and (norm_target == norm_sc or norm_target in norm_sc or norm_sc in norm_target):
            best_match = (sc_name, sc_path)
            # Exact match preference
            if norm_target == norm_sc:
                break

    if best_match:
        name, path = best_match
        try:
            os.startfile(path)
            return True, f"Opening {name.title()}"
        except Exception as e:
            print(f"Failed to open shortcut {path}: {e}")

    # 5. Search Windows Registry Registered App Paths
    reg_apps = get_registry_apps()
    for app_name, app_path in reg_apps.items():
        norm_app = re.sub(r'[^a-zA-Z0-9]', '', app_name)
        if norm_target and (norm_target == norm_app or norm_target in norm_app):
            try:
                os.startfile(app_path)
                return True, f"Opening {app_name.title()}"
            except Exception:
                pass

    # 6. Domain or URL Detection
    domain_match = re.search(r'([a-zA-Z0-9\-]+\.(com|org|net|io|in|co|ai|edu|gov|app|dev))', clean)
    if domain_match:
        domain = domain_match.group(1)
        url = f"https://{domain}"
        webbrowser.open(url)
        return True, f"Opening {domain}"

    # 7. Fallback: If it's a single keyword, try opening as a website (e.g. "zomato" -> www.zomato.com)
    words = clean.split()
    if len(words) == 1 and words[0].isalnum():
        web_url = f"https://www.{words[0]}.com"
        webbrowser.open(web_url)
        return True, f"Opening {words[0].title()}"

    # 8. Otherwise, search Google for the target
    search_url = f"https://www.google.com/search?q={requests.utils.quote(clean)}"
    webbrowser.open(search_url)
    return True, f"Searching Google and opening {clean}"
