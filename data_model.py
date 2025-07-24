# data_model.py
import copy
import pandas as pd
import re
from PyQt5.QtWidgets import QMessageBox
import file_io as io

class DataModel:
    SESSION_FILE = "leaderboard_session.csv"
    FORMULA_FILE = "leaderboard_formula.txt"

    def __init__(self):
        self.df = pd.DataFrame(columns=["Model", "Retrieval", "Abnormal Behavior", "Overall"])
        self.column_types = {}
        self.df_history = []
        self.retrieval_col = "Retrieval"
        self.abnormal_col = "Abnormal Behavior"
        self.overall_col = "Overall"
        self.model_col_name = "Model"
        self.overall_formula = "{Retrieval} - {Abnormal Behavior}"
        self.formula_cols = set(re.findall(r'\{(.*?)\}', self.overall_formula))
        self.load_session()
        self.set_column_types()
        self.save_to_history()

    def load_session(self):
        self.df = io.load_df(self.SESSION_FILE)
        self.overall_formula = io.load_formula(self.FORMULA_FILE)
        self.formula_cols = set(re.findall(r'\{(.*?)\}', self.overall_formula))
        self.recompute_all_overall()

    def save_session(self):
        io.save_df(self.df, self.SESSION_FILE)
        io.save_formula(self.overall_formula, self.FORMULA_FILE)

    def save_to_history(self):
        self.df_history.append((copy.deepcopy(self.df), copy.deepcopy(self.column_types), self.retrieval_col, self.abnormal_col, self.overall_col, self.overall_formula))

    def undo(self):
        if len(self.df_history) > 1:
            self.df_history.pop()
            self.df, self.column_types, self.retrieval_col, self.abnormal_col, self.overall_col, self.overall_formula = copy.deepcopy(self.df_history[-1])
            self.formula_cols = set(re.findall(r'\{(.*?)\}', self.overall_formula))
            return True
        return False

    def set_column_types(self):
        self.column_types = {}
        for col in self.df.columns:
            if col == "Model":
                self.column_types[col] = "string"
            elif pd.api.types.is_numeric_dtype(self.df[col]):
                all_int = self.df[col].dropna().apply(lambda x: isinstance(x, (int, float)) and float(x).is_integer()).all()
                self.column_types[col] = "integer" if all_int else "float"
            else:
                self.column_types[col] = "string"

    def compute_overall(self, row_dict):
        formula = self.overall_formula
        cols = re.findall(r'\{(.*?)\}', formula)
        values = {}
        for col in cols:
            val = row_dict.get(col, 0)
            if not isinstance(val, (int, float)):
                val = 0
            values[col] = val
        expr = formula
        for col in cols:
            expr = expr.replace(f"{{{col}}}", str(values[col]))
        try:
            return eval(expr)
        except:
            return 0

    def recompute_all_overall(self):
        for i in range(len(self.df)):
            self.df.at[i, self.overall_col] = self.compute_overall(self.df.iloc[i].to_dict())

    def add_model(self, model, retrieval, abnormal):
        if model.strip() == "":
            raise ValueError("Model name cannot be empty.")
        if model in self.df[self.model_col_name].tolist():
            raise ValueError("A model with this name already exists.")
        new_row = {self.model_col_name: model, self.retrieval_col: retrieval, self.abnormal_col: abnormal}
        for col in self.df.columns:
            if col not in new_row:
                typ = self.column_types[col]
                new_row[col] = "" if typ == "string" else 0 if typ == "integer" else 0.0
        new_row[self.overall_col] = self.compute_overall(new_row)
        new_df = pd.DataFrame([new_row])
        self.df = pd.concat([self.df, new_df], ignore_index=True)
        self.save_to_history()

    def add_column(self, name, typ):
        if name in self.df.columns:
            raise ValueError("Column name already exists.")
        default = '' if typ == "string" else 0 if typ == "integer" else 0.0
        self.df[name] = default
        self.column_types[name] = typ
        self.save_to_history()

    def rename_column(self, old_name, new_name):
        if old_name == self.model_col_name:
            raise ValueError("Cannot rename the Model column.")
        if old_name == self.overall_col:
            raise ValueError("Cannot rename the Overall column.")
        if new_name in self.df.columns:
            raise ValueError("New name already exists.")
        self.df = self.df.rename(columns={old_name: new_name})
        if old_name in self.column_types:
            self.column_types[new_name] = self.column_types.pop(old_name)
        if old_name == self.retrieval_col:
            self.retrieval_col = new_name
        elif old_name == self.abnormal_col:
            self.abnormal_col = new_name
        if old_name in self.formula_cols:
            self.overall_formula = self.overall_formula.replace(f"{{{old_name}}}", f"{{{new_name}}}")
            self.formula_cols = set(re.findall(r'\{(.*?)\}', self.overall_formula))
        self.save_to_history()

    def change_column_type(self, col, new_typ):
        if new_typ == self.column_types.get(col):
            return
        self.column_types[col] = new_typ
        for i in range(len(self.df)):
            val = self.df.at[i, col]
            try:
                if new_typ =="string":
                    self.df.at[i, col] = str(val)
                elif new_typ == "integer":
                    self.df.at[i, col] = int(float(val))
                elif new_typ == "float":
                    self.df.at[i, col] = float(val)
            except ValueError:
                default = '' if new_typ == "string" else 0 if new_typ == "integer" else 0.0
                self.df.at[i, col] = default
        self.save_to_history()

    def remove_rows(self, df_rows):
        df_rows = sorted(set(df_rows), reverse=True)
        for df_row in df_rows:
            self.df.drop(self.df.index[df_row], inplace=True)
        self.df.reset_index(drop=True, inplace=True)
        self.save_to_history()

    def import_data(self, path):
        self.df = io.import_df(path)
        self.df = self.df.fillna('')
        self.set_column_types()
        self.recompute_all_overall()
        self.save_to_history()

    def export_session(self, path):
        io.export_df(self.df, path)

    def set_overall_formula(self, formula):
        self.overall_formula = formula
        self.formula_cols = set(re.findall(r'\{(.*?)\}', self.overall_formula))
        self.recompute_all_overall()
        self.save_to_history()

    def update_cell(self, df_row, header, val):
        typ = self.column_types.get(header, "string")
        old_val = self.df.at[df_row, header]
        if header == self.model_col_name:
            if val.strip() == "":
                raise ValueError("Model name cannot be empty.")
            if val in self.df[self.model_col_name].tolist() and val != old_val:
                raise ValueError("A model with this name already exists.")
        try:
            if typ == "string":
                parsed_val = str(val)
            elif typ == "integer":
                parsed_val = int(val)
            elif typ == "float":
                parsed_val = float(val)
        except ValueError:
            raise ValueError(f"Invalid input '{val}' for {typ} type.")
        if parsed_val == old_val:
            return
        self.df.at[df_row, header] = parsed_val
        if header != self.overall_col and header in self.formula_cols:
            self.df.at[df_row, self.overall_col] = self.compute_overall(self.df.iloc[df_row].to_dict())
        self.save_to_history()

    def delete_column(self, col):
        if col == self.model_col_name:
            raise ValueError("Cannot delete the Model column.")
        if col == self.overall_col:
            raise ValueError("Cannot delete the Overall column.")
        if col in self.formula_cols:
            raise ValueError("Cannot delete a column used in the Overall formula. Change the formula first if needed.")
        self.df.drop(columns=[col], inplace=True)
        if col in self.column_types:
            del self.column_types[col]
        if col == self.retrieval_col:
            self.retrieval_col = ""
        elif col == self.abnormal_col:
            self.abnormal_col = ""
        self.save_to_history()