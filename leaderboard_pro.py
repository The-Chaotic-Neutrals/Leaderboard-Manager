# main.py
import sys
import pandas as pd
from PyQt5.QtWidgets import (
    QApplication, QMainWindow, QMessageBox
)
from PyQt5.QtGui import QPalette, QColor
from PyQt5.QtCore import Qt
import matplotlib
matplotlib.use('Qt5Agg')
from ui import Ui_LeaderboardPro
import data_model
import shortcuts
from table_handler import TableHandler
from style_handler import StyleHandler
from chart_handler import ChartHandler
from action_handler import ActionHandler

class LeaderboardPro(QMainWindow, Ui_LeaderboardPro):
    DF_ROW_ROLE = Qt.UserRole + 1

    def __init__(self):
        super().__init__()
        self.setupUi(self)
        self.data_model = data_model.DataModel()
        self.font_size = 16
        self.font_family = "Verdana"
        self.chart_base_font_size = 12
        self.current_view = "Table"
        self.has_been_sorted = False
        self.current_sort_col = 0
        self.current_sort_order = Qt.AscendingOrder

        self.style_handler = StyleHandler(self)
        self.table_handler = TableHandler(self)
        self.chart_handler = ChartHandler(self)
        self.action_handler = ActionHandler(self)

        self.apply_styles()
        self.refresh_table()
        self.change_view(self.current_view)

        # Shortcuts
        shortcuts.setup_shortcuts(self)

    def apply_styles(self):
        self.style_handler.apply_styles()

    def refresh_table(self):
        self.table_handler.refresh_table()

    def update_table(self):
        self.table_handler.update_table()

    def update_chart(self):
        self.chart_handler.update_chart()

    def change_view(self, view):
        self.chart_handler.change_view(view)

    def reload_session(self):
        self.action_handler.reload_session()

    def save_session_manually(self):
        self.action_handler.save_session_manually()

    def undo(self):
        self.action_handler.undo()

    def add_model(self):
        self.action_handler.add_model()

    def add_column(self):
        self.action_handler.add_column()

    def rename_column(self):
        self.action_handler.rename_column()

    def change_column_type(self):
        self.action_handler.change_column_type()

    def remove_selected(self):
        self.action_handler.remove_selected()

    def import_data(self):
        self.action_handler.import_data()

    def export_session(self):
        self.action_handler.export_session()

    def set_overall_formula(self):
        self.action_handler.set_overall_formula()

    def resizeEvent(self, event):
        super().resizeEvent(event)
        self.bg.setGeometry(self.rect())

    def closeEvent(self, event):
        self.data_model.save_session()
        event.accept()

    def change_font_size(self):
        self.style_handler.change_font_size()

    def change_font_family(self):
        self.style_handler.change_font_family()

if __name__ == "__main__":
    app = QApplication(sys.argv)
    palette = QPalette()
    palette.setColor(QPalette.Window, QColor("#000"))
    palette.setColor(QPalette.WindowText, Qt.white)
    app.setPalette(palette)

    window = LeaderboardPro()
    window.show()
    sys.exit(app.exec_())