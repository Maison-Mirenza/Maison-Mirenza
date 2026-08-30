# Maison Mirenza — site

Site statique de **Maison Mirenza**, généré à partir de données (JSON) par un petit
générateur Python. Le rendu final est généré dans `docs/` au moment du build. Le dossier `docs/` n’est plus versionné :
**GitHub Actions le construit et le déploie directement sur GitHub Pages**, ce qui évite de dupliquer les médias vidéo.

> Philosophie : construire une **Maison** avant une boutique, un **système de recherche**
> avant des arguments — puis, au moment exact du choix produit, rendre la décision simple.

---

## 1. Déploiement sur GitHub Pages

1. Créez un dépôt GitHub vide et envoyez **le contenu de ce dossier** (pas le ZIP comme un fichier unique).
2. Dans GitHub : **Settings → Pages → Build and deployment → Source : GitHub Actions**.
3. Chaque push sur `main` lance `.github/workflows/build.yml`, construit `docs/` puis publie le site.

> Les vidéos ne sont conservées qu’une seule fois dans `src/media/`. `docs/` est un artefact de build temporaire et n’est pas versionné.

## 2. Reconstruire le site

Nécessite **Python 3.10+** (aucune dépendance externe pour le build ; `Pillow` uniquement
si vous régénérez les favicons/OG — voir plus bas).

```bash
python3 build.py
```

Le script vide puis régénère entièrement `docs/`. Modifiez les données dans `src/`,
relancez, committez `docs/`.

---

## 3. Structure

```
build.py            Générateur : rendu de toutes les pages + artefacts de déploiement
build_lib.py        Bibliothèque : données, gouvernance, gabarits (head/header/footer), posters SVG
src/
  data/             Source de vérité (JSON)
    site.json         Marque, SEO, navigation, footer, feature flags
    catalog.json      Univers → Famille → Ligne → Produit → Variante → SKU (extensible)
    research.json     Mirenza Lab : axes, méthodes, programmes (dont confidentiels)
    claims.json       Registre des allégations (statuts) — pilote l'affichage
    selector.json     Règles du sélecteur « Trouver ma protection »
    journal.json      Articles du Journal
    content.json      Contenus éditoriaux des pages
  css/              tokens.css (palette, type) + styles.css (design system)
  js/               main.js (menu, vidéos lazy, sélecteur, filtres, reveal)
  media/            Monogramme, favicons, image OG (générés depuis le logo réel)
docs/               SORTIE GÉNÉRÉE — non versionnée ; GitHub Actions la construit et la publie.
.github/workflows/  build.yml — reconstruction automatique optionnelle (voir §8)
```

---

## 4. Gouvernance des allégations (important)

Le site n'affiche publiquement que ce qui est **validé**. Cette règle est appliquée
**au moment du build** — les données non publiables ne sont jamais écrites dans le HTML.

**Règle** (dans `build_lib.py`) :
```python
public = claim.public == true AND claim.status in ["verified", "published"]
```

### Capacités d'absorption (ml)
Dans `claims.json`, les allégations `abs-light / abs-regular / abs-night`
(15 / 25 / 35 ml) sont `status: in_validation`, `public: false`.
→ Le site **n'affiche donc pas les chiffres**. Il montre les niveaux
(Light / Regular / Night) et leur usage (« Flux léger / modéré / abondant »),
avec la mention **« Capacité en cours de validation »**.

Le jour où une allégation passe à `verified`/`published` et `public: true`,
le chiffre **apparaît automatiquement** partout (fiches produit, sélecteur, famille) —
sans toucher au HTML. Il suffit de mettre à jour `claims.json` et de relancer le build.

### Programmes confidentiels
`research.json` contient des programmes internes marqués `public: false`
(faisabilité, hypothèses). Ils **n'apparaissent jamais** dans le HTML ni dans les
données publiques : le build les filtre avant écriture. La page `lab/programmes/`
mentionne seulement leur **nombre**, jamais leur contenu.

### Données publiques
`docs/data/` ne contient qu'une version **filtrée** des données (les cibles chiffrées
non validées et les programmes confidentiels en sont retirés).

---

## 5. Ajouter une nouvelle famille de créations

Aucune réécriture du header n'est nécessaire : la navigation et les grilles sont
pilotées par les données.

Dans `src/data/catalog.json`, ajoutez une famille sous un univers avec
`"status": "published"` (utilisez `future_family_template` comme base) :

```json
{
  "id": "ma-famille",
  "name": "Nom de la famille",
  "slug": "ma-famille",
  "status": "published",
  "lines": [{ "id": "core", "name": "…", "products": [ … ] }]
}
```

Relancez `python3 build.py` : la page famille, les fiches produit, le plan du site et
les liens sont générés automatiquement. Tant qu'une famille est `status: private/draft`,
elle reste invisible (pas de fausse page « bientôt »).

---

## 6. Ajouter les vraies polices (Suisse Intl)

Les fichiers Suisse Intl ne sont pas inclus (licence). Le site utilise une pile de
repli (Helvetica Neue / Arial), fidèle visuellement.

