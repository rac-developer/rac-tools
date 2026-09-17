# AGENTS.md - OmniFloat

> Guía ultraconcisa de arquitectura, patrones y comandos para agentes de IA en OmniFloat.

---

## 1. Propósito y Stack Tecnológico
* **Tipo**: Lanzador flotante minimalista multiplataforma para **Windows** y **Linux** (estilo Spotlight / Raycast).
* **Lenguaje**: Python 3.9+
* **GUI**: PySide6 (Qt for Python - Widgets: `QWidget`, `QLineEdit`, `QListWidget`, `QSystemTrayIcon`, `QDialog`).
* **IPC**: `QLocalServer` y `QLocalSocket` para instancia única y control remoto por CLI (`omnifloat --toggle`).
* **Sistemas Operativos**:
  * **Windows**: `ctypes` (`user32.dll`) para hotkeys Win32 (`RegisterHotKey`) y `winreg` para autoinicio en Registro (`Run`).
  * **Linux**: Freedesktop XDG (`.desktop` apps y autoinicio), temas de iconos (`QIcon.fromTheme`), detección de navegador XDG (`xdg-settings`), soporte opcional `pynput` en X11 y toggle IPC nativo para Wayland/X11.
* **Motor Matemático**: `ast` nativo + `operator` (evaluador AST seguro sin `eval()`).
* **Persistencia**: JSON (`~/.omnifloat_config.json`).
* **Testing**: `unittest` (módulo estándar).

---

## 2. Mapa de Componentes
| Archivo | Responsabilidad Principal |
|---|---|
| `main.py` | Entrada (`QApplication`), servidor IPC de instancia única (`QLocalServer`), inicialización de servicios y cableado de señales Qt. |
| `launcher_window.py` | UI del launcher flotante (`Frameless`, `AlwaysOnTop`, centrado superior), diseño glassmorphism frosted glass, filtros de eventos, persistencia de estado y renderizado dinámico (`ResultWidget`). |
| `indexer.py` | `SearchItem` y `AppIndexer`: indexación multiplataforma (.lnk/exe en Windows, .desktop/XDG en Linux, sistema y prefijos web `g `, `y `). |
| `math_evaluator.py` | `SafeMathEvaluator(ast.NodeVisitor)`: evaluación de expresiones aritméticas, funciones matemáticas permitidas y porcentajes (`%`, `of`, `de`, recargos y descuentos). |
| `hotkey_handler.py` | `GlobalHotkeyThread`: escucha Win32 `RegisterHotKey` en Windows, `pynput` o fallback IPC en Linux. |
| `settings_window.py` | Diálogo modal de configuración (`QDialog`): atajo, autoinicio (Registro Windows / XDG Linux), rutas indexadas, tema y opacidad. |
| `tray.py` | `SystemTrayManager`: icono procedural (`QPainter`) y menú contextual en la bandeja del sistema. |
| `icon_provider.py` | `IconManager`: resolución y caché de iconos nativos (Win32 API o Linux XDG Icon Themes) y detección del navegador por defecto. |
| `config.py` | `ConfigManager`: lectura/escritura de configuración local y autoinicio multiplataforma (`winreg` en Windows, XDG `.desktop` en Linux). |
| `styles.py` | Hojas de estilo QSS para temas `Dark` y `Light` con efecto glassmorphism. |
| `build.py` | Script de compilación automática a ejecutable independiente (Windows `.exe` o Linux ELF binario) vía PyInstaller. |
| `install.sh` / `uninstall.sh` | Scripts de instalación y desinstalación para Linux (iconos, .desktop y paquete pip). |
| `install_windows.bat` | Script de instalación por lotes para Windows. |
| `pyproject.toml` / `setup.py` | Configuración estándar de empaquetado pip/PEP 621 con entrypoints `omnifloat`. |
| `test_math_evaluator.py` | Pruebas unitarias para la validación y seguridad del evaluador matemático. |
| `test_icon_provider.py` | Pruebas unitarias para el gestor de iconos y detección de navegador por defecto. |
| `test_crossplatform.py` | Pruebas unitarias para compatibilidad cruzada (.desktop parsing, pynput formatting). |

---

## 3. Patrones de Diseño Utilizados
* **Observer / Signal-Slot (Qt)**: Comunicación reactiva entre hilos y componentes (`hotkey_triggered`, `settings_changed`).
* **Visitor Pattern**: `SafeMathEvaluator` hereda de `ast.NodeVisitor` para recorrer el árbol sintáctico de forma segura.
* **Worker Thread**: `GlobalHotkeyThread` desacoplado del hilo principal de UI.
* **Single-Instance IPC**: `QLocalServer` y `QLocalSocket` para comunicar múltiples llamadas CLI (`omnifloat --toggle`) con la instancia activa en segundo plano.
* **Separation of Concerns (SoC) / MVC**:
  * *Modelo*: `SearchItem`, `AppIndexer`, `ConfigManager`.
  * *Vista*: `LauncherWindow`, `ResultWidget`, `SettingsWindow`, `styles.py`.
  * *Controlador*: `main.py` coordina las dependencias.

---

## 4. Comandos Clave

```bash
# Instalación en modo desarrollo (Windows o Linux)
pip install -e .

# Ejecución directa
python main.py
# O vía comando registrado
omnifloat
# Toggle desde terminal o atajo de teclado del sistema
omnifloat --toggle

# Ejecución de pruebas unitarias
python -m unittest discover

# Compilación a binario independiente (Windows .exe o Linux ELF)
python build.py
```

---

## 5. Reglas y Convenciones para Agentes
1. **No usar `eval()`**: Toda evaluación matemática DEBE pasar por `SafeMathEvaluator` en `math_evaluator.py`.
2. **Compatibilidad SO cruzada**: Nunca importar `winreg` o invocar `os.startfile` sin verificar `sys.platform == "win32"`.
3. **Hilo de UI protegido**: Operaciones bloqueantes de SO o hotkeys deben ir en hilos dedicados o emitir eventos Qt (`Signal`).
4. **Ciclo de vida Qt**: `app.setQuitOnLastWindowClosed(False)` es mandatorio para mantener la app viva en la bandeja del sistema.
5. **Estilos**: Centralizar modificaciones visuales en `styles.py` manteniendo coherencia entre `DARK_STYLESHEET` y `LIGHT_STYLESHEET`.
