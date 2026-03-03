# 🗺️ ROADMAP — Our Quotes App

> Dernière mise à jour : 2 mars 2026
> État actuel : **Phase 4 terminée — données réelles intégrées**

---

## Vue d'ensemble

```
PHASE 1 — Refactor vanilla          ██████████  ✅ Terminé
PHASE 2 — Quick wins (Jeu + Share)  ██████████  ✅ Terminé
PHASE 3 — Migration Vue 3           ██████████  ✅ Terminé
PHASE 4 — Nouvelles sections        ██████████  ✅ Terminé (données réelles intégrées)
PHASE 5 — Polish & finitions        ██████████  ✅ Terminé
PHASE 6 — Jeu v2 (XP & rangs)      ██████████  ✅ Terminé
```

---

## PHASE 1 — Refactor vanilla (sessions 1-2)

Objectif : rendre le code modulaire SANS changer de framework, pour préparer la migration et ne rien casser en production.

### 1.1 Extraire un SectionEngine générique ✅
- [x] `SectionEngine(config)` dans `js/engine.js` — paramétrable par section
- [x] Config = `{ id, dataUrl, colMap, storagePrefix, filters[] }`
- [x] Méthodes : `fetchData`, `initData`, `getNext`, `applyFilters`, `toggleFilter`, `resetFilters`, `toggleFavorite`, `isFavorite`, `getFrequency`, `getDailyQuote`
- [x] La section "Our Quotes" = `new SectionEngine(QUOTES_CONFIG)` dans `js/quotes-config.js`

### 1.2 Séparer le state par section ✅
- [x] `createStore(prefix)` dans `js/store.js` — state isolé avec persistence localStorage
- [x] `stores.quotes` = `quotesEngine.store` avec allData, filtered, history, favs, queue, activeFilters
- [x] Alias `App` backward-compatible dans `quotes-config.js` (getters/setters vers le store)
- [x] Chaque store a son propre `storagePrefix` pour localStorage

### 1.3 Découpler le DOM — PARTIEL
- [x] Fonctions utilitaires extraites dans `js/core.js` (esc, getCol, parseDate, formatDate, timeAgo, showToast, loadChartJS)
- [x] Popups extraits dans `js/popups.js` (PopupQueue, code, update, install)
- [ ] ~1 200 lignes de UI rendering restent inline (couplées au DOM) — seront migrées vers composants Vue en Phase 3

### 1.4 Fichiers multiples ✅
- [x] Structure multi-fichiers opérationnelle :
  ```
  index.html              1 495 lignes (shell HTML + UI JS inline)
  css/tokens.css             78 lignes
  css/layout.css            118 lignes
  css/quote.css             334 lignes
  css/filters.css           209 lignes
  css/stats.css             207 lignes
  css/history.css           144 lignes
  css/nav.css                41 lignes
  css/components.css        329 lignes
  js/core.js                 83 lignes (utilities)
  js/store.js                80 lignes (SectionStore)
  js/engine.js              147 lignes (SectionEngine)
  js/popups.js              113 lignes (PopupQueue)
  js/quotes-config.js        65 lignes (config + App alias)
  ```
- [x] Aucun build step — chargement via `<link>` et `<script>` directs

---

## PHASE 2 — Quick wins en vanilla (sessions 3-4)

Objectif : livrer des features visibles avant la migration framework.

### 2.1 Onglet Jeu ✅
- [x] Mode "Qui a dit ?" : phrase affichée, 4 choix d'auteurs
- [x] Mode "Finis la phrase" : début affiché (~55%), compléter le reste, fuzzy match >50%
- [x] Scoring : score courant, streak 🔥, meilleur score ⭐ en localStorage
- [x] UI : même design que les cards actuelles, grid 2×2 pour les choix
- [x] Écran accessible via un 4ème onglet nav (🧠 jeu)

### 2.2 Web Share API ✅
- [x] Bouton ↗ partager sur l'écran quote (entre "Ménestrel" et "Filtrer")
- [x] `navigator.share({ title, text })` si supporté (iOS, Android)
- [x] Fallback : copier dans le presse-papier + toast "📋 Copié"
- [x] Format partagé : `« phrase » \n— Auteur · Lieu`

### 2.3 Améliorations UX en attente
- [ ] Safe-area padding audit complet
- [x] Animations de transition entre onglets (déjà en place via opacity transition)
- [ ] Skeleton loading pour stats

---

## PHASE 3 — Migration Vue 3 (sessions 5-8)

Objectif : passer sur Vue 3 pour supporter les sections multiples sans duplication.

