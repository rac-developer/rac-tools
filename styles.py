DARK_STYLESHEET = """
QWidget#ContainerWidget {
    background-color: rgba(26, 27, 35, 235);
    border: 1px solid rgba(255, 255, 255, 0.12);
    border-radius: 16px;
}

QLineEdit#SearchField {
    background-color: rgba(40, 42, 54, 180);
    color: #F8F8F2;
    border: 1px solid rgba(255, 255, 255, 0.15);
    border-radius: 12px;
    padding: 12px 16px;
    font-size: 18px;
    font-family: 'Segoe UI', sans-serif;
    selection-background-color: #BD93F9;
}

QLineEdit#SearchField:focus {
    border: 1px solid #BD93F9;
    background-color: rgba(40, 42, 54, 220);
}

QListWidget#ResultsList {
    background: transparent;
    border: none;
    outline: none;
    padding: 4px;
}

QListWidget#ResultsList::item {
    background: transparent;
    border-radius: 8px;
    padding: 8px 12px;
    margin-bottom: 2px;
}

QListWidget#ResultsList::item:selected, QListWidget#ResultsList::item:hover {
    background-color: rgba(189, 147, 249, 0.25);
    border: 1px solid rgba(189, 147, 249, 0.5);
}

QLabel#ItemTitle {
    color: #F8F8F2;
    font-size: 15px;
    font-weight: 600;
    font-family: 'Segoe UI', sans-serif;
}

QLabel#MathResultTitle {
    color: #50FA7B;
    font-size: 18px;
    font-weight: bold;
    font-family: 'Segoe UI', sans-serif;
}

QLabel#ItemSubtitle {
    color: #8BE9FD;
    font-size: 12px;
    font-family: 'Segoe UI', sans-serif;
}

QLabel#ItemTag {
    color: #FF79C6;
    background-color: rgba(255, 121, 198, 0.15);
    border: 1px solid rgba(255, 121, 198, 0.3);
    border-radius: 4px;
    padding: 2px 6px;
    font-size: 10px;
    font-weight: bold;
}
"""

LIGHT_STYLESHEET = """
QWidget#ContainerWidget {
    background-color: rgba(248, 249, 250, 240);
    border: 1px solid rgba(0, 0, 0, 0.12);
    border-radius: 16px;
}

QLineEdit#SearchField {
    background-color: rgba(255, 255, 255, 220);
    color: #212529;
    border: 1px solid rgba(0, 0, 0, 0.15);
    border-radius: 12px;
    padding: 12px 16px;
    font-size: 18px;
    font-family: 'Segoe UI', sans-serif;
    selection-background-color: #6200EE;
}

QLineEdit#SearchField:focus {
    border: 1px solid #6200EE;
    background-color: #FFFFFF;
}

QListWidget#ResultsList {
    background: transparent;
    border: none;
    outline: none;
    padding: 4px;
}

QListWidget#ResultsList::item {
    background: transparent;
    border-radius: 8px;
    padding: 8px 12px;
    margin-bottom: 2px;
}

QListWidget#ResultsList::item:selected, QListWidget#ResultsList::item:hover {
    background-color: rgba(98, 0, 238, 0.12);
    border: 1px solid rgba(98, 0, 238, 0.3);
}

QLabel#ItemTitle {
    color: #212529;
    font-size: 15px;
    font-weight: 600;
    font-family: 'Segoe UI', sans-serif;
}

QLabel#MathResultTitle {
    color: #2E7D32;
    font-size: 18px;
    font-weight: bold;
    font-family: 'Segoe UI', sans-serif;
}

QLabel#ItemSubtitle {
    color: #495057;
    font-size: 12px;
    font-family: 'Segoe UI', sans-serif;
}

QLabel#ItemTag {
    color: #6200EE;
    background-color: rgba(98, 0, 238, 0.1);
    border: 1px solid rgba(98, 0, 238, 0.25);
    border-radius: 4px;
    padding: 2px 6px;
    font-size: 10px;
    font-weight: bold;
}
"""
