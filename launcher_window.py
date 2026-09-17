import sys
import math
import ctypes
from PySide6.QtCore import Qt, QSize, QEvent, QTimer
from PySide6.QtGui import QScreen, QGuiApplication, QKeyEvent, QIcon, QCursor, QFontMetrics, QPixmap, QPainter, QColor, QPen
from PySide6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLineEdit, QListWidget,
    QListWidgetItem, QLabel, QGraphicsDropShadowEffect, QApplication, QSizePolicy, QFrame
)

from math_evaluator import evaluate_expression
from indexer import SearchItem
from icon_provider import IconManager
from styles import DARK_STYLESHEET, LIGHT_STYLESHEET

def create_search_icon(size: int = 18, color: QColor = QColor(255, 255, 255, 140)) -> QPixmap:
    """Generates a clean, crisp vector magnifying glass icon for the search bar."""
    pm = QPixmap(size, size)
    pm.fill(QColor(0, 0, 0, 0))
    p = QPainter(pm)
    p.setRenderHint(QPainter.Antialiasing)
    p.setPen(QPen(color, 1.8))
    r = size * 0.32
    cx, cy = size * 0.40, size * 0.40
    p.drawEllipse(int(cx - r), int(cy - r), int(r * 2), int(r * 2))
    rad = math.radians(45)
    x1 = cx + r * math.cos(rad)
    y1 = cy + r * math.sin(rad)
    p.drawLine(int(x1), int(y1), int(size - 2), int(size - 2))
    p.end()
    return pm

class ElidedLabel(QLabel):
    """QLabel that automatically truncates text with an ellipsis without clipping or pushing layouts."""
    def __init__(self, text: str = "", elide_mode=Qt.ElideRight, parent=None):
        super().__init__(parent)
        self._raw_text = text
        self._elide_mode = elide_mode
        self.setSizePolicy(QSizePolicy.Ignored, QSizePolicy.Preferred)
        self.setToolTip(text)
        self.setText(text)

    def setText(self, text: str):
        self._raw_text = text
        self.setToolTip(text)
        self._update_elided()

    def resizeEvent(self, event):
        super().resizeEvent(event)
        self._update_elided()

    def _update_elided(self):
        if not self._raw_text:
            super().setText("")
            return
        w = self.width()
        if w <= 20:
            super().setText(self._raw_text)
            return
        fm = QFontMetrics(self.font())
        elided = fm.elidedText(self._raw_text, self._elide_mode, w)
        super().setText(elided)


class ResultWidget(QWidget):
    """Custom widget for rendering each result item with its native icon, title, subtitle and badge."""
    def __init__(self, item: SearchItem, is_math: bool = False, parent=None):
        super().__init__(parent)
        layout = QHBoxLayout(self)
        layout.setContentsMargins(10, 6, 12, 6)
        layout.setSpacing(12)

        # 1. Icon (app native icon, default browser icon, or calculator icon)
        self.icon_label = QLabel()
        self.icon_label.setFixedSize(32, 32)
        self.icon_label.setAlignment(Qt.AlignCenter)
        icon = IconManager.instance().get_icon(item)
        self.icon_label.setPixmap(icon.pixmap(28, 28))
        layout.addWidget(self.icon_label, alignment=Qt.AlignVCenter)

        # 2. Text container (Title and Subtitle/Link)
        text_layout = QVBoxLayout()
        text_layout.setSpacing(2)
        text_layout.setContentsMargins(0, 0, 0, 0)

        if is_math:
            self.title_label = ElidedLabel(f"= {item.action}", elide_mode=Qt.ElideRight)
            self.title_label.setObjectName("MathResultTitle")
            self.subtitle_label = ElidedLabel("Presiona Enter para copiar al portapapeles", elide_mode=Qt.ElideRight)
            self.subtitle_label.setObjectName("ItemSubtitle")
            tag_text = "CALCULADORA"
        else:
            self.title_label = ElidedLabel(item.title, elide_mode=Qt.ElideRight)
            self.title_label.setObjectName("ItemTitle")
            elide_mode = Qt.ElideRight if item.item_type == "web" else Qt.ElideMiddle
            self.subtitle_label = ElidedLabel(item.subtitle, elide_mode=elide_mode)
            self.subtitle_label.setObjectName("ItemSubtitle")
            tag_text = "WEB" if item.item_type == "web" else "APP"

        text_layout.addWidget(self.title_label)
        text_layout.addWidget(self.subtitle_label)

        # Stretch factor 1 to give the text layout all available horizontal space
        layout.addLayout(text_layout, 1)

        # 3. Tag Badge
        tag_label = QLabel(tag_text)
        tag_label.setObjectName("ItemTag")
        layout.addWidget(tag_label, alignment=Qt.AlignVCenter)


