# file_io.py
import os
import pandas as pd

def load_df(session_file):
    if os.path.exists(session_file):
        df = pd.read_csv(session_file)
        if "Behavior" in df.columns:
            df = df.drop(columns=["Behavior"])
        if "Abnormal" in df.columns:
            df = df.rename(columns={"Abnormal": "Abnormal Behavior"})
        df = df.fillna('')
        return df
    return pd.DataFrame(columns=["Model", "Retrieval", "Abnormal Behavior", "Overall"])

def save_df(df, session_file):
    df.to_csv(session_file, index=False)

def load_formula(formula_file):
    if os.path.exists(formula_file):
        with open(formula_file, 'r') as f:
            return f.read().strip()
    return "{Retrieval} - {Abnormal Behavior}"

def save_formula(formula, formula_file):
    with open(formula_file, 'w') as f:
        f.write(formula)

def import_df(path):
    if path.endswith('.csv'):
        df = pd.read_csv(path)
    else:
        df = pd.read_excel(path)
    if "Behavior" in df.columns:
        df = df.drop(columns=["Behavior"])
    if "Abnormal" in df.columns:
        df = df.rename(columns={"Abnormal": "Abnormal Behavior"})
    return df

def export_df(df, path):
    df.to_csv(path, index=False)