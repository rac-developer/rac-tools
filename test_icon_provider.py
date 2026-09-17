import unittest
import sys
import os
from PySide6.QtWidgets import QApplication
from indexer import SearchItem
from icon_provider import IconManager

class TestIconProvider(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        if not QApplication.instance():
            cls.app = QApplication(sys.argv)
        else:
            cls.app = QApplication.instance()

    def test_singleton_instance(self):
        m1 = IconManager.instance()
        m2 = IconManager.instance()
        self.assertIs(m1, m2)

    def test_default_browser_icon(self):
        mgr = IconManager.instance()
        icon = mgr.get_default_browser_icon()
        self.assertFalse(icon.isNull())
        pixmap = icon.pixmap(32, 32)
        self.assertFalse(pixmap.isNull())

    def test_math_icon(self):
        mgr = IconManager.instance()
        icon = mgr.get_math_icon()
        self.assertFalse(icon.isNull())
        pixmap = icon.pixmap(32, 32)
        self.assertFalse(pixmap.isNull())

    def test_app_and_web_item_icons(self):
        mgr = IconManager.instance()
        web_item = SearchItem("Google Search", "https://google.com", "web", "https://google.com")
        web_icon = mgr.get_icon(web_item)
        self.assertFalse(web_icon.isNull())

        app_item = SearchItem("Notepad", "notepad.exe", "app", "notepad.exe")
        app_icon = mgr.get_icon(app_item)
        self.assertFalse(app_icon.isNull())

        math_item = SearchItem("Calc", "42", "math", "42")
        math_icon = mgr.get_icon(math_item)
        self.assertFalse(math_icon.isNull())

if __name__ == "__main__":
    unittest.main()
