DARK_STYLESHEET = """
QWidget#ContainerWidget {
    background: qlineargradient(x1:0, y1:0, x2:0, y2:1,
        stop:0 rgba(60, 64, 78, 255),
        stop:0.03 rgba(36, 38, 48, 255),
        stop:0.25 rgba(22, 23, 29, 255),
        stop:1 rgba(13, 14, 17, 255)
    );
    border: 1px solid rgba(255, 255, 255, 0.18);
    border-top: 1px solid rgba(255, 255, 255, 0.45);
    border-bottom: 1px solid rgba(255, 255, 255, 0.08);
    border-radius: 16px;
}

QLineEdit#SearchField {
    background: transparent;
    color: #FFFFFF;
    border: none;
    outline: none;
    padding: 0px 4px;
    font-size: 17px;
    font-family: 'Segoe UI', -apple-system, sans-serif;
    selection-background-color: rgba(255, 255, 255, 0.25);
}

QLineEdit#SearchField:focus {
    background: transparent;
    border: none;
    outline: none;
}

QFrame#SearchDivider {
    background-color: rgba(255, 255, 255, 0.08);
    border: none;
}

QListWidget#ResultsList {
    background: transparent;
    border: none;
    outline: none;
    padding: 2px 0px;
}

QListWidget#ResultsList::item {
    background: transparent;
    border-radius: 8px;
    padding: 2px 4px;
    margin-bottom: 2px;
}

QListWidget#ResultsList::item:selected, QListWidget#ResultsList::item:hover {
    background-color: rgba(255, 255, 255, 0.08);
    border: 1px solid rgba(255, 255, 255, 0.12);
}

QLabel#ItemTitle {
    color: #F3F3F3;
    font-size: 14px;
    font-weight: 600;
    font-family: 'Segoe UI', -apple-system, sans-serif;
}

QLabel#MathResultTitle {
    color: #FFFFFF;
    font-size: 16px;
    font-weight: bold;
    font-family: 'Segoe UI', -apple-system, sans-serif;
}

QLabel#ItemSubtitle {
    color: #8E8E93;
    font-size: 12px;
    font-family: 'Segoe UI', -apple-system, sans-serif;
}

QLabel#ItemTag {
    color: #A1A1AA;
    background-color: rgba(255, 255, 255, 0.06);
    border: 1px solid rgba(255, 255, 255, 0.10);
    border-radius: 4px;
    padding: 2px 6px;
    font-size: 10px;
    font-weight: 600;
    font-family: 'Segoe UI', -apple-system, sans-serif;
}

QScrollBar:vertical {
    border: none;
    background: transparent;
    width: 6px;
    margin: 2px 0 2px 0;
}

QScrollBar::handle:vertical {
    background: rgba(255, 255, 255, 0.15);
    min-height: 20px;
    border-radius: 3px;
}

QScrollBar::handle:vertical:hover {
    background: rgba(255, 255, 255, 0.30);
}

QScrollBar::add-line:vertical, QScrollBar::sub-line:vertical {
    height: 0px;
}

QScrollBar::add-page:vertical, QScrollBar::sub-page:vertical {
    background: none;
}
"""

LIGHT_STYLESHEET = """
QWidget#ContainerWidget {
    background: qlineargradient(x1:0, y1:0, x2:0, y2:1,
        stop:0 rgba(255, 255, 255, 255),
        stop:0.03 rgba(248, 250, 253, 255),
        stop:0.25 rgba(240, 242, 247, 255),
        stop:1 rgba(230, 233, 238, 255)
    );
    border: 1px solid rgba(0, 0, 0, 0.14);
    border-top: 1px solid rgba(255, 255, 255, 0.90);
    border-bottom: 1px solid rgba(0, 0, 0, 0.08);
    border-radius: 16px;
}

QLineEdit#SearchField {
    background: transparent;
    color: #18181B;
    border: none;
    outline: none;
    padding: 0px 4px;
    font-size: 17px;
    font-family: 'Segoe UI', -apple-system, sans-serif;
    selection-background-color: rgba(0, 0, 0, 0.15);
}

QLineEdit#SearchField:focus {
    background: transparent;
    border: none;
    outline: none;
}

QFrame#SearchDivider {
    background-color: rgba(0, 0, 0, 0.08);
    border: none;
}

QListWidget#ResultsList {
    background: transparent;
    border: none;
    outline: none;
    padding: 2px 0px;
}

QListWidget#ResultsList::item {
    background: transparent;
    border-radius: 8px;
    padding: 2px 4px;
    margin-bottom: 2px;
}

QListWidget#ResultsList::item:selected, QListWidget#ResultsList::item:hover {
    background-color: rgba(0, 0, 0, 0.06);
    border: 1px solid rgba(0, 0, 0, 0.10);
}

QLabel#ItemTitle {
    color: #18181B;
    font-size: 14px;
    font-weight: 600;
    font-family: 'Segoe UI', -apple-system, sans-serif;
}

QLabel#MathResultTitle {
    color: #09090B;
    font-size: 16px;
    font-weight: bold;
    font-family: 'Segoe UI', -apple-system, sans-serif;
}

QLabel#ItemSubtitle {
    color: #71717A;
    font-size: 12px;
    font-family: 'Segoe UI', -apple-system, sans-serif;
}

QLabel#ItemTag {
    color: #52525B;
    background-color: rgba(0, 0, 0, 0.05);
    border: 1px solid rgba(0, 0, 0, 0.10);
    border-radius: 4px;
    padding: 2px 6px;
    font-size: 10px;
    font-weight: 600;
    font-family: 'Segoe UI', -apple-system, sans-serif;
}

QScrollBar:vertical {
    border: none;
    background: transparent;
    width: 6px;
    margin: 2px 0 2px 0;
}

QScrollBar::handle:vertical {
    background: rgba(0, 0, 0, 0.15);
    min-height: 20px;
    border-radius: 3px;
}

QScrollBar::handle:vertical:hover {
    background: rgba(0, 0, 0, 0.30);
}

QScrollBar::add-line:vertical, QScrollBar::sub-line:vertical {
    height: 0px;
}

QScrollBar::add-page:vertical, QScrollBar::sub-page:vertical {
    background: none;
}
"""
