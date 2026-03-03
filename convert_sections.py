#!/usr/bin/env python3
"""
convert_sections.py
───────────────────
Convertit vos fichiers Excel/CSV pour les sections Mike Dyson et Mots Cools
en fichiers JSON utilisables par l'application Our Quotes.

Colonnes attendues :
  Mike Dyson  → Devinette ; Réponse ; Catégorie
  Mots Cools  → Mot ; Définition ; Catégorie ; Date d'apparition

Usage :
  python3 convert_sections.py mikedyson mon_fichier.xlsx
  python3 convert_sections.py motscools mon_fichier.csv
  python3 convert_sections.py mikedyson                    → cherche auto le fichier

Dépendances :
  pip3 install pandas openpyxl
"""

import sys
import json
import os
import glob
from pathlib import Path

try:
    import pandas as pd
except ImportError:
    print("❌  pandas manquant. Installez-le : pip3 install pandas openpyxl")
    sys.exit(1)


# ═══════════════════════════════════════════════
#  CONFIG PAR SECTION
# ═══════════════════════════════════════════════

SECTIONS = {
    "mikedyson": {
        "label": "Mike Dyson",
        "output": "data-mikedyson.json",
        "columns": {
            "devinette": ["devinette", "question", "riddle", "blague"],
            "reponse":   ["réponse", "reponse", "answer", "response"],
            "celebrite": ["célébrité", "celebrite", "celebrity", "celeb", "personnalité", "personnalite"],
            "categorie": ["catégorie", "categorie", "category", "cat"],
        },
        "json_keys": {
            "devinette": "q",
            "reponse":   "a",
            "celebrite": "celeb",
            "categorie": "cat",
        },
        "required": "devinette",
        "preview_field": "devinette",
    },
    "motscools": {
        "label": "Mots Cools",
        "output": "data-motscools.json",
        "columns": {
            "mot":        ["mot", "word", "terme"],
            "definition": ["définition", "definition", "def", "signification"],
            "categorie":  ["catégorie", "categorie", "category", "cat"],
            "date":       ["date d'apparition", "date", "apparition", "created"],
        },
        "json_keys": {
            "mot":        "word",
            "definition": "def",
            "categorie":  "cat",
            "date":       "date",
        },
        "required": "mot",
        "preview_field": "mot",
    },
}


# ═══════════════════════════════════════════════
#  UTILITAIRES
# ═══════════════════════════════════════════════

def find_file():
    """Cherche automatiquement un fichier dans le dossier courant."""
    for pattern in ["*.xlsx", "*.xls", "*.csv", "*.tsv"]:
        files = glob.glob(pattern)
        # Exclure les fichiers data-*.json et le script lui-même
        files = [f for f in files if not f.startswith("data-")]
        if files:
            return files[0]
    return None


def open_with_encoding(filepath):
    """Ouvre un fichier texte en gérant le BOM UTF-8."""
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
    """Charge un fichier Excel, CSV ou TSV en DataFrame."""
    ext = Path(filepath).suffix.lower()
    print(f"📂  Format : {ext.upper()}")

    if ext in (".xlsx", ".xls"):
        df = pd.read_excel(filepath, dtype=str).fillna("")
        return df

    raw = open_with_encoding(filepath)

    if ext == ".tsv":
        sep = "\t"
        print("    Séparateur : tabulation (TSV)")
    else:
        sample = "".join(raw[:10])
        counts = {",": sample.count(","), ";": sample.count(";"), "\t": sample.count("\t")}
        sep = max(counts, key=counts.get)
        labels = {",": "virgule", ";": "point-virgule", "\t": "tabulation"}
        print(f"    Séparateur détecté : {labels.get(sep, sep)}")

    from io import StringIO
    text = "".join(raw)

    df = pd.read_csv(
        StringIO(text),
        sep=sep,
        dtype=str,
        quotechar='"',
        doublequote=True,
        engine="python",
        on_bad_lines="warn",
    ).fillna("").apply(lambda col: col.str.strip() if col.dtype == object else col)

    return df


def match_column(df_columns, aliases):
    """Trouve la colonne correspondante parmi les alias possibles."""
    df_cols_lower = {c.lower().strip(): c for c in df_columns}
    for alias in aliases:
        if alias.lower() in df_cols_lower:
            return df_cols_lower[alias.lower()]
    return None


