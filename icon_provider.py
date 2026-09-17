import os
import re
import sys
import shutil
import subprocess

if sys.platform == "win32":
    try:
        import winreg
    except ImportError:
        winreg = None
else:
    winreg = None

from PySide6.QtCore import Qt, QFileInfo
from PySide6.QtGui import QIcon, QPixmap, QPainter, QColor, QFont, QPen
from PySide6.QtWidgets import QFileIconProvider

class IconManager:
    """
    Manages and caches application, browser, and utility icons.
    Automatically identifies the system's default browser from the Windows Registry or Linux XDG.
    """
    _instance = None

    def __init__(self):
        self._provider = QFileIconProvider()
        self._cache: dict[str, QIcon] = {}
        self._default_browser_icon: QIcon | None = None
        self._math_icon: QIcon | None = None

    @classmethod
    def instance(cls) -> "IconManager":
        if cls._instance is None:
            cls._instance = cls()
        return cls._instance

    def get_default_browser_exe(self) -> str | None:
        """Finds the default browser executable from Windows UserChoice registry association."""
        if not winreg:
            return None

        # 1. Official Windows UserChoice for HTTP associations
        try:
            with winreg.OpenKey(
                winreg.HKEY_CURRENT_USER,
                r"Software\Microsoft\Windows\Shell\Associations\UrlAssociations\http\UserChoice"
            ) as key:
                prog_id, _ = winreg.QueryValueEx(key, "ProgId")

            with winreg.OpenKey(
                winreg.HKEY_CLASSES_ROOT,
                rf"{prog_id}\shell\open\command"
            ) as key:
                cmd, _ = winreg.QueryValueEx(key, "")

            m = re.search(r"\"([^\"]+\.exe)\"", cmd, re.IGNORECASE) or re.search(r"([a-zA-Z]:\\[^\s]+\.exe)", cmd, re.IGNORECASE)
            if m and os.path.exists(m.group(1)):
                return m.group(1)
        except Exception:
            pass

        # 2. Fallback to HKCR http command
        try:
            with winreg.OpenKey(winreg.HKEY_CLASSES_ROOT, r"http\shell\open\command") as key:
                cmd, _ = winreg.QueryValueEx(key, "")
            m = re.search(r"\"([^\"]+\.exe)\"", cmd, re.IGNORECASE) or re.search(r"([a-zA-Z]:\\[^\s]+\.exe)", cmd, re.IGNORECASE)
            if m and os.path.exists(m.group(1)):
                return m.group(1)
        except Exception:
            pass

        # 3. Fallback to common browser executables in PATH or system folders
        common_candidates = ["brave.exe", "chrome.exe", "msedge.exe", "firefox.exe"]
        for cand in common_candidates:
            found = shutil.which(cand)
            if found and os.path.exists(found):
                return found

        return None

    def get_linux_default_browser_icon(self) -> QIcon | None:
        """Detects the default browser in Linux via xdg-settings / mimeapps.list and loads its themed icon."""
        desktop_id = None
        # Try xdg-settings
        if shutil.which("xdg-settings"):
            try:
                out = subprocess.check_output(
                    ["xdg-settings", "get", "default-web-browser"],
                    stderr=subprocess.DEVNULL,
                    text=True,
                    timeout=1
                ).strip()
                if out and out.endswith(".desktop"):
                    desktop_id = out
            except Exception:
                pass

        # Fallback to ~/.config/mimeapps.list
        if not desktop_id:
            mime_path = os.path.expanduser("~/.config/mimeapps.list")
            if os.path.exists(mime_path):
                try:
                    with open(mime_path, "r", encoding="utf-8", errors="ignore") as f:
                        for line in f:
                            if line.startswith(("x-scheme-handler/http=", "x-scheme-handler/https=", "text/html=")):
                                val = line.split("=", 1)[1].strip().split(";")[0]
                                if val.endswith(".desktop"):
                                    desktop_id = val
                                    break
                except Exception:
                    pass

        if desktop_id:
            icon_name = desktop_id.replace(".desktop", "")
            icon = QIcon.fromTheme(icon_name)
            if not icon.isNull():
                return icon

        # Generic XDG browser theme icon
        for generic in ["web-browser", "browser", "internet-web-browser"]:
            icon = QIcon.fromTheme(generic)
            if not icon.isNull():
                return icon

        return None

    def get_default_browser_icon(self) -> QIcon:
        """Returns the cached icon of the system's default browser."""
        if self._default_browser_icon and not self._default_browser_icon.isNull():
            return self._default_browser_icon

        if sys.platform == "win32":
            exe = self.get_default_browser_exe()
            if exe:
                icon = self._provider.icon(QFileInfo(exe))
                if not icon.isNull():
                    self._default_browser_icon = icon
                    return self._default_browser_icon
        else:
            icon = self.get_linux_default_browser_icon()
            if icon and not icon.isNull():
                self._default_browser_icon = icon
                return self._default_browser_icon

        self._default_browser_icon = self._create_web_fallback_icon()
        return self._default_browser_icon

    def _create_web_fallback_icon(self) -> QIcon:
        """Generates a stylish procedural globe icon if no browser executable icon is available."""
        pm = QPixmap(32, 32)
        pm.fill(QColor(0, 0, 0, 0))
        p = QPainter(pm)
        p.setRenderHint(QPainter.Antialiasing)
        p.setBrush(QColor(24, 24, 27))
        p.setPen(QPen(QColor(255, 255, 255, 140), 1.5))
        p.drawEllipse(3, 3, 26, 26)
        p.drawEllipse(9, 3, 14, 26)
        p.drawLine(3, 16, 29, 16)
        p.end()
        return QIcon(pm)

    def get_math_icon(self) -> QIcon:
        """Returns a stylish calculator badge icon."""
        if self._math_icon and not self._math_icon.isNull():
            return self._math_icon

        pm = QPixmap(32, 32)
        pm.fill(QColor(0, 0, 0, 0))
        p = QPainter(pm)
        p.setRenderHint(QPainter.Antialiasing)
        p.setBrush(QColor(24, 24, 27))
        p.setPen(QPen(QColor(255, 255, 255, 40), 1))
        p.drawRoundedRect(2, 2, 28, 28, 6, 6)
        p.setPen(QColor(255, 255, 255))
        font = QFont("Segoe UI", 15, QFont.Bold)
        p.setFont(font)
        p.drawText(pm.rect(), Qt.AlignCenter, "=")
        p.end()
        self._math_icon = QIcon(pm)
        return self._math_icon

    def get_icon(self, item) -> QIcon:
        """Returns the appropriate icon for any SearchItem."""
        if item.item_type == "math":
            return self.get_math_icon()

        if item.item_type == "web":
            return self.get_default_browser_icon()

        action = item.action
        if action in self._cache:
            return self._cache[action]

        # 1. If explicit icon name or path was indexed (e.g. from Linux .desktop)
        if getattr(item, "icon_path", None):
            theme_icon = QIcon.fromTheme(item.icon_path)
            if not theme_icon.isNull():
                self._cache[action] = theme_icon
                return theme_icon
            if os.path.exists(item.icon_path):
                file_icon = QIcon(item.icon_path)
                if not file_icon.isNull():
                    self._cache[action] = file_icon
                    return file_icon

        # 2. File or binary target
        target_path = action
        if not os.path.exists(target_path):
            resolved = shutil.which(target_path)
            if resolved and os.path.exists(resolved):
                target_path = resolved

        icon = None
        if os.path.exists(target_path):
            icon = self._provider.icon(QFileInfo(target_path))

        if not icon or icon.isNull():
            icon = self._provider.icon(QFileIconProvider.Computer)

        self._cache[action] = icon
        return icon
