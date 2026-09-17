import sys
from PySide6.QtWidgets import QApplication
from PySide6.QtNetwork import QLocalServer, QLocalSocket

from config import ConfigManager
from indexer import AppIndexer
from hotkey_handler import GlobalHotkeyThread
from launcher_window import LauncherWindow
from settings_window import SettingsWindow
from tray import SystemTrayManager

SOCKET_NAME = "omnifloat_single_instance_socket"

def main():
    app = QApplication(sys.argv)
    app.setApplicationName("OmniFloat")

    # 1. Check if another instance is already running via QLocalSocket
    socket = QLocalSocket()
    socket.connectToServer(SOCKET_NAME)
    if socket.waitForConnected(300):
        cmd = "toggle"
        if "--settings" in sys.argv:
            cmd = "settings"
        elif "--show" in sys.argv:
            cmd = "show"
        socket.write(cmd.encode("utf-8"))
        socket.flush()
        socket.waitForBytesWritten(300)
        socket.disconnectFromServer()
        print(f"[OmniFloat] Signal '{cmd}' sent to running instance. Exiting.")
        return 0

    # 2. Primary instance: initialize QLocalServer
    server = QLocalServer()
    # Clean up any stale socket from previous abnormal terminations
    QLocalServer.removeServer(SOCKET_NAME)
    if not server.listen(SOCKET_NAME):
        print(f"[OmniFloat] Warning: Could not start local IPC server: {server.errorString()}")

    # Crucial: prevent app from closing when launcher or settings windows are hidden/closed
    app.setQuitOnLastWindowClosed(False)

    # Core Components
    config_manager = ConfigManager()

    # Automatically ensure desktop shortcut is created on first run
    if not config_manager.get("desktop_shortcut_created", False):
        try:
            from install_shortcuts import create_desktop_shortcut
            create_desktop_shortcut()
            config_manager.set("desktop_shortcut_created", True)
        except Exception as e:
            print(f"[OmniFloat] Note: Could not auto-create desktop shortcut: {e}")

    indexer = AppIndexer(config_manager)

    # UI Windows
    launcher_window = LauncherWindow(config_manager, indexer)
    settings_window = SettingsWindow(config_manager, indexer)

    # IPC connection handler
    def on_new_connection():
        client_socket = server.nextPendingConnection()
        if client_socket:
            if client_socket.waitForReadyRead(300):
                msg = bytes(client_socket.readAll()).decode("utf-8").strip()
                if msg == "settings":
                    settings_window.show()
                    settings_window.raise_()
                    settings_window.activateWindow()
                elif msg == "show":
                    launcher_window.show_launcher()
                else:
                    launcher_window.toggle_visibility()
            client_socket.disconnectFromServer()

    server.newConnection.connect(on_new_connection)

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

    # Clean exit on app quit
    def cleanup():
        hotkey_thread.stop()
        server.close()
        QLocalServer.removeServer(SOCKET_NAME)

    app.aboutToQuit.connect(cleanup)

    print("[OmniFloat] Application started in System Tray. Press 'Alt+Space' or run 'omnifloat --toggle' to toggle.")
    # Show launcher on initial startup so user gets immediate visual feedback
    launcher_window.show_launcher()
    sys.exit(app.exec())

if __name__ == "__main__":
    main()
