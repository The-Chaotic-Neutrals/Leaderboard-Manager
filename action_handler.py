# action_handler.py
from PyQt5.QtWidgets import QInputDialog, QFileDialog, QMessageBox, QDialog, QVBoxLayout, QHBoxLayout, QPushButton, QLabel, QLineEdit, QTableWidgetItem, QColorDialog, QTableWidget
from PyQt5.QtGui import QColor
import pandas as pd
import data_model
import file_io
import re

class TiersDialog(QDialog):
    def __init__(self, parent, is_min_threshold=True, current_tiers=[]):
        super().__init__(parent)
        self.is_min_threshold = is_min_threshold
        self.setWindowTitle("Manage Min Threshold Tiers" if is_min_threshold else "Manage Range Tiers")
        layout = QVBoxLayout()
        self.table = QTableWidget()
        col_count = 3 if is_min_threshold else 4
        self.table.setColumnCount(col_count)
        headers = ["Min", "Label", "Color"] if is_min_threshold else ["Min", "Max", "Label", "Color"]
        self.table.setHorizontalHeaderLabels(headers)
        layout.addWidget(self.table)
        buttons = QHBoxLayout()
        add_btn = QPushButton("Add")
        add_btn.clicked.connect(self.add_tier)
        buttons.addWidget(add_btn)
        edit_btn = QPushButton("Edit")
        edit_btn.clicked.connect(self.edit_tier)
        buttons.addWidget(edit_btn)
        del_btn = QPushButton("Delete")
        del_btn.clicked.connect(self.delete_tier)
        buttons.addWidget(del_btn)
        layout.addLayout(buttons)
        ok_btn = QPushButton("OK")
        ok_btn.clicked.connect(self.accept)
        layout.addWidget(ok_btn)
        self.setLayout(layout)
        self.populate(current_tiers)

    def populate(self, tiers):
        self.table.setRowCount(len(tiers))
        for r, tier in enumerate(tiers):
            min_item = QTableWidgetItem(str(tier[0]))
            self.table.setItem(r, 0, min_item)
            if self.is_min_threshold:
                label_item = QTableWidgetItem(tier[1])
                self.table.setItem(r, 1, label_item)
                color_item = QTableWidgetItem(tier[2])
                color_item.setBackground(QColor(tier[2]))
                self.table.setItem(r, 2, color_item)
            else:
                max_str = "inf" if tier[1] == float('inf') else str(tier[1])
                max_item = QTableWidgetItem(max_str)
                self.table.setItem(r, 1, max_item)
                label_item = QTableWidgetItem(tier[2])
                self.table.setItem(r, 2, label_item)
                color_item = QTableWidgetItem(tier[3])
                color_item.setBackground(QColor(tier[3]))
                self.table.setItem(r, 3, color_item)

    def get_tiers(self):
        tiers = []
        for r in range(self.table.rowCount()):
            try:
                minv = float(self.table.item(r, 0).text())
                if self.is_min_threshold:
                    label = self.table.item(r, 1).text()
                    color = self.table.item(r, 2).text()
                    tiers.append((minv, label, color))
                else:
                    max_str = self.table.item(r, 1).text()
                    maxv = float('inf') if max_str.lower() == 'inf' else float(max_str)
                    label = self.table.item(r, 2).text()
                    color = self.table.item(r, 3).text()
                    tiers.append((minv, maxv, label, color))
            except:
                pass
        if self.is_min_threshold:
            tiers.sort(key=lambda x: x[0], reverse=True)
        else:
            tiers.sort(key=lambda x: x[0])
        return tiers

    def add_tier(self):
        self.edit_tier(add=True)

    def edit_tier(self, add=False):
        row = self.table.currentRow() if not add else -1
        if row == -1 and not add:
            return
        minv = 0.0 if row == -1 else float(self.table.item(row, 0).text())
        if self.is_min_threshold:
            label = "" if row == -1 else self.table.item(row, 1).text()
            color_str = "#FFFFFF" if row == -1 else self.table.item(row, 2).text()
        else:
            maxv = float('inf') if row == -1 else float('inf') if self.table.item(row, 1).text().lower() == 'inf' else float(self.table.item(row, 1).text())
            max_str = "inf" if maxv == float('inf') else str(maxv)
            label = "" if row == -1 else self.table.item(row, 2).text()
            color_str = "#FFFFFF" if row == -1 else self.table.item(row, 3).text()
        edit_dlg = QDialog(self)
        edit_dlg.setWindowTitle("Add/Edit Tier")
        elayout = QVBoxLayout()
        min_label = QLabel("Min:")
        min_input = QLineEdit(str(minv))
        elayout.addWidget(min_label)
        elayout.addWidget(min_input)
        if not self.is_min_threshold:
            max_label = QLabel("Max (inf for unbounded):")
            max_input = QLineEdit(max_str)
            elayout.addWidget(max_label)
            elayout.addWidget(max_input)
        label_label = QLabel("Label:")
        label_input = QLineEdit(label)
        elayout.addWidget(label_label)
        elayout.addWidget(label_input)
        color_btn = QPushButton("Select Color")
        current_color = QColor(color_str)
        color_btn.setStyleSheet(f"background-color: {color_str};")
        def choose_color():
            new_color = QColorDialog.getColor(current_color, edit_dlg)
            if new_color.isValid():
                current_color.setNamedColor(new_color.name())
                color_btn.setStyleSheet(f"background-color: {new_color.name()};")
        color_btn.clicked.connect(choose_color)
        elayout.addWidget(color_btn)
        ok = QPushButton("OK")
        ok.clicked.connect(edit_dlg.accept)
        elayout.addWidget(ok)
        edit_dlg.setLayout(elayout)
        if edit_dlg.exec_():
            new_min = float(min_input.text())
            new_label = label_input.text()
            new_color = current_color.name()
            if not self.is_min_threshold:
                new_max_str = max_input.text()
                new_max = float('inf') if new_max_str.lower() == 'inf' else float(new_max_str)
            if add:
                row = self.table.rowCount()
                self.table.insertRow(row)
            self.table.setItem(row, 0, QTableWidgetItem(str(new_min)))
            if self.is_min_threshold:
                self.table.setItem(row, 1, QTableWidgetItem(new_label))
                color_item = QTableWidgetItem(new_color)
                color_item.setBackground(current_color)
                self.table.setItem(row, 2, color_item)
            else:
                max_item_str = "inf" if new_max == float('inf') else str(new_max)
                self.table.setItem(row, 1, QTableWidgetItem(max_item_str))
                self.table.setItem(row, 2, QTableWidgetItem(new_label))
                color_item = QTableWidgetItem(new_color)
                color_item.setBackground(current_color)
                self.table.setItem(row, 3, color_item)

    def delete_tier(self):
        row = self.table.currentRow()
        if row != -1:
            self.table.removeRow(row)

