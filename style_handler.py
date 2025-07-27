# style_handler.py
from PyQt5.QtWidgets import QApplication, QInputDialog
from PyQt5.QtGui import QFontDatabase

class StyleHandler:
    def __init__(self, main):
        self.main = main
        self.main.font_size_action.triggered.connect(self.change_font_size)
        self.main.font_family_action.triggered.connect(self.change_font_family)

    def change_font_family(self):
        families = QFontDatabase().families()
        current_index = families.index(self.main.font_family) if self.main.font_family in families else 0
        family, ok = QInputDialog.getItem(self.main, "Change Font Family", "Select font family:", families, current_index, False)
        if ok:
            self.main.font_family = family
            self.apply_styles()
            self.main.update_chart()

    def change_font_size(self):
        size, ok = QInputDialog.getInt(self.main, "Change Font Size", "Enter new font size:", self.main.font_size, 6, 36, 1)
        if ok:
            self.main.font_size = size
            self.apply_styles()
            self.main.update_chart()

    def apply_styles(self):
        app = QApplication.instance()
        app.setStyleSheet(f"""
            * {{
                font-family: {self.main.font_family};
                font-size: {self.main.font_size}px;
            }}
            QTableView {{
               background-color: rgba(0, 0, 0, 128);
            }}
            QTableWidget {{
                background-color: rgba(0, 0, 0, 128);
                color: #FFF;
                gridline-color: #3498db;
                border: 1px solid #3498db;
            }}
            QHeaderView {{
                background-color: #000;
            }}
            QHeaderView::section {{
                background-color: #000;
                color: #FFFFFF;
                padding: 4px;
                border: 1px solid #3498db;
            }}
            QHeaderView[orientation="horizontal"]::section {{
                border-right: 2px solid #FFFFFF;
            }}
            QHeaderView[orientation="vertical"]::section {{
                border-bottom: 2px solid #FFFFFF;
            }}
            QTableWidget::item:selected {{
                background-color: #3498db;
            }}
            QTableCornerButton::section {{
                background-color: #000;
                border: 1px solid #3498db;
            }}
            QLineEdit, QComboBox, QSpinBox {{
                background-color: #111;
                color: white;
                padding: 6px;
                border: 1px solid #3498db;
            }}
            QComboBox QAbstractItemView {{
                background-color: #111;
                color: white;
                border: 1px solid #3498db;
                selection-background-color: #3498db;
                selection-color: white;
            }}
            QPushButton {{
                background-color: #3498db;
                color: white;
                font-weight: bold;
                padding: 8px;
                border: 1px solid #FFFFFF;
            }}
            QLabel {{
                color: #FFFFFF;
            }}
            QMessageBox {{
                background-color: #000;
                color: #FFF;
            }}
            QMessageBox QLabel {{
                color: #FFF;
            }}
            QMessageBox QPushButton {{
                background-color: #3498db;
                color: white;
                border: 1px solid #FFFFFF;
                padding: 5px;
            }}
            QInputDialog {{
                background-color: #000;
                color: #FFF;
            }}
            QMenuBar {{
                background-color: #000;
                color: #FFFFFF;
            }}
            QMenuBar::item {{
                background-color: #000;
                color: #FFFFFF;
            }}
            QMenuBar::item:selected {{
                background-color: #3498db;
                color: #FFFFFF;
            }}
            QMenu {{
                background-color: #000;
                color: #FFFFFF;
                border: 1px solid #3498db;
            }}
            QMenu::item {{
                background-color: #000;
                color: #FFFFFF;
            }}
            QMenu::item:selected {{
                background-color: #3498db;
                color: #FFFFFF;
            }}
            QScrollBar:vertical {{
                border: 1px solid #3498db;
                background: #111;
                width: 15px;
                margin: 0px 0px 0px 0px;
            }}
            QScrollBar::handle:vertical {{
                background: #3498db;
                min-height: 20px;
            }}
            QScrollBar::add-line:vertical {{
                height: 0px;
                subcontrol-position: bottom;
                subcontrol-origin: margin;
            }}
            QScrollBar::sub-line:vertical {{
                height: 0px;
                subcontrol-position: top;
                subcontrol-origin: margin;
            }}
            QScrollBar::add-page:vertical, QScrollBar::sub-page:vertical {{
                background: #111;
            }}
            QScrollBar:horizontal {{
                border: 1px solid #3498db;
                background: #111;
                height: 15px;
                margin: 0px 0px 0px 0px;
            }}
            QScrollBar::handle:horizontal {{
                background: #3498db;
                min-width: 20px;
            }}
            QScrollBar::add-line:horizontal {{
                width: 0px;
                subcontrol-position: right;
                subcontrol-origin: margin;
            }}
            QScrollBar::sub-line:horizontal {{
                width: 0px;
                subcontrol-position: left;
                subcontrol-origin: margin;
            }}
            QScrollBar::add-page:horizontal, QScrollBar::sub-page:horizontal {{
                background: #111;
            }}
        """)