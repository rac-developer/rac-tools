import os
from PySide6.QtCore import Qt, Signal
from PySide6.QtWidgets import (
    QDialog, QVBoxLayout, QHBoxLayout, QTabWidget, QWidget, QLabel,
    QLineEdit, QCheckBox, QListWidget, QPushButton, QComboBox, QSlider,
    QFileDialog, QMessageBox
)

class SettingsWindow(QDialog):
    settings_changed = Signal()

    def __init__(self, config_manager, indexer, parent=None):
        super().__init__(parent)
        self.config_manager = config_manager
        self.indexer = indexer

        self.setWindowTitle("OmniFloat - Configuración")
        self.resize(520, 380)

        self._init_ui()
        self._load_current_settings()

    def _init_ui(self):
        layout = QVBoxLayout(self)

        self.tabs = QTabWidget()

        # Tab 1: General
        self.tab_general = QWidget()
        gen_layout = QVBoxLayout(self.tab_general)

        gen_layout.addWidget(QLabel("Atajo de teclado global (ej. Alt+Space):"))
        self.hotkey_input = QLineEdit()
        gen_layout.addWidget(self.hotkey_input)

        self.autostart_checkbox = QCheckBox("Iniciar OmniFloat con Windows")
        gen_layout.addWidget(self.autostart_checkbox)
        gen_layout.addStretch()

        self.tabs.addTab(self.tab_general, "General")

        # Tab 2: Search Paths
        self.tab_paths = QWidget()
        paths_layout = QVBoxLayout(self.tab_paths)

        paths_layout.addWidget(QLabel("Carpetas indexadas para buscar ejecutables y accesos directos:"))
        self.paths_list = QListWidget()
        paths_layout.addWidget(self.paths_list)

        btn_layout = QHBoxLayout()
        self.btn_add_path = QPushButton("Agregar Carpeta")
        self.btn_add_path.clicked.connect(self.add_folder)
        self.btn_remove_path = QPushButton("Eliminar Selección")
        self.btn_remove_path.clicked.connect(self.remove_folder)
        btn_layout.addWidget(self.btn_add_path)
        btn_layout.addWidget(self.btn_remove_path)

        paths_layout.addLayout(btn_layout)
        self.tabs.addTab(self.tab_paths, "Rutas de Búsqueda")

        # Tab 3: Appearance
        self.tab_appearance = QWidget()
        app_layout = QVBoxLayout(self.tab_appearance)

        app_layout.addWidget(QLabel("Tema visual:"))
        self.theme_combo = QComboBox()
        self.theme_combo.addItems(["Dark", "Light"])
        app_layout.addWidget(self.theme_combo)

        app_layout.addWidget(QLabel("Opacidad de la ventana:"))
        self.opacity_slider = QSlider(Qt.Horizontal)
        self.opacity_slider.setRange(50, 100)
        self.opacity_slider.setValue(95)
        self.opacity_label = QLabel("95%")
        self.opacity_slider.valueChanged.connect(lambda v: self.opacity_label.setText(f"{v}%"))

        slider_layout = QHBoxLayout()
        slider_layout.addWidget(self.opacity_slider)
        slider_layout.addWidget(self.opacity_label)
        app_layout.addLayout(slider_layout)
        app_layout.addStretch()

        self.tabs.addTab(self.tab_appearance, "Apariencia")

        layout.addWidget(self.tabs)

        # Dialog Buttons
        bottom_buttons = QHBoxLayout()
        bottom_buttons.addStretch()
        self.btn_save = QPushButton("Guardar y Aplicar")
        self.btn_save.clicked.connect(self.save_settings)
        self.btn_cancel = QPushButton("Cancelar")
        self.btn_cancel.clicked.connect(self.reject)
        bottom_buttons.addWidget(self.btn_save)
        bottom_buttons.addWidget(self.btn_cancel)

        layout.addLayout(bottom_buttons)

    def _load_current_settings(self):
        self.hotkey_input.setText(self.config_manager.get("hotkey", "Alt+Space"))
        self.autostart_checkbox.setChecked(self.config_manager.get("autostart", False))

        self.paths_list.clear()
        for path in self.config_manager.get("search_paths", []):
            self.paths_list.addItem(path)

        current_theme = self.config_manager.get("theme", "Dark")
        index = self.theme_combo.findText(current_theme)
        if index >= 0:
            self.theme_combo.setCurrentIndex(index)

        opacity = int(float(self.config_manager.get("opacity", 0.95)) * 100)
        self.opacity_slider.setValue(opacity)
        self.opacity_label.setText(f"{opacity}%")

    def add_folder(self):
        folder = QFileDialog.getExistingDirectory(self, "Seleccionar Carpeta para Indexar")
        if folder:
            # Avoid duplicate paths
            existing = [self.paths_list.item(i).text() for i in range(self.paths_list.count())]
            if folder not in existing:
                self.paths_list.addItem(folder)

    def remove_folder(self):
        current_row = self.paths_list.currentRow()
        if current_row >= 0:
            self.paths_list.takeItem(current_row)

    def save_settings(self):
        self.config_manager.set("hotkey", self.hotkey_input.text().strip())
        self.config_manager.set("autostart", self.autostart_checkbox.isChecked())

        paths = [self.paths_list.item(i).text() for i in range(self.paths_list.count())]
        self.config_manager.set("search_paths", paths)

        self.config_manager.set("theme", self.theme_combo.currentText())
        self.config_manager.set("opacity", self.opacity_slider.value() / 100.0)

        # Trigger reindexing and notify main application
        self.indexer.reindex()
        self.settings_changed.emit()
        self.accept()
