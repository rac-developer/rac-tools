import os
import json
import sys

if sys.platform == "win32":
    try:
        import winreg
    except ImportError:
        winreg = None
else:
    winreg = None

DEFAULT_CONFIG = {
    "hotkey": "Alt+Space",
    "autostart": False,
    "search_paths": [],
    "theme": "Dark",
    "opacity": 1.0
}

CONFIG_FILE_PATH = os.path.join(os.path.expanduser("~"), ".omnifloat_config.json")
REG_KEY_PATH = r"Software\Microsoft\Windows\CurrentVersion\Run"
APP_NAME = "OmniFloat"

class ConfigManager:
    def __init__(self):
        self.config = DEFAULT_CONFIG.copy()
        self.load_config()
        self._ensure_default_paths()

    def _ensure_default_paths(self):
        """Adds standard system application search paths based on the host OS."""
        if not self.config.get("search_paths"):
            defaults = []
            if sys.platform == "win32":
                user_start = os.path.join(os.environ.get("APPDATA", ""), r"Microsoft\Windows\Start Menu\Programs")
                common_start = os.path.join(os.environ.get("PROGRAMDATA", ""), r"Microsoft\Windows\Start Menu\Programs")
                user_desktop = os.path.join(os.path.expanduser("~"), "Desktop")
                onedrive_desktop = os.path.join(os.path.expanduser("~"), "OneDrive", "Desktop")
                candidates = [user_start, common_start, user_desktop, onedrive_desktop]
            else:
                # Standard Linux XDG and Flatpak/Snap application directories
                candidates = [
                    "/usr/share/applications",
                    "/usr/local/share/applications",
                    os.path.expanduser("~/.local/share/applications"),
                    "/var/lib/flatpak/exports/share/applications",
                    os.path.expanduser("~/.local/share/flatpak/exports/share/applications"),
                    "/var/lib/snapd/desktop/applications",
                ]

            for path in candidates:
                if os.path.exists(path) and path not in defaults:
                    defaults.append(path)
            self.config["search_paths"] = defaults
            self.save_config()

    def load_config(self):
        if os.path.exists(CONFIG_FILE_PATH):
            try:
                with open(CONFIG_FILE_PATH, "r", encoding="utf-8") as f:
                    loaded = json.load(f)
                    self.config.update(loaded)
            except Exception as e:
                print(f"[ConfigManager] Error loading config: {e}")
        else:
            self.save_config()

    def save_config(self):
        try:
            with open(CONFIG_FILE_PATH, "w", encoding="utf-8") as f:
                json.dump(self.config, f, indent=4, ensure_ascii=False)
        except Exception as e:
            print(f"[ConfigManager] Error saving config: {e}")

    def get(self, key, default=None):
        return self.config.get(key, default)

    def set(self, key, value):
        self.config[key] = value
        self.save_config()
        if key == "autostart":
            self.set_autostart(value)

    def set_autostart(self, enable: bool):
        """Configures autostart on system boot for Windows (Registry) or Linux (XDG autostart .desktop)."""
        if sys.platform == "win32" and winreg:
            try:
                key = winreg.OpenKey(winreg.HKEY_CURRENT_USER, REG_KEY_PATH, 0, winreg.KEY_ALL_ACCESS)
                if enable:
                    executable_path = f'"{sys.executable}" "{os.path.abspath(sys.argv[0])}"'
                    winreg.SetValueEx(key, APP_NAME, 0, winreg.REG_SZ, executable_path)
                else:
                    try:
                        winreg.DeleteValue(key, APP_NAME)
                    except FileNotFoundError:
                        pass
                winreg.CloseKey(key)
            except Exception as e:
                print(f"[ConfigManager] Windows Registry autostart error: {e}")
        else:
            # Linux XDG Autostart
            autostart_dir = os.path.expanduser("~/.config/autostart")
            desktop_file = os.path.join(autostart_dir, "omnifloat.desktop")
            if enable:
                try:
                    os.makedirs(autostart_dir, exist_ok=True)
                    cmd = f'"{sys.executable}" "{os.path.abspath(sys.argv[0])}"'
                    content = (
                        "[Desktop Entry]\n"
                        "Type=Application\n"
                        "Name=OmniFloat\n"
                        "Comment=OmniFloat Floating Launcher\n"
                        f"Exec={cmd}\n"
                        "Terminal=false\n"
                        "X-GNOME-Autostart-enabled=true\n"
                    )
                    with open(desktop_file, "w", encoding="utf-8") as f:
                        f.write(content)
                except Exception as e:
                    print(f"[ConfigManager] Linux XDG autostart write error: {e}")
            else:
                if os.path.exists(desktop_file):
                    try:
                        os.remove(desktop_file)
                    except Exception as e:
                        print(f"[ConfigManager] Linux XDG autostart remove error: {e}")
