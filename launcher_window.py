import sys
from PySide6.QtCore import Qt, QSize, QEvent
from PySide6.QtGui import QScreen, QGuiApplication, QKeyEvent, QIcon, QCursor
from PySide6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLineEdit, QListWidget,
    QListWidgetItem, QLabel, QGraphicsDropShadowEffect, QApplication
)

from math_evaluator import evaluate_expression
from indexer import SearchItem
from styles import DARK_STYLESHEET, LIGHT_STYLESHEET

class ResultWidget(QWidget):
    """Custom widget for rendering each result item in the search list."""
    def __init__(self, item: SearchItem, is_math: bool = False, parent=None):
        super().__init__(parent)
        layout = QHBoxLayout(self)
        layout.setContentsMargins(8, 6, 8, 6)

        # Text container
        text_layout = QVBoxLayout()
        text_layout.setSpacing(2)

        if is_math:
            self.title_label = QLabel(f"= {item.action}")
            self.title_label.setObjectName("MathResultTitle")
            self.subtitle_label = QLabel("Presiona Enter para copiar al portapapeles")
            self.subtitle_label.setObjectName("ItemSubtitle")
            tag_text = "CALCULADORA"
        else:
            self.title_label = QLabel(item.title)
            self.title_label.setObjectName("ItemTitle")
            self.subtitle_label = QLabel(item.subtitle)
            self.subtitle_label.setObjectName("ItemSubtitle")
            tag_text = "WEB" if item.item_type == "web" else "APP"

        text_layout.addWidget(self.title_label)
        text_layout.addWidget(self.subtitle_label)

        layout.addLayout(text_layout)
        layout.addStretch()

        # Tag Badge
        tag_label = QLabel(tag_text)
        tag_label.setObjectName("ItemTag")
        layout.addWidget(tag_label, alignment=Qt.AlignVCenter)


class LauncherWindow(QWidget):
    def __init__(self, config_manager, indexer):
        super().__init__()
        self.config_manager = config_manager
        self.indexer = indexer

        # Window Flags & Attributes
        self.setWindowFlags(Qt.FramelessWindowHint | Qt.WindowStaysOnTopHint | Qt.Tool)
        self.setAttribute(Qt.WA_TranslucentBackground, True)
        self.resize(680, 420)

        self._init_ui()
        self.apply_theme()

    def _init_ui(self):
        main_layout = QVBoxLayout(self)
        main_layout.setContentsMargins(12, 12, 12, 12)

        # Outer rounded container widget
        self.container = QWidget()
        self.container.setObjectName("ContainerWidget")

        # Subtle shadow effect
        shadow = QGraphicsDropShadowEffect(self)
        shadow.setBlurRadius(24)
        shadow.setColor(Qt.black)
        shadow.setOffset(0, 8)
        self.container.setGraphicsEffect(shadow)

        container_layout = QVBoxLayout(self.container)
        container_layout.setContentsMargins(16, 16, 16, 16)
        container_layout.setSpacing(12)

        # Search Input
        self.search_input = QLineEdit()
        self.search_input.setObjectName("SearchField")
        self.search_input.setPlaceholderText("Escribe para buscar aplicaciones, matemáticas o web...")
        self.search_input.textChanged.connect(self.on_text_changed)
        container_layout.addWidget(self.search_input)

        # Results List Widget
        self.results_list = QListWidget()
        self.results_list.setObjectName("ResultsList")
        self.results_list.itemActivated.connect(self.execute_selected_item)
        container_layout.addWidget(self.results_list)

        main_layout.addWidget(self.container)

        # Install event filter on search input for custom key handling
        self.search_input.installEventFilter(self)

    def apply_theme(self):
        theme = self.config_manager.get("theme", "Dark")
        opacity = float(self.config_manager.get("opacity", 0.95))

        if theme == "Light":
            self.setStyleSheet(LIGHT_STYLESHEET)
        else:
            self.setStyleSheet(DARK_STYLESHEET)

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

    def show_launcher(self):
        self.apply_theme()
        self.position_top_third()
        self.show()
        self.raise_()
        self.activateWindow()
        self.search_input.setFocus()
        self.search_input.selectAll()
        self.on_text_changed(self.search_input.text())

    def eventFilter(self, watched, event):
        if watched == self.search_input and event.type() == QEvent.KeyPress:
            key_event = event
            if key_event.key() == Qt.Key_Escape:
                self.hide()
                return True
            elif key_event.key() in (Qt.Key_Return, Qt.Key_Enter):
                self.execute_selected_item()
                return True
            elif key_event.key() == Qt.Key_Down:
                current_row = self.results_list.currentRow()
                if current_row < self.results_list.count() - 1:
                    self.results_list.setCurrentRow(current_row + 1)
                return True
            elif key_event.key() == Qt.Key_Up:
                current_row = self.results_list.currentRow()
                if current_row > 0:
                    self.results_list.setCurrentRow(current_row - 1)
                return True

        return super().eventFilter(watched, event)

    def on_text_changed(self, text: str):
        self.results_list.clear()

        if not text.strip():
            return

        # 1. Real-time Safe Math Evaluation
        math_result = evaluate_expression(text)
        if math_result is not None:
            math_item = SearchItem("Evaluación Matemática", "Copiar al portapapeles", "math", math_result)
            list_item = QListWidgetItem(self.results_list)
            list_item.setSizeHint(QSize(0, 56))
            list_item.setData(Qt.UserRole, math_item)
            widget = ResultWidget(math_item, is_math=True)
            self.results_list.setItemWidget(list_item, widget)

        # 2. App & Web search results
        search_results = self.indexer.search(text)
        for item in search_results:
            list_item = QListWidgetItem(self.results_list)
            list_item.setSizeHint(QSize(0, 52))
            list_item.setData(Qt.UserRole, item)
            widget = ResultWidget(item, is_math=False)
            self.results_list.setItemWidget(list_item, widget)

        if self.results_list.count() > 0:
            self.results_list.setCurrentRow(0)

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

        self.hide()
