import ctypes
from ctypes import wintypes
from PySide6.QtCore import QThread, Signal

# Windows API Constants
WM_HOTKEY = 0x0312
MOD_ALT = 0x0001
MOD_CONTROL = 0x0002
MOD_SHIFT = 0x0004
MOD_WIN = 0x0008
MOD_NOREPEAT = 0x4000

VK_SPACE = 0x20
HOTKEY_ID = 1001

class GlobalHotkeyThread(QThread):
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
        # Register hotkey on thread initialization
        res = self.user32.RegisterHotKey(None, HOTKEY_ID, self.modifiers, self.vk)
        if not res:
            print(f"[GlobalHotkeyThread] Warning: Could not register hotkey '{self.key_str}' (Error code {ctypes.GetLastError()})")
        else:
            print(f"[GlobalHotkeyThread] Registered global hotkey '{self.key_str}' successfully.")

        msg = wintypes.MSG()
        while self.running:
            # GetMessage blocks until a message is available
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
        # Post QUIT message to break GetMessageW loop
        if hasattr(self, "worker_thread_id") and self.worker_thread_id:
            self.user32.PostThreadMessageW(self.worker_thread_id, 0x0012, 0, 0)
        self.wait(1000)
