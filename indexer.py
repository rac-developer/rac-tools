import os
import sys
import glob
import subprocess
import shutil
import re

def parse_desktop_file(file_path: str):
    """
    Parses a Freedesktop .desktop file extracting application metadata.
    Returns (name, comment, exec_cmd, icon) or None if not a valid launchable application.
    """
    try:
        name = None
        comment = None
        generic_name = None
        exec_cmd = None
        icon = None
        is_app = False
        no_display = False
        hidden = False
        in_desktop_entry = False

        with open(file_path, "r", encoding="utf-8", errors="ignore") as f:
            for line in f:
                line = line.strip()
                if line == "[Desktop Entry]":
                    in_desktop_entry = True
                    continue
                elif line.startswith("[") and line.endswith("]"):
                    in_desktop_entry = False
                    continue

                if not in_desktop_entry or "=" not in line:
                    continue

                key, val = line.split("=", 1)
                key = key.strip()
                val = val.strip()

                if key == "Type" and val == "Application":
                    is_app = True
                elif key == "Name" and not name:
                    name = val
                elif key == "Comment" and not comment:
                    comment = val
                elif key == "GenericName" and not generic_name:
                    generic_name = val
                elif key == "Exec" and not exec_cmd:
                    exec_cmd = val
                elif key == "Icon" and not icon:
                    icon = val
                elif key == "NoDisplay" and val.lower() == "true":
                    no_display = True
                elif key == "Hidden" and val.lower() == "true":
                    hidden = True

        if is_app and not no_display and not hidden and name and exec_cmd:
            clean_exec = re.sub(r"%[a-zA-Z]", "", exec_cmd).strip()
            subtitle = comment or generic_name or clean_exec
            return name, subtitle, clean_exec, icon
    except Exception:
        pass
    return None

class SearchItem:
    def __init__(self, title: str, subtitle: str, item_type: str, action: str, icon_path: str = None):
        self.title = title
        self.subtitle = subtitle
        self.item_type = item_type  # 'app', 'math', 'web', 'cmd'
        self.action = action        # File path, URL, command string, or math result
        self.icon_path = icon_path

    def execute(self):
        if self.item_type == 'app':
            if sys.platform == "win32":
                try:
                    os.startfile(self.action)
                except Exception as e:
                    subprocess.Popen(self.action, shell=True)
            else:
                # Linux execution
                if self.action.endswith(".desktop"):
                    launched = False
                    for launcher in ["gio", "gtk-launch"]:
                        if shutil.which(launcher):
                            cmd = [launcher, "launch", self.action] if launcher == "gio" else [launcher, os.path.basename(self.action)]
                            try:
                                subprocess.Popen(cmd)
                                launched = True
                                break
                            except Exception:
                                pass
                    if not launched:
                        parsed = parse_desktop_file(self.action)
                        if parsed and parsed[2]:
                            subprocess.Popen(parsed[2], shell=True)
                        else:
                            subprocess.Popen(["xdg-open", self.action])
                else:
                    try:
                        subprocess.Popen(["xdg-open", self.action])
                    except Exception:
                        subprocess.Popen(self.action, shell=True)
        elif self.item_type == 'web':
            import webbrowser
            webbrowser.open(self.action)
        elif self.item_type == 'cmd':
            try:
                subprocess.Popen(self.action, shell=True)
            except Exception as e:
                print(f"[SearchItem] Error executing command {self.action}: {e}")