def clean_value(val):
    """Nettoie une valeur."""
    if pd.isna(val):
        return ""
    s = str(val).strip()
    if len(s) >= 2 and s.startswith('"') and s.endswith('"'):
        s = s[1:-1].replace('""', '"')
    return s


# ═══════════════════════════════════════════════
#  CONVERSION
# ═══════════════════════════════════════════════

def convert(section_key, filepath):
    cfg = SECTIONS[section_key]
    print(f"\n🎯  Section : {cfg['label']}")
    print(f"    Fichier : {filepath}\n")

    df = load_file(filepath)
    print(f"\n✓   {len(df)} lignes lues")
    print(f"✓   Colonnes trouvées : {list(df.columns)}\n")

    # Mapper les colonnes
    col_map = {}
    for field, aliases in cfg["columns"].items():
        matched = match_column(df.columns, aliases)
        if matched:
            col_map[field] = matched
            print(f"    ✓ {field} → « {matched} »")
        else:
            print(f"    ⚠ {field} → non trouvée (cherché : {aliases})")

    required_field = cfg["required"]
    if required_field not in col_map:
        print(f"\n❌  La colonne obligatoire « {required_field} » n'a pas été trouvée.")
        print(f"    Colonnes disponibles : {list(df.columns)}")
        print(f"    Alias acceptés : {cfg['columns'][required_field]}")
        sys.exit(1)

    # Construire les enregistrements JSON
    records = []
    skipped = 0

    for _, row in df.iterrows():
        record = {}
        for field, col_name in col_map.items():
            json_key = cfg["json_keys"][field]
            record[json_key] = clean_value(row[col_name])

        # Vérifier que le champ obligatoire n'est pas vide
        req_key = cfg["json_keys"][required_field]
        if not record.get(req_key):
            skipped += 1
            continue

        records.append(record)

    if skipped:
        print(f"\nℹ️   {skipped} ligne(s) ignorée(s) (champ obligatoire vide)")

    # Aperçu
    print(f"\n👁   Aperçu des 3 premiers éléments :")
    preview_key = cfg["json_keys"][cfg["preview_field"]]
    for r in records[:3]:
        text = (r.get(preview_key, "?") or "?")[:70]
        cat = r.get("cat", "")
        cat_str = f" [{cat}]" if cat else ""
        print(f"     {text}{cat_str}")

    # Écrire le JSON
    output_path = Path(filepath).parent / cfg["output"]
    with open(output_path, "w", encoding="utf-8") as f:
        json.dump(records, f, ensure_ascii=False, indent=2)

    print(f"\n✅  {len(records)} éléments → {output_path}")
    print(f"\n   Uploadez {cfg['output']} sur votre dépôt GitHub Pages.\n")


# ═══════════════════════════════════════════════
#  MAIN
# ═══════════════════════════════════════════════

def print_usage():
    print("Usage : python3 convert_sections.py <section> [fichier]")
    print()
    print("Sections disponibles :")
    for key, cfg in SECTIONS.items():
        cols = list(cfg["columns"].keys())
        print(f"  {key:12s} → {cfg['label']:12s}  (colonnes : {', '.join(cols)})")
        print(f"  {'':12s}   → génère {cfg['output']}")
    print()
    print("Exemples :")
    print("  python3 convert_sections.py mikedyson blagues.xlsx")
    print("  python3 convert_sections.py motscools vocabulaire.csv")
    print("  python3 convert_sections.py mikedyson              # auto-détecte le fichier")


if __name__ == "__main__":
    if len(sys.argv) < 2 or sys.argv[1] in ("-h", "--help"):
        print_usage()
        sys.exit(0)

    section = sys.argv[1].lower().replace("-", "").replace("_", "").replace(" ", "")

    if section not in SECTIONS:
        print(f"❌  Section inconnue : « {sys.argv[1]} »")
        print(f"    Sections valides : {', '.join(SECTIONS.keys())}")
        sys.exit(1)

    filepath = sys.argv[2] if len(sys.argv) > 2 else find_file()

    if not filepath:
        print("❌  Aucun fichier Excel/CSV trouvé dans le dossier.")
        print(f"    Usage : python3 convert_sections.py {section} mon_fichier.xlsx")
        sys.exit(1)

    if not os.path.exists(filepath):
        print(f"❌  Fichier introuvable : {filepath}")
        sys.exit(1)

    convert(section, filepath)
