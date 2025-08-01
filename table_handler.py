# table_handler.py
from PyQt5.QtWidgets import QTableWidgetItem, QMessageBox
from PyQt5.QtGui import QColor
from PyQt5.QtCore import Qt
import pandas as pd

class TableHandler:
    def __init__(self, main):
        self.main = main
        self.main.table.itemChanged.connect(self.handle_cell_change)
        self.main.table.horizontalHeader().sortIndicatorChanged.connect(self.on_sort_changed)
        self.main.table.horizontalHeader().sectionResized.connect(self.on_section_resized)
        self.main.table.itemClicked.connect(self.handle_item_clicked)
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
                header = self.main.data_model.df.columns[j]
                typ = self.main.data_model.column_types.get(header)
                if typ == "boolean":
                    item = QTableWidgetItem()
                    item.setFlags(Qt.ItemIsEnabled)
                    item.setCheckState(Qt.Checked if val else Qt.Unchecked)
                else:
                    item = QTableWidgetItem(str(val) if pd.notna(val) else '')
                    if typ in ["integer", "float"]:
                        try:
                            num_val = float(val) if pd.notna(val) else 0.0
                            item.setData(Qt.UserRole, num_val)
                        except ValueError:
                            pass
                bg_color = self.main.data_model.get_column_color(header, val)
                if bg_color.alpha() > 0:
                    bg_color.setAlpha(180)
                item.setBackground(bg_color)
                fg_color = QColor("black") if self.is_light_color(bg_color) else QColor("white")
                item.setForeground(fg_color)
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
        typ = self.main.data_model.column_types.get(header)
        if typ == "boolean":
            return  # Handled separately
        model_col = self.main.data_model.df.columns.get_loc(self.main.data_model.model_col_name)
        model_item = self.main.table.item(visual_row, model_col)
        if model_item:
            df_row = model_item.data(self.main.DF_ROW_ROLE)
            if df_row is not None:
                val = item.text()
                try:
                    self.main.data_model.update_cell(df_row, header, val)
                    # Update all potentially affected cells in this row (since recompute_all_computed may change other columns)
                    for k in range(self.main.table.columnCount()):
                        h = self.main.table.horizontalHeaderItem(k).text()
                        it = self.main.table.item(visual_row, k)
                        if it:
                            new_v = self.main.data_model.df.at[df_row, h]
                            it.setText(str(new_v))
                            if self.main.data_model.column_types.get(h) in ["integer", "float"]:
                                try:
                                    num_v = float(new_v)
                                    it.setData(Qt.UserRole, num_v)
                                except ValueError:
                                    pass
                            bg = self.main.data_model.get_column_color(h, new_v)
                            if bg.alpha() > 0:
                                bg.setAlpha(180)
                            it.setBackground(bg)
                            fg = QColor("black") if self.is_light_color(bg) else QColor("white")
                            it.setForeground(fg)
                except ValueError as e:
                    QMessageBox.warning(self.main, "Invalid Input", str(e))
                    # Revert text
                    item.setText(str(self.main.data_model.df.at[df_row, header]))

    def handle_item_clicked(self, item):
        col = item.column()
        header = self.main.data_model.df.columns[col]
        if self.main.data_model.column_types.get(header) == "boolean":
            current_state = item.checkState()
            new_state = Qt.Unchecked if current_state == Qt.Checked else Qt.Checked
            item.setCheckState(new_state)
            model_col = self.main.data_model.df.columns.get_loc(self.main.data_model.model_col_name)
            df_row = self.main.table.item(item.row(), model_col).data(self.main.DF_ROW_ROLE)
            val = (new_state == Qt.Checked)
            self.main.data_model.update_cell(df_row, header, val)
            # Update color
            bg_color = self.main.data_model.get_column_color(header, val)
            if bg_color.alpha() > 0:
                bg_color.setAlpha(180)
            item.setBackground(bg_color)
            fg_color = QColor("black") if self.is_light_color(bg_color) else QColor("white")
            item.setForeground(fg_color)

            # Update affected cells in row
            visual_row = item.row()
            for k in range(self.main.table.columnCount()):
                h = self.main.table.horizontalHeaderItem(k).text()
                if h == header:
                    continue
                it = self.main.table.item(visual_row, k)
                if it and h in self.main.data_model.column_formulas:
                    new_v = self.main.data_model.df.at[df_row, h]
                    it.setText(str(new_v))
                    if self.main.data_model.column_types.get(h) in ["integer", "float"]:
                        try:
                            num_v = float(new_v)
                            it.setData(Qt.UserRole, num_v)
                        except ValueError:
                            pass
                    bg = self.main.data_model.get_column_color(h, new_v)
                    if bg.alpha() > 0:
                        bg.setAlpha(180)
                    it.setBackground(bg)
                    fg = QColor("black") if self.is_light_color(bg) else QColor("white")
                    it.setForeground(fg)

    def is_light_color(self, color):
        r = color.red() / 255.0
        g = color.green() / 255.0
        b = color.blue() / 255.0
        luminance = 0.299 * r + 0.587 * g + 0.114 * b
        return luminance > 0.5