### 3.1 Setup technique ✅
- [x] Vue 3 via CDN (ESM) + importmap — zéro build step, compatible GitHub Pages
- [x] Pinia pour state management — store factory paramétrable par section
- [x] Structure multi-fichiers :
  ```
  index.html                         130 lignes (shell + CSS section-tabs + popups HTML)
  js/core.js                          67 lignes (utilitaires globaux)
  js/app.js                          175 lignes (createApp + Pinia + popups + SW)
  js/stores/sectionStore.js          200 lignes (store factory générique)
  js/stores/sections.js               82 lignes (configs Quotes/MikeDyson/MotsCools)
  js/components/SectionView.js        84 lignes (wrapper onglets par section)
  js/components/RandomCard.js        122 lignes (affichage item + fav + share)
  js/components/FilterPanel.js        95 lignes (filtres paramétrables)
  js/components/StatsView.js         192 lignes (overview + charts)
  js/components/HistoryList.js        67 lignes (historique swipeable)
  js/components/QuizGame.js          137 lignes (jeu qui a dit / finis la phrase)
  js/components/FavSheet.js           51 lignes (bottom sheet favoris)
  js/components/PopupQueue.js        178 lignes (code + update + install)
  css/ (9 fichiers)                1 645 lignes (tokens, layout, screens, game)
  sw.js                               66 lignes (cache v4, stale-while-revalidate)
  ```

### 3.2 Composants réutilisables ✅
- [x] `<SectionView>` — wrapper qui orchestre tous les onglets d'une section
- [x] `<RandomCard>` — affiche item avec animation, fav, share
- [x] `<FilterPanel>` — filtres paramétrables via config.filters, collapsibles
- [x] `<HistoryList>` — liste avec timeAgo, indicateur favori, clic pour afficher
- [x] `<StatsView>` — overview 4 cards + phrase du jour + 3 charts (auteurs, catégories, timeline)
- [x] `<FavSheet>` — bottom sheet favoris
- [x] `<QuizGame>` — 2 modes (qui a dit / finis la phrase), scoring avec streak/best
- [x] `<PopupQueue>` — code d'accès + update SW + install PWA, séquentiel
- [x] Share intégré dans RandomCard (navigator.share + fallback clipboard)

### 3.3 Migrer la section "Our Quotes" ✅
- [x] Config complète dans sections.js (colMap, 6 filtres, labels)
- [x] Store Pinia créé via createSectionStore('quotes', QUOTES_CONFIG)
- [x] Tous les écrans convertis en composants Vue
- [x] Tests en conditions réelles — à valider au premier déploiement

### 3.4 Navigation multi-sections ✅
- [x] Tab bar principal : Quotes / Mike Dyson / Mots Cools (section-tabs)
- [x] Tab bar secondaire par section : phrases / stats / jeu / historique
- [x] Couleur accent dynamique par section (violet / vert / cyan)
- [x] Lazy-load des données au premier switch de section
- [x] État conservé pour chaque section (v-show, pas v-if)

---

## PHASE 4 — Nouvelles sections (sessions 9-11)

Objectif : ajouter Mike Dyson et Mots Cools en réutilisant les composants.

