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
        dm.page_name = "Default"
        return [dm]
    metadata = pd.read_excel(xls, 'Metadata')
    dms = []
    for _, row in metadata.iterrows():
        page_name = row['page_name']
        df = pd.read_excel(xls, page_name)
        dm = data_model.DataModel()
        dm.page_name = page_name
        dm.df = df.fillna('')
        dm.set_column_types()
        # Load formulas
        if 'formulas_str' in row and pd.notna(row['formulas_str']):
            strs = row['formulas_str'].split('|')
            for s in strs:
                if not s.strip():
                    continue
                if ':' in s:
                    c, f = s.split(':', 1)
                    dm.column_formulas[c] = f.replace('||', '|')
                    dm.column_formula_refs[c] = set(re.findall(r'\{(.*?)\}', dm.column_formulas[c]))
        # Load tiers
        if 'tiers_str' in row and pd.notna(row['tiers_str']):
            strs = row['tiers_str'].split('|')
            for s in strs:
                if not s.strip():
                    continue
                parts = s.split(':')
                c = parts[0]
                typ_tiers = parts[1]
                typ, tiers_str = typ_tiers.split(';', 1)
                if typ == 'a':
                    tier_mode = "min_threshold"
                elif typ == 'p':
                    tier_mode = "range"
                elif typ == 's':
                    tier_mode = "string"
                else:
                    continue
                tier_list = []
                tier_strs = tiers_str.split(';')
                for ts in tier_strs:
                    if not ts.strip():
                        continue
                    if '~' in ts:
                        tp = ts.split('~')
                    else:
                        tp = ts.split(',')
                    if tier_mode == "min_threshold":
                        minv = float(tp[0])
                        label = tp[1]
                        color = tp[2]
                        tier_list.append((minv, label, color))
                    elif tier_mode == "range":
                        minv = float(tp[0])
                        max_str = tp[1]
                        maxv = float('inf') if max_str == 'inf' else float(max_str)
                        label = tp[2]
                        color = tp[3]
                        tier_list.append((minv, maxv, label, color))
                    elif tier_mode == "string":
                        pattern = tp[0]
                        label = tp[1]
                        color = tp[2]
                        tier_list.append((pattern, label, color))
                dm.column_tiers[c] = (tier_mode, tier_list)
        # Backwards compat
        if 'score_col' in row and pd.notna(row['score_col']):
            score_col = row['score_col']
            formula = row['formula'] if pd.notna(row['formula']) else ""
            if formula:
                dm.column_formulas[score_col] = formula
                dm.column_formula_refs[score_col] = set(re.findall(r'\{(.*?)\}', formula))
            if 'score_tiers_str' in row and pd.notna(row['score_tiers_str']):
                strs = row['score_tiers_str'].split('|')
                tiers = []
                for s in strs:
                    if '~' in s:
                        parts = s.split('~')
                    else:
                        parts = s.split(',')
                    minv = float(parts[0])
                    label = parts[1]
                    color = parts[2]
                    tiers.append((minv, label, color))
                dm.column_tiers[score_col] = ("min_threshold", sorted(tiers, key=lambda x: x[0], reverse=True))
        if 'penalty_col' in row and pd.notna(row['penalty_col']):
            penalty_col = row['penalty_col']
            if 'penalty_tiers_str' in row and pd.notna(row['penalty_tiers_str']):
                strs = row['penalty_tiers_str'].split('|')
                tiers = []
                for s in strs:
                    if '~' in s:
                        parts = s.split('~')
                    else:
                        parts = s.split(',')
                    minv = float(parts[0])
                    maxv = float(parts[1]) if parts[1] != 'inf' else float('inf')
                    label = parts[2]
                    color = parts[3]
                    tiers.append((minv, maxv, label, color))
                dm.column_tiers[penalty_col] = ("range", sorted(tiers, key=lambda x: x[0]))
        dm.plot_columns = row['plot_columns'].split(',') if 'plot_columns' in row and pd.notna(row['plot_columns']) else []
        dms.append(dm)
    return dms

def save_multi(dms, session_file):
    with pd.ExcelWriter(session_file) as writer:
        metadata = []
        for dm in dms:
            meta = {'page_name': dm.page_name}
            formulas_str = '|'.join([f"{c}:{f.replace('|', '||')}" for c, f in dm.column_formulas.items()])
            meta['formulas_str'] = formulas_str if formulas_str else None
            tiers_str_list = []
            for c, (tier_mode, tiers) in dm.column_tiers.items():
                inner = []
                if tier_mode == "min_threshold":
                    typ = 'a'
                    for tier in tiers:
                        ts = ','.join([str(tier[0]), tier[1], tier[2]])
                        inner.append(ts)
                elif tier_mode == "range":
                    typ = 'p'
                    for tier in tiers:
                        max_str = 'inf' if tier[1] == float('inf') else str(tier[1])
                        ts = ','.join([str(tier[0]), max_str, tier[2], tier[3]])
                        inner.append(ts)
                elif tier_mode == "string":
                    typ = 's'
                    for tier in tiers:
                        ts = ','.join([tier[0], tier[1], tier[2]])
                        inner.append(ts)
                tiers_inner = ';'.join(inner)
                tiers_str_list.append(f"{c}:{typ};{tiers_inner}")
            tiers_str = '|'.join(tiers_str_list)
            meta['tiers_str'] = tiers_str if tiers_str else None
            meta['plot_columns'] = ','.join(dm.plot_columns) if dm.plot_columns else None
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