1. Déposez les WOFF2 dans `docs/assets/fonts/` (et `src/…` si vous rebuildez) :
   `SuisseIntl-Regular.woff2`, `SuisseIntl-Medium.woff2`.
2. Dé-commentez les blocs `@font-face` en haut de `src/css/tokens.css`.
3. Relancez le build.

---

## 7. Ajouter les vrais films

Les emplacements de films affichent aujourd'hui des **posters SVG de marque**
(placeholders élégants avec label). Pour activer une vidéo réelle :

1. Déposez le MP4 dans `docs/assets/media/` (ex. `mm_house_manifesto_loop_16x9_v01.mp4`).
2. Dans `src/data/content.json`, sur le film concerné, ajoutez la clé `"src"` :
   ```json
   "film": { "id": "mm_house_manifesto_loop_16x9_v01", "src": "mm_house_manifesto_loop_16x9_v01.mp4", "ratio": "16x9", "label": "…" }
   ```
3. Relancez le build. La vidéo se charge en lazy-load, se lit en sourdine dans le
   viewport, se met en pause hors écran, et respecte `prefers-reduced-motion`.
   Le poster SVG sert d'image d'attente.

Voir `assets/media/ASSET_MANIFEST` du brief pour la nomenclature des fichiers.

---

## 8. Reconstruction automatique (optionnel)

Le workflow GitHub Actions (`.github/workflows/build.yml`) reconstruit `docs/` à chaque push sur `main` puis déploie directement l’artefact sur GitHub Pages. Dans **Settings → Pages**, choisissez **Source : GitHub Actions**.

---

## 9. Réglages rapides (feature flags)

Dans `src/data/site.json → features` (puis rebuild) :

| Flag | Effet |
|---|---|
| `enable_endometriosis` | Affiche/masque le pilier Endométriose |
| `enable_pharmacy` | Affiche/masque l'espace « En pharmacie » |
| `enable_selector` | Active « Trouver ma protection » |
| `enable_journal` | Active le Journal |
| `enable_lab_publications` | Affiche la page Publications du Lab |
| `enable_research_participation` | Ouvre l'appel à participation Endométriose (à n'activer qu'avec un protocole réel) |

---

## 10. Notes

- Accessibilité : navigation clavier, focus visible, `prefers-reduced-motion`, contrastes,
  skip-link, alternatives textuelles. Le contenu reste visible sans JavaScript.
- SEO : titres/descriptions par page, Open Graph, canoniques, JSON-LD (Organization,
  Product, Article, MedicalWebPage), `robots.txt`, `sitemap.xml`.
- Le formulaire de contact est une démonstration statique : branchez un service
  (Formspree, Basin, etc.) ou un back-end pour l'activer.
- Aucune fausse imagerie produit ni scientifique n'a été générée. Les visuels produit
  sont des placeholders explicites (« à photographier ») ; la technologie et le packaging
  s'appuient sur vos **références approuvées**.

---

## 11. Visuels & films (direction visuelle)

### Intégration des films au site
Les films MP4 sont **désormais intégrés** et se lisent en boucle, en autoplay
silencieux à l’entrée dans le viewport, en pause hors écran, avec image d’attente
(poster) et **respect de `prefers-reduced-motion`** (film figé sur le poster) :
- **Accueil** : hero = *Manifeste* ; section « L’univers en mouvement » = les 4
  films de territoires (eau, huile, velours, nuit) — présentés comme des directions,
  pas un catalogue.
- **Lingerie menstruelle** (famille) : hero = *La signature* (élastique).
- **Classic Brief** (produit) : média = *La couture*.
- **Technologie** : *Les épaisseurs* (qualitatif, sans chiffres).
Les fichiers vidéo vivent dans `src/media/` (copiés vers `docs/assets/media/`).
Pour changer un film, éditez la clé `film` correspondante dans `src/data/content.json`
ou le cfg du gabarit, puis relancez le build.


Une série de visuels **macro / détail** raconte la Maison sans dévoiler la forme
entière des produits : l’élastique signé « Maison Mirenza », la couture, les
épaisseurs de protection, la matière (tissage), l’absorption, le contour technique.

- **Sources** : SVG vectoriels dans `src/media/mm_*.svg` (statiques et animés).
- **Générateur** : voir le paquet « Visuels & films » (`art.py`, `build_gallery.py`)
  et sa planche `index.html`.
- **Intégration** : les versions **statiques** sont câblées dans le site
  (famille → élastique signé ; produits → couture / contour ; technologie →
  épaisseurs). Les versions **animées** (SMIL) sont fournies pour vos usages
  éditoriaux/sociaux ; le site privilégie les statiques pour l’accessibilité
  (`prefers-reduced-motion`).
- **Gouvernance** : l’infographie de référence portant des valeurs en millilitres
  (15/25/35 ml) n’est **pas** publiée sur le site tant que ces capacités ne sont
  pas validées. Elle reste disponible dans la source pour l’équipe. Les visuels
  « épaisseurs » n’affichent que des libellés qualitatifs (Contact / Absorption /
  Barrière / Extérieur). L’emballage réel (photo) reste affiché dans l’espace
  Pharmacie — à confirmer selon votre politique d’affichage.
