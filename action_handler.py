# action_handler.py
from PyQt5.QtWidgets import QInputDialog, QFileDialog, QMessageBox

class ActionHandler:
    def __init__(self, main):
        self.main = main
        self.main.add_btn.clicked.connect(self.add_model)
        self.main.add_column_btn.clicked.connect(self.add_column)
        self.main.rename_column_btn.clicked.connect(self.rename_column)
        self.main.change_type_btn.clicked.connect(self.change_column_type)
        self.main.remove_btn.clicked.connect(self.remove_selected)
        self.main.import_btn.clicked.connect(self.import_data)
        self.main.export_btn.clicked.connect(self.export_session)
        self.main.save_btn.clicked.connect(self.save_session_manually)
        self.main.undo_btn.clicked.connect(self.undo)
        self.main.set_formula_btn.clicked.connect(self.set_overall_formula)
        self.main.delete_column_btn.clicked.connect(self.delete_column)

    def reload_session(self):
        self.main.data_model.load_session()
        self.main.data_model.set_column_types()
        self.main.refresh_table()
        self.main.update_chart()
        QMessageBox.information(self.main, "Reload Successful", "Session reloaded from file.")

    def save_session_manually(self):
        self.main.data_model.save_session()
        QMessageBox.information(self.main, "Save Successful", "Session saved.")

    def undo(self):
        if self.main.data_model.undo():
            self.main.refresh_table()
            self.main.update_chart()
        else:
            QMessageBox.warning(self.main, "Undo", "No more actions to undo.")

    def add_model(self):
        model = self.main.model_input.text()
        try:
            retrieval = float(self.main.retrieval_input.text())
            abnormal_behavior = float(self.main.abnormal_behavior_input.text())
        except ValueError:
            QMessageBox.warning(self.main, "Invalid Input", "Please provide valid numeric scores.")
            return
        try:
            self.main.data_model.add_model(model, retrieval, abnormal_behavior)
            self.clear_inputs()
            self.main.refresh_table()
            self.main.update_chart()
        except ValueError as e:
            QMessageBox.warning(self.main, "Invalid Input", str(e))

    def clear_inputs(self):
        self.main.model_input.clear()
        self.main.retrieval_input.clear()
        self.main.abnormal_behavior_input.clear()

    def add_column(self):
        name, ok = QInputDialog.getText(self.main, "Add Column", "Column Name:")
        if ok and name:
            typ, ok2 = QInputDialog.getItem(self.main, "Add Column", "Type:", ["string", "integer", "float"], 0, False)
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
                    self.main.refresh_table()
                    self.main.update_chart()
                except ValueError as e:
                    QMessageBox.warning(self.main, "Error", str(e))

    def change_column_type(self):
        columns = self.main.data_model.df.columns.tolist()
        col, ok = QInputDialog.getItem(self.main, "Change Type", "Select Column:", columns, 0, False)
        if ok:
            new_typ, ok2 = QInputDialog.getItem(self.main, "Change Type", "New Type:", ["string", "integer", "float"], 0, False)
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
            self.main.data_model.import_data(path)
            self.main.refresh_table()
            self.main.update_chart()

    def export_session(self):
        path, _ = QFileDialog.getSaveFileName(self.main, "Export Session", "", "CSV Files (*.csv)")
        if path:
            self.main.data_model.export_session(path)
            QMessageBox.information(self.main, "Export Successful", f"Session saved to {path}")

    def set_overall_formula(self):
        formula, ok = QInputDialog.getText(self.main, "Set Overall Formula", "Enter formula (e.g. {Retrieval} - {Abnormal Behavior}):", text=self.main.data_model.overall_formula)
        if ok and formula:
            self.main.data_model.set_overall_formula(formula)
            self.main.refresh_table()
            self.main.update_chart()

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