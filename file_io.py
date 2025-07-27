# file_io.py
import os
import pandas as pd
import re
import data_model

def load_multi(session_file):
    if not os.path.exists(session_file):
        dm = data_model.DataModel()
        return [dm]
    xls = pd.ExcelFile(session_file)
    if 'Metadata' not in xls.sheet_names:
        # Treat as single sheet
        df = pd.read_excel(session_file)
        dm = data_model.DataModel()
        dm.df = df.fillna('')
        dm.set_column_types()
        dm.score_formula = ""  # Default
        dm.formula_cols = set()
        dm.page_name = "Default"
        return [dm]
    metadata = pd.read_excel(xls, 'Metadata')
    dms = []
    for _, row in metadata.iterrows():
        page_name = row['page_name']
        formula = row['formula'] if pd.notna(row['formula']) else ""
        score_col = row['score_col'] if pd.notna(row['score_col']) else None
        penalty_col = row['penalty_col'] if pd.notna(row['penalty_col']) else None
        df = pd.read_excel(xls, page_name)
        dm = data_model.DataModel()
        dm.page_name = page_name
        dm.df = df.fillna('')
        dm.set_column_types()
        dm.score_formula = formula
        dm.formula_cols = set(re.findall(r'\{(.*?)\}', formula))
        dm.score_col = score_col
        dm.penalty_col = penalty_col
        dm.recompute_all_overall()
        # Load tiers
        if 'score_tiers_str' in row and pd.notna(row['score_tiers_str']):
            strs = row['score_tiers_str'].split('|')
            tiers = []
            for s in strs:
                parts = s.split(',', 2)
                minv = float(parts[0])
                label = parts[1]
                color = parts[2]
                tiers.append((minv, label, color))
            dm.score_tiers = sorted(tiers, key=lambda x: x[0], reverse=True)
        if 'penalty_tiers_str' in row and pd.notna(row['penalty_tiers_str']):
            strs = row['penalty_tiers_str'].split('|')
            tiers = []
            for s in strs:
                parts = s.split(',', 3)
                minv = float(parts[0])
                maxv = float(parts[1])
                label = parts[2]
                color = parts[3]
                tiers.append((minv, maxv, label, color))
            dm.penalty_tiers = sorted(tiers, key=lambda x: x[0])
        dms.append(dm)
    return dms

def save_multi(dms, session_file):
    with pd.ExcelWriter(session_file) as writer:
        metadata = []
        for dm in dms:
            meta = {'page_name': dm.page_name, 'formula': dm.score_formula}
            meta['score_col'] = dm.score_col
            meta['penalty_col'] = dm.penalty_col
            meta['score_tiers_str'] = '|'.join([f"{m},{l},{c}" for m, l, c in dm.score_tiers])
            meta['penalty_tiers_str'] = '|'.join([f"{m},{mx},{l},{c}" for m, mx, l, c in dm.penalty_tiers])
            metadata.append(meta)
        pd.DataFrame(metadata).to_excel(writer, sheet_name='Metadata', index=False)
        for dm in dms:
            dm.df.to_excel(writer, sheet_name=dm.page_name, index=False)

def import_df(path):
    if path.endswith('.csv'):
        df = pd.read_csv(path)
    else:
        df = pd.read_excel(path)
    return df

def export_df(df, path):
    df.to_csv(path, index=False)