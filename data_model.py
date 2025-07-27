# data_model.py
import copy
import pandas as pd
import re
from PyQt5.QtWidgets import QMessageBox
from PyQt5.QtGui import QColor

class DataModel:
    SESSION_FILE = "leaderboard_session.xlsx"

    def __init__(self):
        self.page_name = "Default"
        self.df = pd.DataFrame(columns=["Model"])
        self.column_types = {}
        self.df_history = []
        self.score_col = None
        self.penalty_col = None
        self.model_col_name = "Model"
        self.score_formula = ""
        self.formula_cols = set()
        self.score_tiers = []
        self.penalty_tiers = []
        self.all_data_models = None  # Will be set by main
        self.set_column_types()
        self.save_to_history()

    def save_to_history(self):
        self.df_history.append((copy.deepcopy(self.df), copy.deepcopy(self.column_types), self.score_col, self.penalty_col, self.score_formula, copy.deepcopy(self.score_tiers), copy.deepcopy(self.penalty_tiers)))

    def undo(self):
        if len(self.df_history) > 1:
            self.df_history.pop()
            self.df, self.column_types, self.score_col, self.penalty_col, self.score_formula, self.score_tiers, self.penalty_tiers = copy.deepcopy(self.df_history[-1])
            self.formula_cols = set(re.findall(r'\{(.*?)\}', self.score_formula))
            return True
        return False

    def set_column_types(self):
        self.column_types = {}
        for col in self.df.columns:
            if col == "Model":
                self.column_types[col] = "string"
            elif pd.api.types.is_bool_dtype(self.df[col]):
                self.column_types[col] = "boolean"
            elif pd.api.types.is_numeric_dtype(self.df[col]):
                all_int = self.df[col].dropna().apply(lambda x: isinstance(x, (int, float)) and float(x).is_integer()).all()
                self.column_types[col] = "integer" if all_int else "float"
            else:
                self.column_types[col] = "string"

    def compute_overall(self, row_dict):
        formula = self.score_formula
        if not formula:
            return 0
        refs = re.findall(r'\{(.*?)\}', formula)
        values = {}
        for ref in refs:
            if ':' in ref:
                page_name, col_name = ref.split(':', 1)
                if page_name == self.page_name:
                    val = row_dict.get(col_name, 0)
                else:
                    other_dm = next((dm for dm in self.all_data_models if dm.page_name == page_name), None)
                    if other_dm:
                        model = row_dict.get(self.model_col_name, '')
                        matching = other_dm.df[other_dm.df[self.model_col_name] == model]
                        if not matching.empty:
                            val = matching.iloc[0].get(col_name, 0)
                        else:
                            val = 0
                    else:
                        val = 0
            else:
                val = row_dict.get(ref, 0)
            if isinstance(val, bool):
                val = 1 if val else 0
            if not isinstance(val, (int, float)):
                val = 0
            values[ref] = val
        expr = formula
        for ref in refs:
            expr = expr.replace(f"{{{ref}}}", str(values[ref]))
        try:
            return eval(expr)
        except:
            return 0

    def recompute_all_overall(self):
        if self.score_col:
            for i in range(len(self.df)):
                self.df.at[i, self.score_col] = self.compute_overall(self.df.iloc[i].to_dict())

    def add_model(self, model):
        if model.strip() == "":
            raise ValueError("Model name cannot be empty.")
        if model in self.df[self.model_col_name].tolist():
            raise ValueError("A model with this name already exists.")
        new_row = {self.model_col_name: model}
        for col in self.df.columns:
            if col != self.model_col_name:
                typ = self.column_types[col]
                if typ == "string":
                    new_row[col] = ""
                elif typ == "integer":
                    new_row[col] = 0
                elif typ == "float":
                    new_row[col] = 0.0
                elif typ == "boolean":
                    new_row[col] = False
        if self.score_col:
            new_row[self.score_col] = self.compute_overall(new_row)
        new_df = pd.DataFrame([new_row])
        self.df = pd.concat([self.df, new_df], ignore_index=True)
        self.save_to_history()

    def add_column(self, name, typ):
        if name in self.df.columns:
            raise ValueError("Column name already exists.")
        if typ == "string":
            default = ''
        elif typ == "integer":
            default = 0
        elif typ == "float":
            default = 0.0
        elif typ == "boolean":
            default = False
        self.df[name] = default
        self.column_types[name] = typ
        self.save_to_history()

    def rename_column(self, old_name, new_name):
        if old_name == self.model_col_name:
            raise ValueError("Cannot rename the Model column.")
        if new_name in self.df.columns:
            raise ValueError("New name already exists.")
        self.df = self.df.rename(columns={old_name: new_name})
        if old_name in self.column_types:
            self.column_types[new_name] = self.column_types.pop(old_name)
        if old_name == self.score_col:
            self.score_col = new_name
        if old_name == self.penalty_col:
            self.penalty_col = new_name
        self.save_to_history()

    def change_column_type(self, col, new_typ):
        if new_typ == self.column_types.get(col):
            return
        self.column_types[col] = new_typ
        for i in range(len(self.df)):
            val = self.df.at[i, col]
            try:
                if new_typ == "string":
                    self.df.at[i, col] = str(val)
                elif new_typ == "integer":
                    self.df.at[i, col] = int(float(val))
                elif new_typ == "float":
                    self.df.at[i, col] = float(val)
                elif new_typ == "boolean":
                    self.df.at[i, col] = bool(val)
            except ValueError:
                if new_typ == "string":
                    default = ''
                elif new_typ == "integer":
                    default = 0
                elif new_typ == "float":
                    default = 0.0
                elif new_typ == "boolean":
                    default = False
                self.df.at[i, col] = default
        self.save_to_history()

    def remove_rows(self, df_rows):
        df_rows = sorted(set(df_rows), reverse=True)
        for df_row in df_rows:
            self.df.drop(self.df.index[df_row], inplace=True)
        self.df.reset_index(drop=True, inplace=True)
        self.save_to_history()

    def set_score_formula(self, formula):
        refs = set(re.findall(r'\{(.*?)\}', formula))
        if self.score_col in refs:
            raise ValueError("Formula cannot reference the score column itself.")
        for ref in refs:
            if ':' in ref:
                page, col = ref.split(':', 1)
                other_dm = next((dm for dm in self.all_data_models if dm.page_name == page), None)
                if not other_dm:
                    raise ValueError(f"Page {page} not found.")
                if col not in other_dm.df.columns:
                    raise ValueError(f"Column {col} not found in page {page}.")
                if other_dm.column_types.get(col) not in ["integer", "float", "boolean"]:
                    raise ValueError(f"Column {col} in page {page} is not numeric.")
            else:
                if ref not in self.df.columns:
                    raise ValueError(f"Column {ref} not found.")
                if self.column_types.get(ref) not in ["integer", "float", "boolean"]:
                    raise ValueError(f"Column {ref} is not numeric.")
        self.score_formula = formula
        self.formula_cols = refs
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
            elif typ == "boolean":
                parsed_val = bool(val)
        except ValueError:
            raise ValueError(f"Invalid input '{val}' for {typ} type.")
        if parsed_val == old_val:
            return
        self.df.at[df_row, header] = parsed_val
        if header != self.score_col and (header in self.formula_cols or any(header == r.split(':',1)[-1] and r.startswith(self.page_name + ':') for r in self.formula_cols)):
            self.df.at[df_row, self.score_col] = self.compute_overall(self.df.iloc[df_row].to_dict())
        self.save_to_history()

    def delete_column(self, col):
        if col == self.model_col_name:
            raise ValueError("Cannot delete the Model column.")
        if col == self.score_col:
            raise ValueError("Cannot delete the score column.")
        if col == self.penalty_col:
            raise ValueError("Cannot delete the penalty column.")
        if col in self.formula_cols:
            raise ValueError("Column is used in the score formula. Change the formula first if needed.")
        ref = f"{self.page_name}:{col}"
        for dm in self.all_data_models:
            if ref in dm.formula_cols:
                raise ValueError(f"Column is used in a formula in page {dm.page_name}")
        self.df.drop(columns=[col], inplace=True)
        if col in self.column_types:
            del self.column_types[col]
        self.save_to_history()

    def set_score_col(self, col):
        if col not in self.df.columns:
            raise ValueError("Column does not exist.")
        if self.column_types.get(col) not in ["integer", "float", "boolean"]:
            raise ValueError("Score column must be numeric.")
        if col == self.penalty_col:
            raise ValueError("Cannot set the same column as penalty.")
        self.score_col = col
        self.recompute_all_overall()
        self.save_to_history()

    def set_penalty_col(self, col):
        if col not in self.df.columns:
            raise ValueError("Column does not exist.")
        if self.column_types.get(col) not in ["integer", "float", "boolean"]:
            raise ValueError("Penalty column must be numeric.")
        if col == self.score_col:
            raise ValueError("Cannot set the same column as score.")
        self.penalty_col = col
        self.save_to_history()

    def get_score_color(self, score):
        try:
            score = float(score)
            for min_val, _, color in self.score_tiers:
                if score >= min_val:
                    return QColor(color)
            return QColor("transparent")
        except ValueError:
            return QColor("transparent")

    def get_penalty_color(self, score):
        try:
            score = float(score)
            for min_val, max_val, _, color in self.penalty_tiers:
                if min_val <= score <= max_val:
                    return QColor(color)
            return QColor("transparent")
        except ValueError:
            return QColor("transparent")