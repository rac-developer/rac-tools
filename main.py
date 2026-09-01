import sys
from PySide6.QtWidgets import QApplication

from config import ConfigManager
from indexer import AppIndexer
from hotkey_handler import GlobalHotkeyThread
from launcher_window import LauncherWindow
from settings_window import SettingsWindow
from tray import SystemTrayManager

def main():
    # Initialize Qt Application
    app = QApplication(sys.argv)
    app.setApplicationName("OmniFloat")
    # Crucial: prevent app from closing when launcher or settings windows are hidden/closed
    app.setQuitOnLastWindowClosed(False)

    # Core Components
    config_manager = ConfigManager()
    indexer = AppIndexer(config_manager)

    # UI Windows
    launcher_window = LauncherWindow(config_manager, indexer)
    settings_window = SettingsWindow(config_manager, indexer)

    # System Tray Integration
    tray_manager = SystemTrayManager(launcher_window, settings_window)

    # Global Hotkey Thread
    hotkey = config_manager.get("hotkey", "Alt+Space")
    hotkey_thread = GlobalHotkeyThread(key_str=hotkey)
    hotkey_thread.hotkey_triggered.connect(launcher_window.toggle_visibility)
    hotkey_thread.start()

    # Re-configure hotkey when settings change
    def on_settings_changed():
        new_hotkey = config_manager.get("hotkey", "Alt+Space")
        hotkey_thread.update_hotkey(new_hotkey)
        launcher_window.apply_theme()

    settings_window.settings_changed.connect(on_settings_changed)

    # Clean thread exit on app quit
    app.aboutToQuit.connect(hotkey_thread.stop)

    print("[OmniFloat] Application started in System Tray. Press 'Alt+Space' to toggle launcher.")
    # Show launcher on initial startup so user gets immediate visual feedback
    launcher_window.show_launcher()
    sys.exit(app.exec())

if __name__ == "__main__":
    main()