### 4.1 Section Mike Dyson ✅
- [x] Config `MIKEDYSON_CONFIG` (colMap, 2 filtres, accent vert #4ade80)
- [x] Store réactif créé automatiquement par `createStore(cfg)`
- [x] `data-mikedyson.json` : **20 devinettes réelles** (jeux de mots sur célébrités)
- [x] Colonnes : `q` (devinette), `a` (réponse), `cat` (catégorie)
- [x] 9 catégories : Popstars, Cinéma, Fictifs, Histoire, Humoriste, Légende, Philosophie, Politique, Sport
- [x] Script de conversion dédié : `convert_sections.py mikedyson fichier.xlsx`
- [x] Navigation, jeu, stats, filtres fonctionnels via composants partagés

### 4.2 Section Mots Cools ✅
- [x] Config `MOTSCOOLS_CONFIG` (colMap simplifié mot/def/cat, accent cyan #22d3ee)
- [x] Store réactif créé automatiquement
- [x] `data-motscools.json` : **127 mots réels** (vocabulaire rare avec définitions)
- [x] Colonnes : `word` (mot), `def` (définition), `cat` (catégorie grammaticale), `date` (époque d'apparition)
- [x] 15 catégories grammaticales : nom masculin/féminin, adjectif, verbe, locution, etc.
- [x] Script de conversion dédié : `convert_sections.py motscools fichier.xlsx`
- [x] Affichage adapté : "mot" comme texte, "définition" comme auteur

### 4.3 Multi-database dans le SW ✅
- [x] `sw.js` v4 pré-cache les 3 fichiers JSON + tous les assets Vue
- [x] Stratégie stale-while-revalidate pour les assets, network-first pour HTML

---

## PHASE 5 — Polish & finitions (sessions 12-13)

### 5.1 Thème par section ✅
- [x] Couleur accent dynamique : violet (quotes), vert (mike dyson), cyan (mots cools)
- [x] Header adaptatif avec nom de section (config.label.toUpperCase())
- [x] Icônes distinctes par section (🎲 / 🎤 / 💎) dans les tabs

### 5.2 Performance ✅
- [x] Lazy-load des sections non actives (v-show + fetchData au premier switch)
- [x] Service Worker v4 avec cache des 3 JSON + tous les assets
- [ ] Audit Lighthouse PWA (à faire post-déploiement)

### 5.3 Expérience ✅
- [x] Confetti burst 🎉 sur bonne réponse au quiz (20 particules, 6 couleurs, 1.2s)
- [x] Micro-animations : correctPulse (scale), wrongShake (translateX), nav ripple
- [x] Transitions écrans : opacity 0.22s + translateY(4px)
- [x] Section tab indicator animé (underline transition)
- [x] Loading skeleton CSS prêt
- [x] Code d'accès popup dans version Vue (code 6 digits, validation, séquentiel)
- [x] Install PWA popup avec "ne plus rappeler"
- [x] Onboarding première visite : 8 étapes animées (slide horizontal), « Passer » ou « Suivant → »
- [x] Toggle dark/light mode : bouton ☀️/🌙 dans le header, persisté en localStorage
- [x] Historique : suppression de l'opacité dégressive sur les items

---

## PHASE 6 — Jeu v2 : XP & progression (session 14)

Objectif : refonte complète de l'onglet jeu avec un système de progression inspiré de CodePet.

### 6.1 Système XP & rangs ✅
- [x] 5 rangs de progression : 🥚 Newbie (0) → 🐣 Connaisseur (50) → 🤔 Expert (150) → 🦅 Maître (350) → 👑 Légende (700)
- [x] XP par bonne réponse : "Qui a dit ?" = 10 XP, "Finis la phrase" = 15 XP
- [x] Bonus de série (streak) : +2 XP par réponse consécutive (max +20)
- [x] XP persisté dans localStorage (`qapp_game_xp`)
- [x] Progression calculée dynamiquement vers le rang suivant

### 6.2 UI CodePet-style ✅
- [x] Carte XP centrale avec glow radial, emoji de rang, nom + description
- [x] Barre de progression gradient (accent → rose) avec pourcentage animé
- [x] Animation bounce de l'emoji sur bonne réponse
- [x] Pop "+XP" flottant avec animation fadeUp
- [x] Stats row : 3 mini-cards (Score / Série 🔥 / Record ⭐)
- [x] Historique d'activité : 8 dernières réponses avec icône, texte, XP, timestamp

### 6.3 Implémentation multi-versions ✅
- [x] Vanilla JS : `index.html` + `demo.html` (CSS game-pet-card, JS GAME_RANKS + addGameXP)
- [x] Vue 3 : `vue-demo.html` (composant QuizGame avec computed rank/xpPct, store.addGameXP)
- [x] Light mode CSS ajouté pour toutes les nouvelles classes game-*

### 6.4 Scripts de conversion sections ✅
- [x] `convert_sections.py` : script dédié pour Mike Dyson et Mots Cools
- [x] Mike Dyson : colonnes Devinette / Réponse / Célébrité / Catégorie → `q`, `a`, `celeb`, `cat`
- [x] Mots Cools : colonnes Mot / Définition / Catégorie / Date d'apparition → `word`, `def`, `cat`, `date`
- [x] Auto-détection séparateur, encodage, matching colonnes flexible

---

## Versioning

À chaque deploy, incrémenter :
- `CACHE_VERSION` dans `sw.js`
- `APP_VERSION` dans `index.html` (déclenche re-saisie du code d'accès)

---

## Décisions techniques

| Décision | Choix | Raison |
|---|---|---|
| Framework | Vue 3 (CDN global) | Réactivité native, zéro build step, GitHub Pages direct |
| State | Vue.reactive() | Plus simple que Pinia sans build step, store factory paramétrable |
| Navigation | Section tabs + sub-tabs | Pas besoin de Vue Router, v-show conserve l'état |
| Build | Aucun (CDN) | Compatible GitHub Pages, zéro config, importmap si besoin |
| CSS | Design tokens + fichiers séparés | Cohérent, maintenable, même tokens partout |
| Data | JSON statique par section | Simple, cacheable, compatible SW |
| Animations | CSS keyframes + JS confetti | Léger, performant, pas de lib externe |
| XP / Rangs | 5 paliers, bonus streak | Gamification progressive, motivant sur le long terme |
| Conversion | Scripts Python dédiés | Un par type de section, auto-détection format/encodage |

---

## Inventaire des données

| Section | Fichier | Items | Clés JSON | Catégories |
|---|---|---|---|---|
| Our Quotes | `data.json` | 506 | vol, date, q, name, loc, cat1, cat2, alc, ctx, wam | Neutre, Beauf, Absurde, Raciste, Classy, etc. |
| Mike Dyson | `data-mikedyson.json` | 20 | q, a, cat | Popstars, Cinéma, Fictifs, Histoire, Sport, etc. |
| Mots Cools | `data-motscools.json` | 127 | word, def, cat, date | nom masculin/féminin, adjectif, verbe, etc. |
