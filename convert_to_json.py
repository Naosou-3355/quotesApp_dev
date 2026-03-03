#!/usr/bin/env python3
"""
convert_to_json.py
──────────────────
Convertit votre fichier Excel, CSV ou TSV (Google Sheets) en data.json
utilisable par l'application QuoteApp.

Problèmes résolus :
  ✓ Accents et caractères français (UTF-8 avec BOM géré automatiquement)
  ✓ Virgules dans les phrases (guillemets RFC 4180 ou format TSV)
  ✓ Séparateur auto-détecté (virgule, point-virgule, tabulation)

Usage :
  python convert_to_json.py                     → cherche auto le fichier
  python convert_to_json.py mon_fichier.csv     → CSV spécifique
  python convert_to_json.py mon_fichier.tsv     → TSV (recommandé)
  python convert_to_json.py mon_fichier.xlsx    → Excel

Dépendances :
  pip install pandas openpyxl
"""

import sys
import json
import os
import csv
import glob
from pathlib import Path

try:
    import pandas as pd
except ImportError:
    print("❌  pandas manquant. Installez-le : pip install pandas openpyxl")
    sys.exit(1)


def find_file():
    """Cherche automatiquement un fichier dans le dossier courant, TSV en priorité."""
    for pattern in ["*.tsv", "*.csv", "*.xlsx", "*.xls"]:
        files = glob.glob(pattern)
        if files:
            return files[0]
    return None


def open_with_encoding(filepath):
    """
    Ouvre le fichier texte en gérant le BOM UTF-8 (0xEF 0xBB 0xBF).
    Ce BOM est ajouté silencieusement par Google Sheets et Excel Windows.
    Sans gestion, il crée le caractère parasite 'ï»¿' en tête du fichier,
    ce qui empêche de reconnaître le nom de la première colonne (Horodateur, etc.).
    'utf-8-sig' est l'encodage Python qui strips automatiquement ce BOM.
    """
    encodings = ["utf-8-sig", "utf-8", "latin-1", "cp1252"]
    for enc in encodings:
        try:
            with open(filepath, "r", encoding=enc, newline="") as f:
                lines = f.readlines()
            print(f"    Encodage détecté : {enc}")
            return lines
        except (UnicodeDecodeError, LookupError):
            continue
    raise ValueError("Impossible de lire le fichier — encodage non reconnu.")


def load_file(filepath):
    ext = Path(filepath).suffix.lower()
    print(f"📂  Format : {ext.upper()}")

    if ext in (".xlsx", ".xls"):
        df = pd.read_excel(filepath, dtype=str).fillna("")
        return df

    raw = open_with_encoding(filepath)

    if ext == ".tsv":
        sep = "\t"
        print("    Séparateur : tabulation (TSV — virgules dans les phrases OK)")
    else:
        sample = "".join(raw[:10])
        counts = {",": sample.count(","), ";": sample.count(";"), "\t": sample.count("\t")}
        sep = max(counts, key=counts.get)
        labels = {",": "virgule", ";": "point-virgule", "\t": "tabulation"}
        print(f"    Séparateur détecté : {labels[sep]}")

    from io import StringIO
    text = "".join(raw)

    df = pd.read_csv(
        StringIO(text),
        sep=sep,
        dtype=str,
        quotechar='"',          # champs avec virgules encadrés par guillemets doubles (RFC 4180)
        doublequote=True,       # "" dans un champ = guillemet littéral
        engine="python",        # parser plus robuste pour les cas limites
        on_bad_lines="warn",
    ).fillna("").apply(lambda col: col.str.strip() if col.dtype == object else col)

    return df


def clean_value(val):
    if pd.isna(val):
        return ""
    s = str(val).strip()
    # Supprime les guillemets résiduels encadrants (cas rares d'exports non-standard)
    if len(s) >= 2 and s.startswith('"') and s.endswith('"'):
        s = s[1:-1].replace('""', '"')
    return s


# ── Mapping clés verbeuses → clés compactes ──
# Réduit la taille de data.json de ~27%
# L'app (index.html) attend ces clés courtes
KEY_MAP = {
    'volume':              'vol',
    'horodateur':          'date',
    'insert quote':        'q',
    'insert name':         'name',
    'insert location':     'loc',
    'main category':       'cat1',
    'second category':     'cat2',
    'under alcohol':       'alc',
    'context':             'ctx',
    'si wam':              'wam',
}


def compact_key(col_name):
    """Mappe un nom de colonne Google Sheets vers sa clé compacte."""
    lower = col_name.lower().strip()
    for pattern, short in KEY_MAP.items():
        if lower.startswith(pattern):
            return short
    return col_name  # fallback: garder tel quel


def convert(filepath):
    df = load_file(filepath)
    print(f"\n✓   {len(df)} lignes lues")
    print(f"✓   Colonnes : {list(df.columns)}\n")

    quote_cols = [c for c in df.columns if any(kw in c.lower() for kw in ["quote", "phrase"])]
    if not quote_cols:
        print("⚠️   Colonne 'Insert quote' non trouvée — toutes les lignes seront exportées.")

    # Build key mapping for this file's columns
    col_map = {col: compact_key(col) for col in df.columns}
    mapped_cols = {v: k for k, v in col_map.items()}
    print(f"🔑  Mapping des clés :")
    for orig, short in col_map.items():
        if orig != short:
            print(f"     {orig}  →  {short}")

    records, skipped = [], 0
    for _, row in df.iterrows():
        record = {col_map[col]: clean_value(row[col]) for col in df.columns}
        # Check for empty quote using the mapped key
        q_key = col_map.get(quote_cols[0]) if quote_cols else None
        if q_key and not record.get(q_key):
            skipped += 1
            continue
        records.append(record)

    if skipped:
        print(f"ℹ️   {skipped} ligne(s) ignorée(s) (phrase vide)")

    # Aperçu
    print(f"\n👁   Aperçu des 3 premières phrases :")
    for r in records[:3]:
        q = (r.get('q', '?') or '?')[:70]
        a = r.get('name', '?')
        print(f"     [{a}]  {q}")

    output_path = Path(filepath).parent / "data.json"
    with open(output_path, "w", encoding="utf-8") as f:
        json.dump(records, f, ensure_ascii=False, indent=2)

    size_kb = output_path.stat().st_size / 1024
    print(f"\n✅  {len(records)} phrases → {output_path} ({size_kb:.0f} ko)")
    print("\n   Uploadez ce data.json sur votre dépôt GitHub Pages pour mettre à jour l'app.\n")


if __name__ == "__main__":
    filepath = sys.argv[1] if len(sys.argv) > 1 else find_file()

    if not filepath:
        print("❌  Aucun fichier CSV/TSV/Excel trouvé dans le dossier.")
        print("    Usage : python convert_to_json.py mon_fichier.tsv")
        sys.exit(1)

    if not os.path.exists(filepath):
        print(f"❌  Fichier introuvable : {filepath}")
        sys.exit(1)

    convert(filepath)
