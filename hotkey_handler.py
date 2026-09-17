import sys
from PySide6.QtCore import QThread, Signal

# Optional pynput for Linux X11 environments
try:
    from pynput import keyboard
    HAS_PYNPUT = True
except ImportError:
    HAS_PYNPUT = False

def _format_pynput_hotkey(key_str: str) -> str:
    """Formats human-readable hotkey like 'Alt+Space' into pynput syntax '<alt>+<space>'."""
    parts = [p.strip().lower() for p in key_str.split("+")]
    formatted = []
    for p in parts:
        if p in ("alt", "option"):
            formatted.append("<alt>")
        elif p in ("ctrl", "control"):
            formatted.append("<ctrl>")
        elif p in ("shift",):
            formatted.append("<shift>")
        elif p in ("win", "cmd", "super"):
            formatted.append("<cmd>")
        elif p in ("space", "espacio", "spacebar"):
            formatted.append("<space>")
        else:
            formatted.append(p)
    return "+".join(formatted)

if sys.platform == "win32":
    import ctypes
    from ctypes import wintypes

    # Windows API Constants
    WM_HOTKEY = 0x0312
    MOD_ALT = 0x0001
    MOD_CONTROL = 0x0002
    MOD_SHIFT = 0x0004
    MOD_WIN = 0x0008
    MOD_NOREPEAT = 0x4000

    VK_SPACE = 0x20
    HOTKEY_ID = 1001

    class Win32HotkeyThread(QThread):
        hotkey_triggered = Signal()

        def __init__(self, key_str: str = "Alt+Space", parent=None):
            super().__init__(parent)
            self.key_str = key_str
            self.running = True
            self.user32 = ctypes.windll.user32
            self.modifiers, self.vk = self._parse_hotkey(key_str)

        def _parse_hotkey(self, key_str: str):
            parts = [p.strip().lower() for p in key_str.split("+")]
            mods = MOD_NOREPEAT
            vk = VK_SPACE

            for part in parts:
                if part in ("alt", "option"):
                    mods |= MOD_ALT
                elif part in ("ctrl", "control"):
                    mods |= MOD_CONTROL
                elif part in ("shift",):
                    mods |= MOD_SHIFT
                elif part in ("win", "cmd", "super"):
                    mods |= MOD_WIN
                elif part in ("space", "espacio", "spacebar"):
                    vk = VK_SPACE
                elif len(part) == 1:
                    vk = ord(part.upper())

            return mods, vk

        def update_hotkey(self, key_str: str):
            self.key_str = key_str
            self.modifiers, self.vk = self._parse_hotkey(key_str)
            if hasattr(self, "worker_thread_id") and self.worker_thread_id:
                self.user32.PostThreadMessageW(self.worker_thread_id, 0x0464, 0, 0)

        def run(self):
            self.worker_thread_id = int(ctypes.windll.kernel32.GetCurrentThreadId())
            res = self.user32.RegisterHotKey(None, HOTKEY_ID, self.modifiers, self.vk)
            if not res:
                print(f"[Win32HotkeyThread] Warning: Could not register hotkey '{self.key_str}' (Error code {ctypes.GetLastError()})")
            else:
                print(f"[Win32HotkeyThread] Registered global hotkey '{self.key_str}' successfully.")

            msg = wintypes.MSG()
            while self.running:
                b_ret = self.user32.GetMessageW(ctypes.byref(msg), None, 0, 0)
                if b_ret == 0 or b_ret == -1:
                    break
                if msg.message == WM_HOTKEY and msg.wParam == HOTKEY_ID:
                    self.hotkey_triggered.emit()
                elif msg.message == 0x0464:  # WM_RELOAD_HOTKEY
                    self.user32.UnregisterHotKey(None, HOTKEY_ID)
                    self.user32.RegisterHotKey(None, HOTKEY_ID, self.modifiers, self.vk)
                self.user32.TranslateMessage(ctypes.byref(msg))
                self.user32.DispatchMessageW(ctypes.byref(msg))

            self.user32.UnregisterHotKey(None, HOTKEY_ID)

        def stop(self):
            self.running = False
            if hasattr(self, "worker_thread_id") and self.worker_thread_id:
                self.user32.PostThreadMessageW(self.worker_thread_id, 0x0012, 0, 0)
            self.wait(1000)

    GlobalHotkeyThread = Win32HotkeyThread

else:
    # Linux implementations
    if HAS_PYNPUT:
        class LinuxPynputHotkeyThread(QThread):
            hotkey_triggered = Signal()

            def __init__(self, key_str: str = "Alt+Space", parent=None):
                super().__init__(parent)
                self.key_str = key_str
                self.listener = None

            def run(self):
                hotkey_fmt = _format_pynput_hotkey(self.key_str)
                try:
                    self.listener = keyboard.GlobalHotKeys({
                        hotkey_fmt: self.hotkey_triggered.emit
                    })
                    print(f"[LinuxHotkeyThread] Listening for global hotkey '{self.key_str}' via pynput.")
                    self.listener.start()
                    self.listener.join()
                except Exception as e:
                    print(f"[LinuxHotkeyThread] Warning: Could not register pynput hotkey: {e}")

            def update_hotkey(self, key_str: str):
                self.key_str = key_str
                if self.listener:
                    try:
                        self.listener.stop()
                    except Exception:
                        pass
                self.start()

            def stop(self):
                if self.listener:
                    try:
                        self.listener.stop()
                    except Exception:
                        pass
                self.wait(1000)

        GlobalHotkeyThread = LinuxPynputHotkeyThread
    else:
        class LinuxFallbackHotkeyThread(QThread):
            hotkey_triggered = Signal()

            def __init__(self, key_str: str = "Alt+Space", parent=None):
                super().__init__(parent)
                self.key_str = key_str

            def run(self):
                print(f"[LinuxHotkey] IPC mode active. Run 'omnifloat --toggle' or bind it to a system shortcut.")

            def update_hotkey(self, key_str: str):
                self.key_str = key_str

            def stop(self):
                pass

        GlobalHotkeyThread = LinuxFallbackHotkeyThread
