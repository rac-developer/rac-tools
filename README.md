# OmniFloat 🔍⚡

> Lanzador flotante minimalista estilo Spotlight / Raycast para **Windows** y **Linux**.

---

## 🌟 Características

* **Búsqueda Instantánea**: Indexación automática de aplicaciones nativas:
  * **Windows**: Accesos directos (`.lnk`), ejecutables (`.exe`), scripts (`.bat`, `.cmd`) y herramientas de sistema.
  * **Linux**: Aplicaciones de escritorio estándar Freedesktop (`.desktop`), Flatpak, Snap y herramientas de sistema.
* **Calculadora Matemática Segura**:
  * Evaluación en tiempo real basada en AST (sin `eval()` inseguro).
  * Soporte completo de porcentajes: `100 + 20%`, `500 - 15%`, `20% de 500`, `15% * 80`.
* **Búsqueda Web y Accesos Directos**:
  * Búsqueda en Google: `g <consulta>`
  * Búsqueda en YouTube: `y <consulta>`
  * Detección automática del navegador web predeterminado y su icono oficial (en Windows y Linux).
* **Diseño Glassmorphism Premium**:
  * Cápsula flotante estilo vidrio ahumado (*smoked glass*) con destellos físicos de luz especular.
  * Soporte de temas **Oscuro** y **Claro** con selector de opacidad.
* **Persistencia Inteligente**:
  * Si haces clic accidentalmente fuera de la ventana, tu búsqueda y sus resultados se mantienen al volver a abrirlo.
  * Selección inteligente para reemplazar o confirmar con <kbd>Enter</kbd>.
* **Bandeja del Sistema (System Tray)**: Permanece activo en segundo plano con bajo consumo de recursos.
* **Integración IPC de Instancia Única**: El comando `omnifloat --toggle` abre y cierra la instancia en segundo plano al instante.

---

## 🚀 Instalación y Uso

### 🐧 En Linux

#### Opción 1: Instalación rápida con script (Recomendada)
El script instala las dependencias, registra el icono en el tema de escritorio y crea el acceso en el menú de aplicaciones:
```bash
git clone https://github.com/rac-developer/rac-tools.git
cd rac-tools
bash install.sh
```

#### Opción 2: Instalación manual con pip
```bash
pip install -e .
```

#### ⌨️ Atajo de Teclado Global en Linux (GNOME, KDE, Wayland, i3, Sway)
En entornos modernos de Linux (especialmente Wayland), el método más rápido y estándar para abrir OmniFloat con cualquier tecla es:
1. Abre **Ajustes del Sistema** -> **Teclado** -> **Atajos de Teclado**.
2. Agrega un atajo personalizado:
   * **Nombre**: `OmniFloat`
   * **Comando**: `omnifloat --toggle`
   * **Atajo**: <kbd>Super</kbd> + <kbd>Espacio</kbd> (o <kbd>Alt</kbd> + <kbd>Espacio</kbd>).

---

### 🪟 En Windows

#### Opción 1: Instalador por lotes
Haz doble clic en `install_windows.bat` o ejecútalo en PowerShell / CMD:
```cmd
install_windows.bat
```

#### Opción 2: Instalación manual con pip
```powershell
pip install -e .
```

#### Opción 3: Ejecución directa
```powershell
python main.py
```
Por defecto, el atajo global registrado en Windows es <kbd>Alt</kbd> + <kbd>Espacio</kbd>.

---

## 🛠️ Compilación a Ejecutable Independiente (Standalone)

Puedes compilar OmniFloat en un único binario ejecutable que no requiere tener Python instalado:
* **En Windows**: Genera `dist/OmniFloat.exe`
* **En Linux**: Genera el binario ejecutable `dist/OmniFloat`

Simplemente ejecuta:
```bash
python build.py
```

---

## 🧪 Pruebas Unitarias

Para ejecutar la suite completa de pruebas unitarias en cualquier sistema operativo:
```bash
python -m unittest discover
```

---

## 🗑️ Desinstalación

* **Linux**: Ejecuta `bash uninstall.sh`
* **Windows**: Ejecuta `pip uninstall omnifloat`
