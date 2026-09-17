"""
OmniFloat - Cross-Platform Shortcut Creator
Creates desktop and start menu shortcuts for OmniFloat on Windows and Linux.
"""
import os
import sys
import shutil
import subprocess

def get_desktop_folder() -> str:
    """Returns the user's active desktop directory across Windows (including OneDrive) and Linux (XDG)."""
    if sys.platform == "win32":
        try:
            import winreg
            with winreg.OpenKey(winreg.HKEY_CURRENT_USER, r"Software\Microsoft\Windows\CurrentVersion\Explorer\User Shell Folders") as key:
                val, _ = winreg.QueryValueEx(key, "Desktop")
                path = os.path.expandvars(val)
                if os.path.exists(path):
                    return path
        except Exception:
            pass
        onedrive_desktop = os.path.join(os.path.expanduser("~"), "OneDrive", "Desktop")
        if os.path.exists(onedrive_desktop):
            return onedrive_desktop
        return os.path.join(os.path.expanduser("~"), "Desktop")
    else:
        # Linux XDG Desktop
        try:
            out = subprocess.check_output(["xdg-user-dir", "DESKTOP"], text=True, stderr=subprocess.DEVNULL).strip()
            if out and os.path.exists(out):
                return out
        except Exception:
            pass
        fallback = os.path.expanduser("~/Desktop")
        if os.path.exists(fallback):
            return fallback
        return os.path.expanduser("~")

def create_windows_shortcuts():
    script_dir = os.path.abspath(os.path.dirname(__file__))
    main_py = os.path.join(script_dir, "main.py")
    pythonw = shutil.which("pythonw") or os.path.join(os.path.dirname(sys.executable), "pythonw.exe")
    icon_ico = os.path.join(script_dir, "assets", "icon.ico")

    desktop = get_desktop_folder()
    start_menu = os.path.join(os.environ.get("APPDATA", ""), r"Microsoft\Windows\Start Menu\Programs")

    targets = [
        ("Escritorio", os.path.join(desktop, "OmniFloat.lnk")),
        ("Menú Inicio", os.path.join(start_menu, "OmniFloat.lnk")),
        ("Carpeta del programa", os.path.join(script_dir, "OmniFloat.lnk"))
    ]

    created = []
    for label, lnk_path in targets:
        try:
            ps_cmd = (
                f'$WshShell = New-Object -ComObject WScript.Shell; '
                f'$Shortcut = $WshShell.CreateShortcut("{lnk_path}"); '
                f'$Shortcut.TargetPath = "{pythonw}"; '
                f'$Shortcut.Arguments = \'"{main_py}"\'; '
                f'$Shortcut.WorkingDirectory = "{script_dir}"; '
                f'$Shortcut.IconLocation = "{icon_ico}, 0"; '
                f'$Shortcut.Description = "OmniFloat - Lanzador Flotante Minimalista"; '
                f'$Shortcut.Save()'
            )
            subprocess.run(["powershell", "-NoProfile", "-Command", ps_cmd], check=True, capture_output=True)
            print(f"[OK] Acceso directo creado en {label}: {lnk_path}")
            created.append(lnk_path)
        except Exception as e:
            print(f"[ERROR] No se pudo crear acceso en {label}: {e}")
    return created

def create_linux_shortcuts():
    script_dir = os.path.abspath(os.path.dirname(__file__))
    desktop_folder = get_desktop_folder()
    desktop_file = os.path.join(desktop_folder, "omnifloat.desktop")

    bin_path = shutil.which("omnifloat") or f'"{sys.executable}" "{os.path.join(script_dir, "main.py")}"'
    icon_path = os.path.join(script_dir, "assets", "icon.png")

    content = f"""[Desktop Entry]
Version=1.0
Type=Application
Name=OmniFloat
GenericName=Lanzador Flotante
Comment=Lanzador flotante minimalista estilo Spotlight / Raycast
Exec={bin_path}
Icon={icon_path}
Terminal=false
Categories=Utility;System;DesktopUtility;
StartupNotify=false
Keywords=launcher;spotlight;raycast;calculator;search;float;
"""
    created = []
    try:
        with open(desktop_file, "w", encoding="utf-8") as f:
            f.write(content)
        os.chmod(desktop_file, 0o755)
        # Mark as trusted on modern GNOME/KDE if gio is available
        if shutil.which("gio"):
            try:
                subprocess.run(["gio", "set", desktop_file, "metadata::trusted", "true"], capture_output=True)
            except Exception:
                pass
        print(f"[OK] Acceso directo creado en Escritorio: {desktop_file}")
        created.append(desktop_file)
    except Exception as e:
        print(f"[ERROR] No se pudo crear acceso directo en Linux: {e}")
    return created

def create_desktop_shortcut():
    """Universal function to create desktop shortcut according to OS."""
    if sys.platform == "win32":
        return create_windows_shortcuts()
    else:
        return create_linux_shortcuts()

if __name__ == "__main__":
    create_desktop_shortcut()
