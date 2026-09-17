import os
import json
import winreg
import sys

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
        # Add default Windows Start Menu and Desktop paths if search_paths is empty
        if not self.config.get("search_paths"):
            defaults = []
            user_start = os.path.join(os.environ.get("APPDATA", ""), r"Microsoft\Windows\Start Menu\Programs")
            common_start = os.path.join(os.environ.get("PROGRAMDATA", ""), r"Microsoft\Windows\Start Menu\Programs")
            user_desktop = os.path.join(os.path.expanduser("~"), "Desktop")

            for path in [user_start, common_start, user_desktop]:
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
            print(f"[ConfigManager] Registry autostart error: {e}")
