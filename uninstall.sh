#!/usr/bin/env bash
# ==============================================================================
# OmniFloat - Script de Desinstalación para Linux
# ==============================================================================
set -e

echo "Desinstalando OmniFloat..."

# Eliminar accesos directos e iconos
rm -f "$HOME/.local/share/applications/omnifloat.desktop"
rm -f "$HOME/.local/share/icons/hicolor/scalable/apps/omnifloat.svg"
rm -f "$HOME/.local/share/icons/hicolor/256x256/apps/omnifloat.png"
rm -f "$HOME/.config/autostart/omnifloat.desktop"

# Desinstalar paquete pip
python3 -m pip uninstall -y omnifloat || true

if command -v update-desktop-database &> /dev/null; then
    update-desktop-database "$HOME/.local/share/applications" 2>/dev/null || true
fi

echo "OmniFloat ha sido desinstalado de tu sistema."
