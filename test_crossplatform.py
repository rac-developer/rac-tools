import unittest
import os
import sys
import tempfile
from indexer import parse_desktop_file, SearchItem
from config import ConfigManager
from hotkey_handler import _format_pynput_hotkey

class TestCrossPlatform(unittest.TestCase):
    def test_parse_desktop_file(self):
        content = """[Desktop Entry]
Version=1.0
Type=Application
Name=Test Editor
GenericName=Text Editor
Comment=Edit code and text
Exec=/usr/bin/test-editor %F --new-window
Icon=test-editor-icon
Terminal=false
Categories=Development;
"""
        with tempfile.NamedTemporaryFile(mode="w", suffix=".desktop", delete=False, encoding="utf-8") as f:
            f.write(content)
            temp_path = f.name

        try:
            parsed = parse_desktop_file(temp_path)
            self.assertIsNotNone(parsed)
            name, subtitle, exec_cmd, icon = parsed
            self.assertEqual(name, "Test Editor")
            self.assertEqual(subtitle, "Edit code and text")
            self.assertEqual(exec_cmd, "/usr/bin/test-editor  --new-window")
            self.assertEqual(icon, "test-editor-icon")
        finally:
            if os.path.exists(temp_path):
                os.remove(temp_path)

    def test_parse_desktop_file_nodisplay_skipped(self):
        content = """[Desktop Entry]
Type=Application
Name=Hidden App
Exec=hidden-app
NoDisplay=true
"""
        with tempfile.NamedTemporaryFile(mode="w", suffix=".desktop", delete=False, encoding="utf-8") as f:
            f.write(content)
            temp_path = f.name

        try:
            parsed = parse_desktop_file(temp_path)
            self.assertIsNone(parsed)
        finally:
            if os.path.exists(temp_path):
                os.remove(temp_path)

    def test_format_pynput_hotkey(self):
        from hotkey_handler import _format_pynput_hotkey
        # Check that helper formats keys properly for Linux
        formatted = _format_pynput_hotkey("Alt+Space")
        self.assertEqual(formatted, "<alt>+<space>")
        formatted_complex = _format_pynput_hotkey("Ctrl+Shift+Space")
        self.assertEqual(formatted_complex, "<ctrl>+<shift>+<space>")

if __name__ == "__main__":
    unittest.main()