class LauncherWindow(QWidget):
    WINDOW_WIDTH = 680
    COLLAPSED_HEIGHT = 78

    def __init__(self, config_manager, indexer):
        super().__init__()
        self.config_manager = config_manager
        self.indexer = indexer

        # Window Flags & Attributes
        self.setWindowFlags(Qt.FramelessWindowHint | Qt.WindowStaysOnTopHint | Qt.Tool)
        self.setAttribute(Qt.WA_TranslucentBackground, True)
        self.resize(self.WINDOW_WIDTH, self.COLLAPSED_HEIGHT)

        # Blur / Auto-hide on losing focus
        self._can_close_on_blur = False
        self._blur_timer = QTimer(self)
        self._blur_timer.setSingleShot(True)
        self._blur_timer.timeout.connect(self._enable_close_on_blur)

        self._init_ui()
        self.apply_theme()

    def _init_ui(self):
        self.main_layout = QVBoxLayout(self)
        self.main_layout.setContentsMargins(12, 12, 12, 12)

        # Outer rounded container widget (The unified frosted glass capsule)
        self.container = QWidget()
        self.container.setObjectName("ContainerWidget")

        # Subtle shadow effect
        shadow = QGraphicsDropShadowEffect(self)
        shadow.setBlurRadius(24)
        shadow.setColor(QColor(0, 0, 0, 160))
        shadow.setOffset(0, 8)
        self.container.setGraphicsEffect(shadow)

        self.container_layout = QVBoxLayout(self.container)
        self.container_layout.setContentsMargins(16, 6, 16, 6)
        self.container_layout.setSpacing(0)

        # Search Bar Header Layout (Vector Search Icon + Transparent Text Field)
        self.search_header_layout = QHBoxLayout()
        self.search_header_layout.setContentsMargins(0, 0, 0, 0)
        self.search_header_layout.setSpacing(12)

        self.search_icon_label = QLabel()
        self.search_icon_label.setFixedSize(20, 20)
        self.search_icon_label.setAlignment(Qt.AlignCenter)
        self.search_header_layout.addWidget(self.search_icon_label, alignment=Qt.AlignVCenter)

        self.search_input = QLineEdit()
        self.search_input.setObjectName("SearchField")
        self.search_input.setFixedHeight(42)
        self.search_input.setPlaceholderText("Escribe para buscar aplicaciones, cálculos o web...")
        self.search_input.textChanged.connect(self.on_text_changed)
        self.search_header_layout.addWidget(self.search_input, 1)

        self.container_layout.addLayout(self.search_header_layout)

        # Subtle divider between search bar and results (hidden when empty)
        self.divider = QFrame()
        self.divider.setObjectName("SearchDivider")
        self.divider.setFrameShape(QFrame.HLine)
        self.divider.setFixedHeight(1)
        self.divider.hide()
        self.container_layout.addWidget(self.divider)

        # Results List Widget (hidden until user searches)
        self.results_list = QListWidget()
        self.results_list.setObjectName("ResultsList")
        self.results_list.itemActivated.connect(self.execute_selected_item)
        self.results_list.itemClicked.connect(self.execute_selected_item)
        self.results_list.hide()
        self.container_layout.addWidget(self.results_list)

        self.main_layout.addWidget(self.container)

        # Install event filter on search input for custom key handling
        self.search_input.installEventFilter(self)

    def apply_theme(self):
        theme = self.config_manager.get("theme", "Dark")
        opacity = float(self.config_manager.get("opacity", 0.95))

        if theme == "Light":
            self.setStyleSheet(LIGHT_STYLESHEET)
            is_dark = False
            icon_color = QColor(0, 0, 0, 130)
        else:
            self.setStyleSheet(DARK_STYLESHEET)
            is_dark = True
            icon_color = QColor(255, 255, 255, 140)

        self.search_icon_label.setPixmap(create_search_icon(18, icon_color))
        self.setWindowOpacity(opacity)

    def position_top_third(self):
        """Positions the window horizontally centered in the top third of the current active screen."""
        cursor_pos = QCursor.pos()
        screen = QGuiApplication.screenAt(cursor_pos) if cursor_pos else None
        if not screen:
            screen = QGuiApplication.primaryScreen()

        if screen:
            geo = screen.geometry()
            x = geo.x() + (geo.width() - self.width()) // 2
            y = geo.y() + (geo.height() // 5)  # Top third
            self.move(x, y)

    def toggle_visibility(self):
        if self.isVisible():
            self.hide()
        else:
            self.show_launcher()

    def _enable_close_on_blur(self):
        self._can_close_on_blur = True
        if self.isVisible() and not self.isActiveWindow():
            self.hide()

    def show_launcher(self):
        self._blur_timer.stop()
        self._can_close_on_blur = False
        self.apply_theme()
        self.show()
        self.raise_()
        self.activateWindow()
        try:
            import ctypes
            ctypes.windll.user32.SetForegroundWindow(int(self.winId()))
        except Exception:
            pass
        current_text = self.search_input.text()
        self.on_text_changed(current_text)
        self.position_top_third()
        self.search_input.setFocus()
        if current_text:
            self.search_input.selectAll()
        # Arm auto-close on blur after initial window activation settles
        self._blur_timer.start(150)

    def hideEvent(self, event):
        self._blur_timer.stop()
        self._can_close_on_blur = False
        super().hideEvent(event)

    def changeEvent(self, event):
        if event.type() == QEvent.ActivationChange:
            if self._can_close_on_blur and not self.isActiveWindow():
                self.hide()
        super().changeEvent(event)

    def keyPressEvent(self, event: QKeyEvent):
        if event.key() == Qt.Key_Escape:
            self.hide()
            return
        super().keyPressEvent(event)

    def eventFilter(self, watched, event):
        if watched == self.search_input and event.type() == QEvent.KeyPress:
            key_event = event
            if key_event.key() == Qt.Key_Escape:
                self.hide()
                return True
            elif key_event.key() in (Qt.Key_Return, Qt.Key_Enter):
                if self.results_list.isVisible() and self.results_list.count() > 0:
                    self.execute_selected_item()
                return True
            elif key_event.key() == Qt.Key_Down:
                if self.results_list.isVisible():
                    current_row = self.results_list.currentRow()
                    if current_row < self.results_list.count() - 1:
                        self.results_list.setCurrentRow(current_row + 1)
                return True
            elif key_event.key() == Qt.Key_Up:
                if self.results_list.isVisible():
                    current_row = self.results_list.currentRow()
                    if current_row > 0:
                        self.results_list.setCurrentRow(current_row - 1)
                return True

        return super().eventFilter(watched, event)

    def on_text_changed(self, text: str):
        self.results_list.clear()

        cleaned = text.strip()
        if not cleaned:
            self.divider.hide()
            self.results_list.hide()
            self.container_layout.setContentsMargins(16, 6, 16, 6)
            self.container_layout.activate()
            self.main_layout.activate()
            self.resize(self.WINDOW_WIDTH, self.COLLAPSED_HEIGHT)
            return

        # 1. Real-time Safe Math Evaluation
        math_result = evaluate_expression(cleaned)
        if math_result is not None:
            math_item = SearchItem("Evaluación Matemática", "Copiar al portapapeles", "math", math_result)
            list_item = QListWidgetItem(self.results_list)
            list_item.setSizeHint(QSize(0, 60))
            list_item.setData(Qt.UserRole, math_item)
            widget = ResultWidget(math_item, is_math=True)
            self.results_list.setItemWidget(list_item, widget)

        # 2. App & Web search results
        search_results = self.indexer.search(cleaned)
        for item in search_results:
            list_item = QListWidgetItem(self.results_list)
            list_item.setSizeHint(QSize(0, 60))
            list_item.setData(Qt.UserRole, item)
            widget = ResultWidget(item, is_math=False)
            self.results_list.setItemWidget(list_item, widget)

        count = self.results_list.count()
        if count > 0:
            self.results_list.setCurrentRow(0)
            self.divider.show()
            self.results_list.show()
            self.container_layout.setContentsMargins(16, 6, 16, 8)
            content_height = min(count * 60 + 6, 380)
            target_height = self.COLLAPSED_HEIGHT + 1 + content_height
            self.container_layout.activate()
            self.main_layout.activate()
            self.resize(self.WINDOW_WIDTH, target_height)
        else:
            self.divider.hide()
            self.results_list.hide()
            self.container_layout.setContentsMargins(16, 6, 16, 6)
            self.container_layout.activate()
            self.main_layout.activate()
            self.resize(self.WINDOW_WIDTH, self.COLLAPSED_HEIGHT)

    def execute_selected_item(self):
        selected = self.results_list.currentItem()
        if not selected:
            return

        item = selected.data(Qt.UserRole)
        if not item:
            return

        if item.item_type == "math":
            # Copy to clipboard
            clipboard = QGuiApplication.clipboard()
            clipboard.setText(item.action)
            print(f"[LauncherWindow] Copied math result '{item.action}' to clipboard.")
        else:
            item.execute()

        self.search_input.clear()
        self.hide()
