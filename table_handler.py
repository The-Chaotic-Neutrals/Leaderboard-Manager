# table_handler.py
from PyQt5.QtWidgets import QTableWidgetItem, QMessageBox
from PyQt5.QtGui import QColor
from PyQt5.QtCore import Qt
import pandas as pd
import colors

class TableHandler:
    def __init__(self, main):
        self.main = main
        self.main.table.itemChanged.connect(self.handle_cell_change)
        self.main.table.horizontalHeader().sortIndicatorChanged.connect(self.on_sort_changed)
        self.main.table.horizontalHeader().sectionResized.connect(self.on_section_resized)
        self.min_widths = []

    def on_sort_changed(self, col, order):
        self.main.has_been_sorted = True
        self.main.current_sort_col = col
        self.main.current_sort_order = order

    def on_section_resized(self, col, old_size, new_size):
        if col < len(self.min_widths) and new_size < self.min_widths[col]:
            self.main.table.setColumnWidth(col, self.min_widths[col])

    def update_table(self):
        self.main.data_model.df = self.main.data_model.df.fillna('')
        self.main.table.blockSignals(True)  # Prevent recursion
        self.main.table.setRowCount(len(self.main.data_model.df))
        self.main.table.setColumnCount(len(self.main.data_model.df.columns))
        self.main.table.setHorizontalHeaderLabels(self.main.data_model.df.columns.tolist())
        try:
            model_col = self.main.data_model.df.columns.get_loc(self.main.data_model.model_col_name)
        except KeyError:
            model_col = -1  # Fallback, but assume present
        for i, row in self.main.data_model.df.iterrows():
            for j, val in enumerate(row):
                item = QTableWidgetItem(str(val) if pd.notna(val) else '')
                header = self.main.data_model.df.columns[j]
                if header == self.main.data_model.overall_col:  # Overall
                    bg_color = colors.get_color_for_score(val)
                elif header == self.main.data_model.abnormal_col:  # Abnormal Behavior
                    bg_color = colors.get_color_for_abnormal(val)
                else:
                    bg_color = QColor("transparent")
                if bg_color.alpha() > 0:
                    bg_color.setAlpha(180)
                item.setBackground(bg_color)
                fg_color = QColor("black") if colors.is_light_color(bg_color) else QColor("white")
                item.setForeground(fg_color)
                if self.main.data_model.column_types.get(header) in ["integer", "float"]:
                    try:
                        num_val = float(val) if pd.notna(val) else 0.0
                        item.setData(Qt.UserRole, num_val)
                    except ValueError:
                        pass
                if j == model_col:
                    item.setData(self.main.DF_ROW_ROLE, int(i))
                self.main.table.setItem(i, j, item)
        self.main.table.blockSignals(False)  # Re-enable signals
        self.main.table.resizeColumnsToContents()
        self.min_widths = [self.main.table.columnWidth(j) for j in range(self.main.table.columnCount())]

    def refresh_table(self):
        self.update_table()
        if self.main.has_been_sorted:
            self.main.table.sortItems(self.main.current_sort_col, self.main.current_sort_order)

    def handle_cell_change(self, item):
        visual_row = item.row()
        col = item.column()
        header = self.main.data_model.df.columns[col]
        model_col = self.main.data_model.df.columns.get_loc(self.main.data_model.model_col_name)
        model_item = self.main.table.item(visual_row, model_col)
        if model_item:
            df_row = model_item.data(self.main.DF_ROW_ROLE)
            if df_row is not None:
                val = item.text()
                try:
                    self.main.data_model.update_cell(df_row, header, val)
                    self.refresh_table()
                except ValueError as e:
                    self.main.table.blockSignals(True)
                    item.setText(str(self.main.data_model.df.at[df_row, header]))
                    self.main.table.blockSignals(False)
                    QMessageBox.warning(self.main, "Invalid Input", str(e))