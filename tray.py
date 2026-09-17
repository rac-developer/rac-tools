from PySide6.QtCore import QObject
from PySide6.QtGui import QIcon, QPixmap, QPainter, QColor
from PySide6.QtWidgets import QSystemTrayIcon, QMenu, QApplication

class SystemTrayManager(QObject):
    def __init__(self, launcher_window, settings_window, parent=None):
        super().__init__(parent)
        self.launcher_window = launcher_window
        self.settings_window = settings_window

        self.tray_icon = QSystemTrayIcon(self._create_default_icon(), parent)
        self.tray_icon.setToolTip("OmniFloat Launcher")

        self._init_menu()
        self.tray_icon.activated.connect(self._on_tray_activated)
        self.tray_icon.show()

    def _create_default_icon(self) -> QIcon:
        """Generates a stylish programmatic icon for the system tray."""
        pixmap = QPixmap(32, 32)
        pixmap.fill(QColor(0, 0, 0, 0))
        painter = QPainter(pixmap)
        painter.setRenderHint(QPainter.Antialiasing)

        # Draw dark circle background with crisp border
        painter.setBrush(QColor(20, 20, 22))
        painter.setPen(QColor(255, 255, 255))
        painter.drawEllipse(2, 2, 28, 28)

        # Draw inner 'O' symbol
        painter.setPen(QColor(255, 255, 255))
        painter.setBrush(QColor(0, 0, 0, 0))
        painter.drawEllipse(9, 9, 14, 14)

        painter.end()
        return QIcon(pixmap)

    def _init_menu(self):
        menu = QMenu()

        action_open = menu.addAction("Abrir Launcher")
        action_open.triggered.connect(self.launcher_window.show_launcher)

        action_settings = menu.addAction("Configuración")
        action_settings.triggered.connect(self.open_settings)

        menu.addSeparator()

        action_quit = menu.addAction("Salir")
        action_quit.triggered.connect(QApplication.instance().quit)

        self.tray_icon.setContextMenu(menu)

    def open_settings(self):
        self.settings_window.show()
        self.settings_window.raise_()
        self.settings_window.activateWindow()

    def _on_tray_activated(self, reason):
        if reason in (QSystemTrayIcon.Trigger, QSystemTrayIcon.DoubleClick):
            self.launcher_window.toggle_visibility()
