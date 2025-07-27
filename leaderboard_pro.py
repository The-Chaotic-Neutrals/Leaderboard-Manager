# leaderboard_pro.py
import sys
import os
import pandas as pd
from PyQt5.QtWidgets import (
    QApplication, QMainWindow, QMessageBox, QLabel, QMenu, QAction
)
from PyQt5.QtGui import QPalette, QColor
from PyQt5.QtCore import Qt
import matplotlib
import matplotlib.pyplot as plt

matplotlib.use('Qt5Agg')
from ui import Ui_LeaderboardPro
import data_model
import shortcuts
from table_handler import TableHandler
from style_handler import StyleHandler
from chart_handler import ChartHandler
from action_handler import ActionHandler
from file_io import load_multi, save_multi


class LeaderboardPro(QMainWindow, Ui_LeaderboardPro):
    DF_ROW_ROLE = Qt.UserRole + 1

    def __init__(self):
        super().__init__()
        self.setupUi(self)
        self.font_size = 16
        self.font_family = "Verdana"
        self.chart_base_font_size = 12
        self.current_view = "Table"
        self.has_been_sorted = False
        self.current_sort_col = 0
        self.current_sort_order = Qt.AscendingOrder

        self.data_models = load_multi(data_model.DataModel.SESSION_FILE) if os.path.exists(data_model.DataModel.SESSION_FILE) else [data_model.DataModel()]

        for dm in self.data_models:
            dm.all_data_models = self.data_models
            self.page_selector.addItem(dm.page_name)

        self.current_page = 0
        self.page_selector.setCurrentIndex(0)
        self.data_model = self.data_models[self.current_page]

        self.style_handler = StyleHandler(self)
        self.table_handler = TableHandler(self)
        self.chart_handler = ChartHandler(self)
        self.action_handler = ActionHandler(self)

        self.page_selector.currentIndexChanged.connect(self.change_page)
        self.apply_styles()
        self.refresh_table()
        self.change_view(self.current_view)
        self.update_legends()

        self.undo_action = QAction("Undo", self)
        self.open_action = QAction("Open", self)
        self.save_action = QAction("Save", self)
        self.reload_action = QAction("Reload", self)

        # Set action texts
        self.open_action.setText("Import Data (CSV/Excel)")
        self.save_action.setText("Save Session")
        self.reload_action.setText("Reload Session")

        # Create export action
        self.export_action = QAction("Export Current Session", self)
        self.export_action.triggered.connect(self.export_session)

        # Add File menu
        self.file_menu = QMenu("File", self)
        self.menuBar().insertMenu(self.customize_menu.menuAction(), self.file_menu)
        self.file_menu.addAction(self.open_action)
        self.file_menu.addAction(self.export_action)
        self.file_menu.addAction(self.save_action)
        self.file_menu.addAction(self.undo_action)
        self.file_menu.addAction(self.reload_action)

        # Add Model menu
        self.model_menu = QMenu("Model", self)
        self.menuBar().insertMenu(self.customize_menu.menuAction(), self.model_menu)
        self.add_model_action = QAction("Add Model", self)
        self.add_model_action.triggered.connect(self.action_handler.add_model)
        self.model_menu.addAction(self.add_model_action)
        self.remove_model_action = QAction("Remove Selected", self)
        self.remove_model_action.triggered.connect(self.action_handler.remove_selected)
        self.model_menu.addAction(self.remove_model_action)

        # Add View menu
        self.view_menu = QMenu("View", self)
        self.menuBar().insertMenu(self.customize_menu.menuAction(), self.view_menu)
        self.table_view_action = QAction("Table", self)
        self.table_view_action.triggered.connect(lambda: self.view_selector.setCurrentText("Table"))
        self.view_menu.addAction(self.table_view_action)
        self.bar_view_action = QAction("Bar Chart", self)
        self.bar_view_action.triggered.connect(lambda: self.view_selector.setCurrentText("Bar Chart"))
        self.view_menu.addAction(self.bar_view_action)

        # Add Page menu
        self.page_menu = QMenu("Page", self)
        self.menuBar().insertMenu(self.customize_menu.menuAction(), self.page_menu)
        self.add_page_action = QAction("Add Page", self)
        self.add_page_action.triggered.connect(self.action_handler.add_page)
        self.page_menu.addAction(self.add_page_action)
        self.rename_page_action = QAction("Rename Page", self)
        self.rename_page_action.triggered.connect(self.action_handler.rename_page)
        self.page_menu.addAction(self.rename_page_action)
        self.delete_page_action = QAction("Delete Page", self)
        self.delete_page_action.triggered.connect(self.action_handler.delete_page)
        self.page_menu.addAction(self.delete_page_action)

        # Add Column menu
        self.column_menu = QMenu("Column", self)
        self.menuBar().insertMenu(self.customize_menu.menuAction(), self.column_menu)
        self.add_column_action = QAction("Add Column", self)
        self.add_column_action.triggered.connect(self.action_handler.add_column)
        self.column_menu.addAction(self.add_column_action)
        self.rename_column_action = QAction("Rename Column", self)
        self.rename_column_action.triggered.connect(self.action_handler.rename_column)
        self.column_menu.addAction(self.rename_column_action)
        self.change_type_action = QAction("Change Column Type", self)
        self.change_type_action.triggered.connect(self.action_handler.change_column_type)
        self.column_menu.addAction(self.change_type_action)
        self.delete_column_action = QAction("Delete Column", self)
        self.delete_column_action.triggered.connect(self.action_handler.delete_column)
        self.column_menu.addAction(self.delete_column_action)

        # Shortcuts
        shortcuts.setup_shortcuts(self)

    def change_page(self, index):
        self.current_page = index
        self.data_model = self.data_models[index]
        self.refresh_table()
        self.update_chart()
        self.update_legends()

    def apply_styles(self):
        self.style_handler.apply_styles()

    def refresh_table(self):
        self.table_handler.refresh_table()

    def update_table(self):
        self.table_handler.update_table()

    def update_chart(self):
        self.chart_handler.update_chart()

    def change_view(self, view):
        self.current_view = view
        if view == "Table":
            self.table.show()
            self.canvas.hide()
            if self.data_model.score_col:
                self.legend_widget.show()
            else:
                self.legend_widget.hide()
            if self.data_model.penalty_col:
                self.abnormal_legend_widget.show()
            else:
                self.abnormal_legend_widget.hide()
        else:
            self.table.hide()
            self.canvas.show()
            self.legend_widget.hide()
            self.abnormal_legend_widget.hide()
            self.update_chart()

    def reload_session(self):
        self.data_models = load_multi(data_model.DataModel.SESSION_FILE)
        for dm in self.data_models:
            dm.all_data_models = self.data_models
        self.page_selector.clear()
        for dm in self.data_models:
            self.page_selector.addItem(dm.page_name)
        self.current_page = 0
        self.page_selector.setCurrentIndex(0)
        self.change_page(0)
        self.update_legends()
        QMessageBox.information(self, "Reload Successful", "Session reloaded from file.")

    def save_session_manually(self):
        self.action_handler.save_session_manually()

    def undo(self):
        self.action_handler.undo()

    def import_data(self):
        self.action_handler.import_data()

    def export_session(self):
        self.action_handler.export_session()

    def resizeEvent(self, event):
        super().resizeEvent(event)
        self.bg.setGeometry(self.rect())

    def closeEvent(self, event):
        save_multi(self.data_models, data_model.DataModel.SESSION_FILE)
        event.accept()

    def change_font_size(self):
        self.style_handler.change_font_size()

    def change_font_family(self):
        self.style_handler.change_font_family()

    def update_legends(self):
        # Update score legend
        if self.data_model.score_col:
            layout = self.legend_widget.layout()
            while layout.count() > 1:
                item = layout.takeAt(1)
                widget = item.widget()
                if widget:
                    widget.deleteLater()
            legend_title = layout.itemAt(0).widget()
            score_name = self.data_model.score_col
            legend_title.setText(f"{score_name} Color Legend")
            legend_title.setStyleSheet("color: #3498db; font-weight: bold;")
            for _, text, color in self.data_model.score_tiers:
                label = QLabel(text)
                label.setStyleSheet(f"color: {color};")
                layout.addWidget(label)
        else:
            self.legend_widget.hide()

        # Update penalty legend
        if self.data_model.penalty_col:
            layout = self.abnormal_legend_widget.layout()
            while layout.count() > 1:
                item = layout.takeAt(1)
                widget = item.widget()
                if widget:
                    widget.deleteLater()
            abnormal_legend_title = layout.itemAt(0).widget()
            penalty_name = self.data_model.penalty_col
            abnormal_legend_title.setText(f"{penalty_name} Color Legend")
            abnormal_legend_title.setStyleSheet("color: #3498db; font-weight: bold;")
            for _, _, text, color in self.data_model.penalty_tiers:
                label = QLabel(text)
                label.setStyleSheet(f"color: {color};")
                layout.addWidget(label)
        else:
            self.abnormal_legend_widget.hide()

if __name__ == "__main__":
    app = QApplication(sys.argv)
    palette = QPalette()
    palette.setColor(QPalette.Window, QColor("#000"))
    palette.setColor(QPalette.WindowText, Qt.white)
    app.setPalette(palette)

    window = LeaderboardPro()
    window.show()
    sys.exit(app.exec_())