class ActionHandler:
    def __init__(self, main):
        self.main = main
        self.main.add_btn.clicked.connect(self.add_model)
        self.main.remove_btn.clicked.connect(self.remove_selected)
        self.main.set_formula_action.triggered.connect(self.set_column_formula)
        self.main.score_tiers_action.triggered.connect(self.set_column_tiers)

    def set_column_formula(self):
        numeric_cols = [col for col, typ in self.main.data_model.column_types.items() if typ in ["integer", "float", "boolean"]]
        if not numeric_cols:
            QMessageBox.warning(self.main, "No Columns", "No numeric columns available.")
            return
        col, ok = QInputDialog.getItem(self.main, "Set Column Formula", "Select column:", numeric_cols, 0, False)
        if ok:
            formula = self.main.data_model.column_formulas.get(col, "")
            f, ok2 = QInputDialog.getText(self.main, "Set Formula", "Enter formula (e.g. {Page1:Column1} - {Column2}):", text=formula)
            if ok2:
                try:
                    self.main.data_model.set_column_formula(col, f)
                    self.main.refresh_table()
                    self.main.update_chart()
                    self.main.change_view(self.main.current_view)
                except ValueError as e:
                    QMessageBox.warning(self.main, "Invalid Formula", str(e))

    def set_column_tiers(self):
        numeric_cols = [col for col, typ in self.main.data_model.column_types.items() if typ in ["integer", "float", "boolean"]]
        if not numeric_cols:
            QMessageBox.warning(self.main, "No Columns", "No numeric columns available.")
            return
        col, ok = QInputDialog.getItem(self.main, "Manage Column Tiers", "Select column:", numeric_cols, 0, False)
        if ok:
            current_type = None
            current_tiers = []
            if col in self.main.data_model.column_tiers:
                is_min_threshold, tiers = self.main.data_model.column_tiers[col]
                current_type = "Min Threshold" if is_min_threshold else "Range"
                current_tiers = tiers
            types = ["Min Threshold", "Range"]
            type_index = types.index(current_type) if current_type else 0
            tier_type, ok2 = QInputDialog.getItem(self.main, "Tier Type", "Select tier type:", types, type_index, False)
            if ok2:
                is_min_threshold = (tier_type == "Min Threshold")
                if current_type and tier_type != current_type:
                    reply = QMessageBox.question(self.main, "Change Type", "Changing type will clear existing tiers. Proceed?", QMessageBox.Yes | QMessageBox.No, QMessageBox.No)
                    if reply != QMessageBox.Yes:
                        return
                    current_tiers = []
                if not current_tiers:
                    if is_min_threshold:
                        current_tiers = [
                            (90, "Amethyst (≥90)", "#9966FF80"),
                            (75, "Gold (≥75)", "#FFD70080"),
                            (50, "Silver (≥50)", "#C0C0C080"),
                            (25, "Bronze (≥25)", "#CD7F3280"),
                            (0, "White (≥0)", "#FFFFFF80")
                        ]
                    else:
                        current_tiers = [
                            (0, 10, "Green (0-10)", "#00800080"),
                            (11, 20, "Yellow (11-20)", "ffff00"),
                            (21, 30, "Orange (21-30)", "#ff5500"),
                            (31, float('inf'), "Red (31+)", "#FF0000")
                        ]
                dlg = TiersDialog(self.main, is_min_threshold=is_min_threshold, current_tiers=current_tiers)
                if dlg.exec_():
                    tiers = dlg.get_tiers()
                    self.main.data_model.set_column_tiers(col, is_min_threshold, tiers)
                    self.main.data_model.save_to_history()
                    self.main.update_legends()
                    self.main.refresh_table()
                    self.main.update_chart()
                    self.main.change_view(self.main.current_view)

    def save_session_manually(self):
        file_io.save_multi(self.main.data_models, data_model.DataModel.SESSION_FILE)
        QMessageBox.information(self.main, "Save Successful", "Session saved.")

    def undo(self):
        if self.main.data_model.undo():
            self.main.refresh_table()
            self.main.update_chart()
            self.main.update_legends()
            self.main.change_view(self.main.current_view)
        else:
            QMessageBox.warning(self.main, "Undo", "No more actions to undo.")

    def add_page(self):
        name, ok = QInputDialog.getText(self.main, "Add Page", "Page Name:")
        if ok and name:
            if name in [dm.page_name for dm in self.main.data_models]:
                QMessageBox.warning(self.main, "Duplicate Name", "Page name already exists.")
                return
            dm = data_model.DataModel()
            dm.page_name = name
            dm.all_data_models = self.main.data_models
            self.main.data_models.append(dm)
            self.main.page_selector.addItem(name)
            self.main.page_selector.setCurrentText(name)
            self.main.change_page(self.main.page_selector.currentIndex())
            for existing_dm in self.main.data_models:
                existing_dm.all_data_models = self.main.data_models

    def rename_page(self):
        old_name = self.main.data_model.page_name
        new_name, ok = QInputDialog.getText(self.main, "Rename Page", "New Name:", text=old_name)
        if ok and new_name and new_name != old_name:
            if new_name in [dm.page_name for dm in self.main.data_models]:
                QMessageBox.warning(self.main, "Duplicate Name", "Page name already exists.")
                return
            for dm in self.main.data_models:
                for c, f in list(dm.column_formulas.items()):
                    new_f = f.replace(f"{{{old_name}:", f"{{{new_name}:")
                    if new_f != f:
                        dm.column_formulas[c] = new_f
                        dm.column_formula_refs[c] = set(re.findall(r'\{(.*?)\}', new_f))
                dm.recompute_all_computed()
            self.main.data_model.page_name = new_name
            self.main.page_selector.setItemText(self.main.current_page, new_name)
            self.main.refresh_table()
            self.main.update_chart()

    def delete_page(self):
        if len(self.main.data_models) == 1:
            QMessageBox.warning(self.main, "Delete Page", "Cannot delete the last page.")
            return
        reply = QMessageBox.question(self.main, "Confirm Delete", f"Are you sure you want to delete page '{self.main.data_model.page_name}'?", QMessageBox.Yes | QMessageBox.No, QMessageBox.No)
        if reply == QMessageBox.Yes:
            del_name = self.main.data_model.page_name
            del self.main.data_models[self.main.current_page]
            self.main.page_selector.removeItem(self.main.current_page)
            self.main.current_page = min(self.main.current_page, len(self.main.data_models) - 1)
            self.main.page_selector.setCurrentIndex(self.main.current_page)
            self.main.change_page(self.main.current_page)
            for dm in self.main.data_models:
                dm.all_data_models = self.main.data_models
                dm.recompute_all_computed()

    def add_model(self):
        model = self.main.model_input.text()
        try:
            self.main.data_model.add_model(model)
            self.main.model_input.clear()
            self.main.refresh_table()
            self.main.update_chart()
        except ValueError as e:
            QMessageBox.warning(self.main, "Invalid Input", str(e))

    def add_column(self):
        name, ok = QInputDialog.getText(self.main, "Add Column", "Column Name:")
        if ok and name:
            typ, ok2 = QInputDialog.getItem(self.main, "Add Column", "Type:", ["string", "integer", "float", "boolean"], 0, False)
            if ok2:
                try:
                    self.main.data_model.add_column(name, typ)
                    self.main.refresh_table()
                    self.main.update_chart()
                except ValueError as e:
                    QMessageBox.warning(self.main, "Duplicate Name", str(e))

    def rename_column(self):
        columns = self.main.data_model.df.columns.tolist()
        old_name, ok = QInputDialog.getItem(self.main, "Rename Column", "Select Column:", columns, 0, False)
        if ok:
            new_name, ok2 = QInputDialog.getText(self.main, "Rename Column", "New Name:")
            if ok2 and new_name and new_name != old_name:
                try:
                    self.main.data_model.rename_column(old_name, new_name)
                    page_name = self.main.data_model.page_name
                    for dm in self.main.data_models:
                        for c, f in list(dm.column_formulas.items()):
                            new_f = f.replace(f"{{{page_name}:{old_name}}}", f"{{{page_name}:{new_name}}}")
                            if dm.page_name == page_name:
                                new_f = new_f.replace(f"{{{old_name}}}", f"{{{new_name}}}")
                            if new_f != f:
                                dm.column_formulas[c] = new_f
                                dm.column_formula_refs[c] = set(re.findall(r'\{(.*?)\}', new_f))
                        dm.recompute_all_computed()
                        dm.save_to_history()
                    self.main.refresh_table()
                    self.main.update_chart()
                    self.main.update_legends()
                except ValueError as e:
                    QMessageBox.warning(self.main, "Error", str(e))

    def change_column_type(self):
        columns = self.main.data_model.df.columns.tolist()
        col, ok = QInputDialog.getItem(self.main, "Change Type", "Select Column:", columns, 0, False)
        if ok:
            new_typ, ok2 = QInputDialog.getItem(self.main, "Change Type", "New Type:", ["string", "integer", "float", "boolean"], 0, False)
            if ok2:
                self.main.data_model.change_column_type(col, new_typ)
                self.main.refresh_table()
                self.main.update_chart()

    def remove_selected(self):
        selected_visual_rows = set(i.row() for i in self.main.table.selectedItems())
        if selected_visual_rows:
            selected_df_rows = []
            try:
                model_col = self.main.data_model.df.columns.get_loc(self.main.data_model.model_col_name)
                for visual_row in selected_visual_rows:
                    model_item = self.main.table.item(visual_row, model_col)
                    if model_item:
                        df_row = model_item.data(self.main.DF_ROW_ROLE)
                        if df_row is not None:
                            selected_df_rows.append(df_row)
            except:
                pass
            if selected_df_rows:
                self.main.data_model.remove_rows(selected_df_rows)
                self.main.refresh_table()
                self.main.update_chart()

    def import_data(self):
        path, _ = QFileDialog.getOpenFileName(self.main, "Import Data", "", "Data Files (*.csv *.xlsx)")
        if path:
            # Get df
            if path.endswith('.csv'):
                df = file_io.import_df(path)
            else:
                xls = pd.ExcelFile(path)
                sheets = [s for s in xls.sheet_names if s != 'Metadata']
                if len(sheets) == 0:
                    QMessageBox.warning(self.main, "Invalid File", "No data sheets found.")
                    return
                if len(sheets) > 1:
                    sheet, ok = QInputDialog.getItem(self.main, "Select Sheet", "Choose sheet:", sheets, 0, False)
                    if not ok:
                        return
                else:
                    sheet = sheets[0]
                df = pd.read_excel(xls, sheet_name=sheet)
                df = df.fillna('')
            # Ask for page
            page_name, ok = QInputDialog.getText(self.main, "Import to Page", "Enter page name (existing or new):")
            if ok and page_name:
                existing = [dm for dm in self.main.data_models if dm.page_name == page_name]
                if existing:
                    dm = existing[0]
                    dm.df = df
                    dm.set_column_types()
                    dm.recompute_all_computed()
                    dm.save_to_history()
                else:
                    dm = data_model.DataModel()
                    dm.page_name = page_name
                    dm.df = df
                    dm.set_column_types()
                    dm.recompute_all_computed()
                    dm.save_to_history()
                    self.main.data_models.append(dm)
                    self.main.page_selector.addItem(page_name)
                dm.all_data_models = self.main.data_models
                for other_dm in self.main.data_models:
                    other_dm.all_data_models = self.main.data_models
                    other_dm.recompute_all_computed()
                if page_name == self.main.data_model.page_name:
                    self.main.refresh_table()
                    self.main.update_chart()

    def export_session(self):
        path, _ = QFileDialog.getSaveFileName(self.main, "Export Session", "", "CSV Files (*.csv);;Excel Files (*.xlsx)")
        if path:
            if path.endswith('.xlsx'):
                file_io.save_multi(self.main.data_models, path)
                QMessageBox.information(self, "Export Successful", f"All pages saved to {path}")
            else:
                file_io.export_df(self.main.data_model.df, path)
                QMessageBox.information(self.main, "Export Successful", f"Current page saved to {path}")

    def delete_column(self):
        columns = self.main.data_model.df.columns.tolist()
        col, ok = QInputDialog.getItem(self.main, "Delete Column", "Select Column:", columns, 0, False)
        if ok:
            reply = QMessageBox.question(self.main, "Confirm Delete", f"Are you sure you want to delete column '{col}'?", QMessageBox.Yes | QMessageBox.No, QMessageBox.No)
            if reply == QMessageBox.Yes:
                try:
                    self.main.data_model.delete_column(col)
                    self.main.refresh_table()
                    self.main.update_chart()
                except ValueError as e:
                    QMessageBox.warning(self.main, "Error", str(e))