class AppIndexer:
    def __init__(self, config_manager):
        self.config_manager = config_manager
        self.indexed_items = []
        self.reindex()

    def reindex(self):
        items = []
        search_paths = self.config_manager.get("search_paths", [])

        # System Tools based on OS
        if sys.platform == "win32":
            system_tools = [
                ("Bloc de notas (Notepad)", "notepad.exe", "notepad.exe"),
                ("Símbolo del sistema (CMD)", "cmd.exe", "cmd.exe"),
                ("PowerShell", "powershell.exe", "powershell.exe"),
                ("Calculadora", "calc.exe", "calc.exe"),
                ("Explorador de archivos", "explorer.exe", "explorer.exe"),
                ("Panel de control", "control.exe", "control.exe"),
                ("Task Manager", "taskmgr.exe", "taskmgr.exe"),
            ]
            for title, subtitle, target in system_tools:
                items.append(SearchItem(title, f"Herramienta de sistema: {subtitle}", "app", target))
        else:
            # Linux built-in system tools
            linux_tools = [
                ("Terminal", "Emulador de terminal", "x-terminal-emulator"),
                ("Archivos", "Administrador de archivos", "xdg-open ."),
                ("Calculadora", "Calculadora de sistema", "gnome-calculator"),
                ("Monitor de sistema", "Monitor de tareas y procesos", "gnome-system-monitor"),
                ("Editor de texto", "Editor de texto de sistema", "gedit"),
                ("Ajustes", "Configuración del sistema", "gnome-control-center"),
            ]
            for title, subtitle, target in linux_tools:
                first_token = target.split()[0]
                if shutil.which(first_token):
                    items.append(SearchItem(title, f"Herramienta de sistema: {subtitle}", "cmd", target))

        # Index directories
        seen_paths = set()
        for folder in search_paths:
            if not os.path.exists(folder):
                continue
            for root, _, files in os.walk(folder):
                for file in files:
                    full_path = os.path.join(root, file)
                    if full_path in seen_paths:
                        continue

                    if sys.platform == "win32":
                        if file.lower().endswith(('.lnk', '.exe', '.bat', '.cmd')):
                            seen_paths.add(full_path)
                            name = os.path.splitext(file)[0]
                            title = name.replace("- Shortcut", "").replace(" - Acceso directo", "").strip()
                            subtitle = full_path
                            items.append(SearchItem(title, subtitle, "app", full_path))
                    else:
                        # Linux: index .desktop application files
                        if file.endswith(".desktop"):
                            seen_paths.add(full_path)
                            parsed = parse_desktop_file(full_path)
                            if parsed:
                                name, subtitle, exec_cmd, icon = parsed
                                items.append(SearchItem(name, subtitle, "app", full_path, icon_path=icon))
                        elif os.access(full_path, os.X_OK) and not os.path.isdir(full_path):
                            seen_paths.add(full_path)
                            items.append(SearchItem(file, full_path, "app", full_path))

        self.indexed_items = items

    def search(self, query: str):
        cleaned = query.strip()
        if not cleaned:
            return []

        results = []

        # 1. Direct Web / URL match
        if cleaned.startswith(("http://", "https://", "www.")):
            url = cleaned if cleaned.startswith("http") else f"https://{cleaned}"
            results.append(SearchItem(f"Abrir enlace: {cleaned}", url, "web", url))

        # 2. Google / Search prefix 'g '
        if cleaned.lower().startswith("g ") and len(cleaned) > 2:
            search_query = cleaned[2:].strip()
            url = f"https://www.google.com/search?q={search_query}"
            results.append(SearchItem(f"Buscar en Google: '{search_query}'", url, "web", url))

        # 3. YouTube search prefix 'y '
        if cleaned.lower().startswith("y ") and len(cleaned) > 2:
            search_query = cleaned[2:].strip()
            url = f"https://www.youtube.com/results?search_query={search_query}"
            results.append(SearchItem(f"Buscar en YouTube: '{search_query}'", url, "web", url))

        # 4. App / File fuzzy matching
        q_lower = cleaned.lower()
        exact_matches = []
        startswith_matches = []
        contains_matches = []

        for item in self.indexed_items:
            t_lower = item.title.lower()
            if t_lower == q_lower:
                exact_matches.append(item)
            elif t_lower.startswith(q_lower):
                startswith_matches.append(item)
            elif q_lower in t_lower:
                contains_matches.append(item)

        results.extend(exact_matches + startswith_matches + contains_matches)

        # Fallback Google search option if no direct app matches
        if not results:
            url = f"https://www.google.com/search?q={cleaned}"
            results.append(SearchItem(f"Buscar en Google: '{cleaned}'", url, "web", url))

        return results[:10]  # Limit top results to 10
