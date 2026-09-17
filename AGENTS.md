# AGENTS.md - OmniFloat

> Guía ultraconcisa de arquitectura, patrones y comandos para agentes de IA en OmniFloat.

---

## 1. Propósito y Stack Tecnológico
* **Tipo**: Lanzador flotante minimalista para Windows (estilo Spotlight / Raycast).
* **Lenguaje**: Python 3.13+
* **GUI**: PySide6 (Qt for Python - Widgets: `QWidget`, `QLineEdit`, `QListWidget`, `QSystemTrayIcon`, `QDialog`).
* **Win32 API**: `ctypes` (`user32.dll`, `kernel32.dll`) para registro global de hotkeys (`RegisterHotKey`) y `winreg` para persistencia en inicio de Windows.
* **Motor Matemático**: `ast` nativo + `operator` (evaluador AST seguro sin `eval()`).
* **Persistencia**: JSON (`~/.omnifloat_config.json`).
* **Testing**: `unittest` (módulo estándar).

---

## 2. Mapa de Componentes
| Archivo | Responsabilidad Principal |
|---|---|
| `main.py` | Entrada (`QApplication`), inicialización de servicios y cableado de señales Qt. |
| `launcher_window.py` | UI del launcher flotante (`Frameless`, `AlwaysOnTop`, centrado superior), diseño glassmorphism frosted glass, filtros de eventos y renderizado dinámico (`ResultWidget`). |
| `indexer.py` | `SearchItem` (modelo de item) y `AppIndexer` (indexación de accesos directos `.lnk`/`.exe`/`.bat`/`.cmd`, sistema y prefijos web `g `, `y `). |
| `math_evaluator.py` | `SafeMathEvaluator(ast.NodeVisitor)`: evaluación de expresiones aritméticas, funciones matemáticas permitidas y porcentajes (`%`, `of`, `de`, recargos y descuentos). |
| `hotkey_handler.py` | `GlobalHotkeyThread(QThread)`: escucha hotkeys Win32 en bucle `GetMessageW` desacoplado del hilo principal de UI. |
| `settings_window.py` | Diálogo modal de configuración (`QDialog`): atajo, autoinicio, rutas indexadas, tema y opacidad. |
| `tray.py` | `SystemTrayManager`: icono procedural (`QPainter`) y menú contextual en la bandeja del sistema. |
| `icon_provider.py` | `IconManager`: resolución y caché de iconos nativos Win32 y detección del navegador por defecto en registro. |
| `config.py` | `ConfigManager`: lectura/escritura de configuración local y clave de registro de autoinicio (`Run`). |
| `styles.py` | Hojas de estilo QSS para temas `Dark` y `Light`. |
| `test_math_evaluator.py` | Pruebas unitarias para la validación y seguridad del evaluador matemático. |
| `test_icon_provider.py` | Pruebas unitarias para el gestor de iconos y detección de navegador por defecto. |

---

## 3. Patrones de Diseño Utilizados
* **Observer / Signal-Slot (Qt)**: Comunicación reactiva entre hilos y componentes (`hotkey_triggered`, `settings_changed`).
* **Visitor Pattern**: `SafeMathEvaluator` hereda de `ast.NodeVisitor` para recorrer el árbol sintáctico de forma segura.
* **Worker Thread**: `GlobalHotkeyThread` corre en un `QThread` secundario para no bloquear el bucle de eventos principal de Qt con `GetMessageW`.
* **Separation of Concerns (SoC) / MVC**:
  * *Modelo*: `SearchItem`, `AppIndexer`, `ConfigManager`.
  * *Vista*: `LauncherWindow`, `ResultWidget`, `SettingsWindow`, `styles.py`.
  * *Controlador*: `main.py` coordina las dependencias.

---

## 4. Comandos Clave

```powershell
# Ejecución directa
python main.py

# Ejecución de pruebas unitarias
python test_math_evaluator.py
# o bien
python -m unittest discover

# Compilación a ejecutable (PyInstaller sugerido)
pyinstaller --noconsole --onefile main.py --name OmniFloat
```

---

## 5. Reglas y Convenciones para Agentes
1. **No usar `eval()`**: Toda evaluación matemática DEBE pasar por `SafeMathEvaluator` en `math_evaluator.py`.
2. **Hilo de UI protegido**: Operaciones bloqueantes de SO o hotkeys deben ir en hilos dedicados o emitir eventos Qt (`Signal`).
3. **Persistencia limpia**: Todo ajuste nuevo debe registrarse en `DEFAULT_CONFIG` (`config.py`) y exponerse en `SettingsWindow`.
4. **Ciclo de vida Qt**: `app.setQuitOnLastWindowClosed(False)` es mandatorio para mantener la app viva en la bandeja del sistema.
5. **Estilos**: Centralizar modificaciones visuales en `styles.py` manteniendo coherencia entre `DARK_STYLESHEET` y `LIGHT_STYLESHEET`.
