# 📖 Guide complet — Our Quotes

## Ce que contient ce dossier

### Fichiers de production (obligatoires)

| Fichier | Rôle |
|---|---|
| `index.html` | L'application complète — HTML + CSS + JS tout-en-un |
| `data.json` | Base de données des citations (section Our Quotes) |
| `sw.js` | Service Worker — mode hors-ligne |
| `manifest.json` | Rend l'app installable sur iPhone (PWA) |
| `icon.jpg` | Icône de l'app |

Ces **5 fichiers** suffisent pour déployer l'app sur GitHub Pages.

### Fichiers des sections supplémentaires (optionnels)

| Fichier | Rôle |
|---|---|
| `data-mikedyson.json` | Base de données Mike Dyson (devinettes) |
| `data-motscools.json` | Base de données Mots Cools (vocabulaire) |

### Scripts de conversion

| Fichier | Rôle |
|---|---|
| `convert_to_json.py` | Convertit l'Excel/CSV Our Quotes → `data.json` |
| `convert_sections.py` | Convertit l'Excel/CSV Mike Dyson ou Mots Cools → JSON |

### Fichiers de développement (pas nécessaires en production)

| Fichier | Rôle |
|---|---|
| `demo.html` | Version testable offline (données inlinées, pas besoin de serveur) |
| `vue-demo.html` | Prototype Vue 3 multi-sections (3 sections avec composants) |
| `GUIDE.md` | Ce fichier |

---

## Étape 1 — Convertir vos données

### Our Quotes (section principale)

1. Exportez votre Google Sheets en CSV ou Excel
2. Placez le fichier dans le même dossier que `convert_to_json.py`
3. Lancez :

```bash
python3 convert_to_json.py mon_fichier.csv
```

→ Génère `data.json`

### Mike Dyson (devinettes)

Votre Excel doit contenir ces colonnes : **Devinette**, **Réponse**, **Catégorie**

```bash
python3 convert_sections.py mikedyson mon_fichier_mikedyson.xlsx
```

→ Génère `data-mikedyson.json` avec les clés `q` (devinette), `a` (réponse), `cat` (catégorie)

### Mots Cools (vocabulaire)

Votre Excel doit contenir ces colonnes : **Mot**, **Définition**, **Catégorie**, **Date d'apparition**

```bash
python3 convert_sections.py motscools mon_fichier_motscools.xlsx
```

→ Génère `data-motscools.json` avec les clés `word`, `def`, `cat`, `date`

### Notes sur les conversions

- Les noms de colonnes sont insensibles à la casse et aux accents
- Le séparateur CSV est auto-détecté (virgule, point-virgule, tabulation)
- Les fichiers Excel `.xlsx` et `.xls` sont supportés
- L'encodage UTF-8 avec BOM est géré automatiquement
- Lancez `python3 convert_sections.py --help` pour voir toutes les options

---

## Étape 2 — Héberger sur GitHub Pages

### Créer le dépôt GitHub
1. [github.com](https://github.com) → **New repository**
2. Nom : `quoteapp` (ou ce que vous voulez)
3. Cochez **Public**
4. **Create repository**

### Uploader les fichiers
Glissez-déposez dans le dépôt :
- `index.html`
- `manifest.json`
- `sw.js`
- `icon.jpg`
- `data.json`
- `data-mikedyson.json` (si section activée)
- `data-motscools.json` (si section activée)

### Activer GitHub Pages
1. **Settings → Pages**
2. Branch : **main**, dossier **/ (root)**
3. **Save** → votre URL : `https://VOTRE-PSEUDO.github.io/quoteapp/`

---

## Étape 3 — Installer sur iPhone

1. Ouvrez **Safari** (obligatoirement Safari sur iOS)
2. Allez sur votre URL GitHub Pages
3. **Partager** (carré avec flèche) → **Sur l'écran d'accueil**
4. Nommez le raccourci → **Ajouter**

---

## Étape 4 — Mettre à jour les données

```bash
# Reconvertir les données
python3 convert_to_json.py mon_fichier.csv
python3 convert_sections.py mikedyson blagues.xlsx
python3 convert_sections.py motscools vocabulaire.xlsx

# Pousser sur GitHub
git add data.json data-mikedyson.json data-motscools.json
git commit -m "Mise à jour données"
git push
```

---

## Architecture de l'application

### Version actuelle : Vanilla JS (index.html)

L'app est un SPA monofichier. Tout le HTML, CSS et JavaScript sont dans `index.html`. Pas de framework, pas de build, pas de bundler.

**Onglets :**
- 🎲 **Phrases** — affichage aléatoire, navigation swipe, détails, favoris
- 📊 **Stats** — statistiques par auteur, catégorie, timeline
- 🎮 **Jeu** — quiz avec système XP/rangs inspiré CodePet
- ⏳ **Historique** — toutes les phrases avec recherche et filtres
- ❤️ **Favoris** — phrases sauvegardées

**Onglet Jeu — Système XP :**
- 🥚 Newbie (0 XP) → 🐣 Connaisseur (50) → 🤔 Expert (150) → 🦅 Maître (350) → 👑 Légende (700)
- Deux modes : "Qui a dit ?" (10 XP + bonus série) et "Finis la phrase" (15 XP + bonus série)
- Barre de progression animée, emoji bounce, pop "+XP" flottant
- Historique des 8 dernières réponses, XP persisté en localStorage

### Version future : Vue 3 (vue-demo.html)

Le prototype multi-sections utilise des composants Vue réactifs et un store par section. Chaque section a sa couleur accent et son `colMap` pour mapper les colonnes JSON.

**Migration prévue :** Quand les données Mike Dyson et Mots Cools seront prêtes, `vue-demo.html` deviendra le nouveau `index.html`.

---

## Personnalisation

### Changer le nom
Dans `manifest.json` : `"name": "VotreNom"` et `"short_name": "Court"`

Dans `index.html` : `<title>QuoteApp</title>`

### Changer la couleur accent
Dans `index.html`, dans le CSS : `--accent: #7c6af7;`

---

## Questions fréquentes

**Mon CSV ne se charge pas ?**
→ Vérifiez l'encodage UTF-8. L'export Google Sheets est déjà en UTF-8.

**`python3` introuvable ?**
→ `brew install python` ou [python.org](https://www.python.org/downloads/macos/)

**L'app ne se met pas à jour sur iPhone ?**
→ Fermez/rouvrez l'app, ou Réglages → Safari → Effacer historique.

**Comment tester sans serveur ?**
→ Ouvrez `demo.html` directement dans votre navigateur.

**Quels fichiers CSS séparés ?**
→ Il n'y en a plus. Tout le CSS est dans `index.html`. Les anciens fichiers du dossier `refactor/` peuvent être supprimés.
