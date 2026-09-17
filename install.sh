#!/usr/bin/env bash
# ==============================================================================
# OmniFloat - Script de Instalación para Linux
# ==============================================================================
set -e

echo "========================================="
echo "   Instalando OmniFloat en Linux"
echo "========================================="

# 1. Comprobar Python 3
if ! command -v python3 &> /dev/null; then
    echo "Error: Python 3 no está instalado. Por favor instálalo primero."
    exit 1
fi

# 2. Instalar el paquete y dependencias vía pip
echo "-> Instalando paquete OmniFloat y dependencias (PySide6)..."
python3 -m pip install --upgrade pip
python3 -m pip install . --user

# 3. Directorios XDG del usuario
APPS_DIR="$HOME/.local/share/applications"
ICON_DIR_SVG="$HOME/.local/share/icons/hicolor/scalable/apps"
ICON_DIR_PNG="$HOME/.local/share/icons/hicolor/256x256/apps"

mkdir -p "$APPS_DIR"
mkdir -p "$ICON_DIR_SVG"
mkdir -p "$ICON_DIR_PNG"

# 4. Instalar Iconos
echo "-> Instalando iconos del sistema..."
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
cp "$SCRIPT_DIR/assets/icon.svg" "$ICON_DIR_SVG/omnifloat.svg"
cp "$SCRIPT_DIR/assets/icon.png" "$ICON_DIR_PNG/omnifloat.png"

# 5. Instalar Acceso Directo de Escritorio (.desktop)
echo "-> Registrando acceso en el menú de aplicaciones..."
BIN_PATH="$(python3 -c 'import shutil, sys; print(shutil.which("omnifloat") or sys.executable + " -m main")')"

cat <<EOF > "$APPS_DIR/omnifloat.desktop"
[Desktop Entry]
Version=1.0
Type=Application
Name=OmniFloat
GenericName=Lanzador Flotante
Comment=Lanzador flotante minimalista estilo Spotlight / Raycast
Exec=$BIN_PATH
Icon=omnifloat
Terminal=false
Categories=Utility;System;DesktopUtility;
StartupNotify=false
Keywords=launcher;spotlight;raycast;calculator;search;float;
EOF

chmod +x "$APPS_DIR/omnifloat.desktop"

# 5.1 Crear acceso directo en el Escritorio
DESKTOP_DIR="$(xdg-user-dir DESKTOP 2>/dev/null || echo "$HOME/Desktop")"
if [ -d "$DESKTOP_DIR" ]; then
    echo "-> Creando acceso directo en tu Escritorio ($DESKTOP_DIR)..."
    cp "$APPS_DIR/omnifloat.desktop" "$DESKTOP_DIR/omnifloat.desktop"
    chmod +x "$DESKTOP_DIR/omnifloat.desktop"
    if command -v gio &> /dev/null; then
        gio set "$DESKTOP_DIR/omnifloat.desktop" metadata::trusted true 2>/dev/null || true
    fi
fi

# 6. Actualizar bases de datos de escritorio e iconos
if command -v update-desktop-database &> /dev/null; then
    update-desktop-database "$APPS_DIR" 2>/dev/null || true
fi
if command -v gtk-update-icon-cache &> /dev/null; then
    gtk-update-icon-cache -f -t "$HOME/.local/share/icons/hicolor" 2>/dev/null || true
fi

echo ""
echo "=================================================================="
echo "   ¡OmniFloat instalado con éxito en Linux!"
echo "=================================================================="
echo "Puedes iniciar OmniFloat desde:"
echo "  - Tu menú de aplicaciones (busca 'OmniFloat')"
echo "  - La terminal ejecutando: omnifloat"
echo ""
echo "TIP PARA ATAJO GLOBAL (GNOME, KDE, Wayland, i3):"
echo "  Ve a Configuración -> Teclado -> Atajos Personalizados"
echo "  Crea un atajo (ej. Super+Espacio o Alt+Espacio) con el comando:"
echo "    omnifloat --toggle"
echo "=================================================================="
