# data_model.py
import copy
import pandas as pd
import re
from PyQt5.QtWidgets import QMessageBox
from PyQt5.QtGui import QColor
from collections import deque, defaultdict

class DataModel:
    SESSION_FILE = "leaderboard_session.xlsx"

    def __init__(self):
        self.page_name = "Default"
        self.df = pd.DataFrame(columns=["Model"])
        self.column_types = {}
        self.df_history = []
        self.model_col_name = "Model"
        self.column_formulas = {}
        self.column_formula_refs = {}
        self.column_tiers = {}
        self.plot_columns = []
        self.all_data_models = None  # Will be set by main
        self.set_column_types()
        self.save_to_history()

    def save_to_history(self):
        self.df_history.append((copy.deepcopy(self.df), copy.deepcopy(self.column_types), copy.deepcopy(self.column_formulas), copy.deepcopy(self.column_formula_refs), copy.deepcopy(self.column_tiers), copy.deepcopy(self.plot_columns)))

    def undo(self):
        if len(self.df_history) > 1:
            self.df_history.pop()
            self.df, self.column_types, self.column_formulas, self.column_formula_refs, self.column_tiers, self.plot_columns = copy.deepcopy(self.df_history[-1])
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

    def compute_value(self, row_dict, formula):
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

    def recompute_column(self, col):
        if col not in self.column_formulas:
            return
        formula = self.column_formulas[col]
        for i in range(len(self.df)):
            row_dict = self.df.iloc[i].to_dict()
            val = self.compute_value(row_dict, formula)
            self.df.at[i, col] = val

    def get_topo_order(self):
        graph = self.build_dep_graph()
        rev_graph = defaultdict(list)
        for u in graph:
            for v in graph[u]:
                rev_graph[v].append(u)
        computed = list(graph.keys())
        indeg = {node: 0 for node in computed}
        for u in graph:
            for v in graph[u]:
                if v in indeg:
                    indeg[v] += 1
        q = deque([node for node in indeg if indeg[node] == 0])
        order = []
        while q:
            u = q.popleft()
            order.append(u)
            for v in rev_graph[u]:
                indeg[v] -= 1
                if indeg[v] == 0:
                    q.append(v)
        if len(order) != len(computed):
            print("Cycle detected in formula dependencies")
        return order

    def recompute_all_computed(self):
        order = self.get_topo_order()
        for full in order:
            page, col = full.split(':', 1)
            dm = next((d for d in self.all_data_models if d.page_name == page), None)
            if dm:
                dm.recompute_column(col)
        graph = self.build_dep_graph()
        if len(order) < len(graph):
            all_computed = set(graph.keys())
            recomputed = set(order)
            cycle_fulls = all_computed - recomputed
            for full in cycle_fulls:
                page, col = full.split(':', 1)
                dm = next((d for d in self.all_data_models if d.page_name == page), None)
                if dm:
                    dm.df[col] = 0

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
        new_df = pd.DataFrame([new_row])
        self.df = pd.concat([self.df, new_df], ignore_index=True)
        self.recompute_all_computed()
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
        if old_name in self.column_formulas:
            self.column_formulas[new_name] = self.column_formulas.pop(old_name)
            self.column_formula_refs[new_name] = self.column_formula_refs.pop(old_name)
        if old_name in self.column_tiers:
            self.column_tiers[new_name] = self.column_tiers.pop(old_name)
        if old_name in self.plot_columns:
            self.plot_columns = [new_name if c == old_name else c for c in self.plot_columns]
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

    def build_dep_graph(self):
        graph = {}
        for dm in self.all_data_models:
            page = dm.page_name
            for col in dm.column_formulas:
                full_target = page + ':' + col
                graph[full_target] = set()
                for ref in dm.column_formula_refs[col]:
                    if ':' not in ref:
                        ref_full = page + ':' + ref
                    else:
                        ref_full = ref
                    graph[full_target].add(ref_full)
        return graph

    def has_cycle(self):
        graph = self.build_dep_graph()
        visited = {}
        path = {}
        def dfs(node):
            if node in path:
                return True
            if node in visited:
                return False
            visited[node] = True
            path[node] = True
            for neigh in graph.get(node, []):
                if dfs(neigh):
                    return True
            del path[node]
            return False
        for node in graph:
            if node not in visited:
                if dfs(node):
                    return True
        return False

    def set_column_formula(self, col, formula):
        if col not in self.df.columns:
            raise ValueError("Column does not exist.")
        if self.column_types.get(col) not in ["integer", "float", "boolean"]:
            raise ValueError("Column must be numeric.")
        refs = set(re.findall(r'\{(.*?)\}', formula))
        for ref in refs:
            if ':' in ref:
                page, c = ref.split(':', 1)
                other_dm = next((dm for dm in self.all_data_models if dm.page_name == page), None)
                if not other_dm:
                    raise ValueError(f"Page {page} not found.")
                if c not in other_dm.df.columns:
                    raise ValueError(f"Column {c} not found in page {page}.")
                if other_dm.column_types.get(c) not in ["integer", "float", "boolean"]:
                    raise ValueError(f"Column {c} in page {page} is not numeric.")
            else:
                if ref not in self.df.columns:
                    raise ValueError(f"Column {ref} not found.")
                if self.column_types.get(ref) not in ["integer", "float", "boolean"]:
                    raise ValueError(f"Column {ref} is not numeric.")
            if ref == col:
                raise ValueError("Formula cannot reference itself.")
        old_formula = self.column_formulas.get(col)
        old_refs = self.column_formula_refs.get(col)
        self.column_formulas[col] = formula
        self.column_formula_refs[col] = refs
        if self.has_cycle():
            if old_formula is not None:
                self.column_formulas[col] = old_formula
                self.column_formula_refs[col] = old_refs
            else:
                del self.column_formulas[col]
                del self.column_formula_refs[col]
            raise ValueError("Formula creates a dependency cycle.")
        self.recompute_all_computed()
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
        self.recompute_all_computed()
        self.save_to_history()

    def delete_column(self, col):
        if col == self.model_col_name:
            raise ValueError("Cannot delete the Model column.")
        if col in self.column_formulas:
            raise ValueError("Cannot delete a computed column. Remove formula first.")
        ref = f"{self.page_name}:{col}"
        for dm in self.all_data_models:
            for refs in dm.column_formula_refs.values():
                if any(r == col and dm == self or r == ref for r in refs):
                    raise ValueError(f"Column is used in a formula in page {dm.page_name}")
        if col in self.column_tiers:
            del self.column_tiers[col]
        self.df.drop(columns=[col], inplace=True)
        if col in self.column_types:
            del self.column_types[col]
        self.plot_columns = [c for c in self.plot_columns if c != col]
        self.save_to_history()

    def set_column_tiers(self, col, tier_mode, tiers):
        if col not in self.df.columns:
            raise ValueError("Column does not exist.")
        typ = self.column_types.get(col)
        if typ in ["integer", "float", "boolean"] and tier_mode == "string":
            raise ValueError("String mode invalid for numeric column.")
        if typ == "string" and tier_mode not in ["string"]:
            raise ValueError("Only string mode for string column.")
        self.column_tiers[col] = (tier_mode, tiers)
        self.save_to_history()

    def get_column_color(self, col, value):
        if col not in self.column_tiers:
            return QColor("transparent")
        tier_mode, tiers = self.column_tiers[col]
        try:
            if tier_mode == "string":
                value_str = str(value)
                for pattern, _, color in tiers:
                    if value_str == pattern:
                        return QColor(color)
            elif tier_mode == "min_threshold":
                value = float(value)
                for min_val, _, color in tiers:
                    if value >= min_val:
                        return QColor(color)
            elif tier_mode == "range":
                value = float(value)
                for min_val, max_val, _, color in tiers:
                    if min_val <= value <= max_val:
                        return QColor(color)
            return QColor("transparent")
        except ValueError:
            return QColor("transparent")