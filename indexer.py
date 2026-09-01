import os
import sys
import glob
import subprocess

class SearchItem:
    def __init__(self, title: str, subtitle: str, item_type: str, action: str, icon_path: str = None):
        self.title = title
        self.subtitle = subtitle
        self.item_type = item_type  # 'app', 'math', 'web', 'cmd'
        self.action = action        # File path, URL, command string, or math result
        self.icon_path = icon_path

    def execute(self):
        if self.item_type == 'app':
            try:
                os.startfile(self.action)
            except Exception as e:
                print(f"[SearchItem] Error starting app {self.action}: {e}")
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

        # Add built-in Windows system tools
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

        # Index directories
        seen_paths = set()
        for folder in search_paths:
            if not os.path.exists(folder):
                continue
            for root, _, files in os.walk(folder):
                for file in files:
                    if file.lower().endswith(('.lnk', '.exe', '.bat', '.cmd')):
                        full_path = os.path.join(root, file)
                        if full_path in seen_paths:
                            continue
                        seen_paths.add(full_path)
                        
                        name = os.path.splitext(file)[0]
                        # Clean name formatting for shortcuts
                        title = name.replace("- Shortcut", "").replace(" - Acceso directo", "").strip()
                        subtitle = full_path
                        items.append(SearchItem(title, subtitle, "app", full_path))

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
