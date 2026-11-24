# 33 — Résolution lexicale universelle : Kristals officiels × 14 langues

**Patch local `DIK-RESOLVE14-V3` — 22 novembre 2026**  
**Périmètre :** lecture seule, aucun appel réseau, aucun accès Git/Render, aucune traduction entre langues.

## Principe

Le Kristal conserve une identité **(namespace, KQ/KP)** indépendante de la langue. diK résout directement une forme pour `locale` en consultant un dictionnaire qui **connaît cet identifiant**. Un mot français ne sert jamais de texte source pour l'anglais, ni l'inverse. Les identifiants Wikidata `Q/P` sont des références **externes**. Pour relier un `Q/P` à un `KQ/KP`, une révision doit porter un `exactMatch` au statut `accepted` avec références de preuves `KS` valides.

Le sous-système Grammatical Framework actuel contient des **handoffs candidats** (`dik.gf-lexical-handoff/0.1-candidate`), avec `gf_function`, `gf_paradigm` et `approved_kristal_link` encore nuls. La présence de ces handoffs ne constitue pas une ressource de formes fléchies exploitable. Ce patch les inventorie, sans les transformer en grammaire validée.

## Commande

```powershell
$env:PYTHONPATH = 'C:\mycode\diK\diK\src'
py -3 -m dik coverage resolve14 `
  --official-root 'C:\mycode\kristal-public\kristals' `
  --sources-root 'C:\mycode' `
  --dik-root 'C:\mycode\diK\diK' `
  --min-kristals 126
```

Le lanceur `TOUT_AUTO_PS7.ps1` fourni dans le ZIP s'occupe de l'installation et de cette commande. Le nombre **126** est un minimum de sécurité correspondant au snapshot fourni, pas une valeur codée dans le moteur. Le scanner compte exclusivement les sous-dossiers immédiats de `kristal-public\kristals` munis de `kristal.discovery.json`. Copies locales, staging, historiques et sorties Kristalizer ne sont **pas** comptés comme Kristals officiels.

Pour consulter un dump Wikidata Q/P local qui n'a pas encore été importé dans un catalogue diK, ajouter explicitement :

```powershell
  --wikidata-dump 'D:\wikidata\latest-all.json.bz2' `
  --approved-sha256 '<empreinte SHA-256 obtenue indépendamment>'
```

Ce sont des **observations locales** de libellés Wikidata, pas des catalogues diK publiés. L'empreinte attendue, si fournie, vérifie le fichier par comparaison à une valeur indépendante ; un hash local seul n'authentifie pas Wikidata. Le scan ne télécharge jamais un dump automatiquement.

## Sources locales prises en compte

1. **Catalogue de la révision v11 sélectionnée** : vérifié via `dictionaries.audit` (schémas, couches, checksums, identités, crosswalk, priorité). Statut `catalogue_courant`.
2. **Autres catalogues v11 découverts dans `--sources-root`** : chaque source complète doit posséder son graphe, son registre et son crosswalk. Un catalogue isolé (p. ex. `qualite-fr`) peut aussi être relié **uniquement si** sa validation Framework complète réussit avec le registre et le crosswalk officiels du **même namespace**. Les formes ne sont raccordées que sur le **même namespace + même KQ/KP**. Un autre namespace n'est jamais fusionné sur similarité des mots. Le rapport sépare les catalogues complets des catalogues isolés vérifiés par héritage du registre officiel. Un `exactMatch accepted` contradictoire empêche le raccordement de cette source. Statut `catalogue_raccorde`, à examiner avant une intégration normative.
3. **Wikidata Q/P dans un dump local explicitement fourni** : résolution par un `Q/P` associé au KQ/KP par `exactMatch accepted` et preuve KS, provenant de la révision sélectionnée ou d'une autre révision v11 auditée. Statut `wikidata_observe`, pas publication d'un dictionnaire. Les `L/S/F` ne sont pas confondus avec les libellés d'items `Q/P`.
4. **GF** : les handoffs candidats sont recensés, jamais utilisés comme traduction ni comme flexion automatiquement validée.

Le moteur ne tente aucun alignement `mot → KQ`, aucune traduction automatique, aucune fusion inter-namespace. Si deux autres catalogues audités proposent des termes différents pour la même cellule sans valeur dans le catalogue sélectionné, le statut est `conflit`. Si le catalogue sélectionné donne un terme différent d'une autre source, il reste prioritaire mais un drapeau de conflit de révision est émis.

## Statuts dans les résultats

| Statut | Signification |
|---|---|
| `catalogue_courant` | Forme trouvée directement pour la langue dans la révision v11 sélectionnée |
| `catalogue_raccorde` | Forme d'un autre catalogue v11 vérifié, de même namespace/KQ/KP |
| `wikidata_observe` | Forme Q/P locale depuis un dump fourni, liée par exactMatch accepted |
| `conflit` | Plusieurs formes concurrentes parmi les sources auditées |
| `non_resolu` | Aucune forme fiable dans les sources réellement inspectées |
| `non_evaluable` | Pas de révision canonique v11 exploitable ; exclu du dénominateur linguistique |

**Important :** `non_resolu` ne veut pas dire « mot inexistant dans cette langue » ; cela veut dire « aucune forme accessible et raccordable dans les sources auditées ». Une langue n'est jamais « traduite » depuis une autre langue.

## Sorties

Les rapports et journaux sont créés sous
`C:\mycode\diK\diK\reports\resolution_14_langues\RESOLUTION_YYYYMMDDTHHMMSSZ\`.

- `rapport.json` — bilan et limites.
- `scan.log` — journal de contrôle.
- `kristals_officiels.csv` — liste des 126 Kristals ou des sous-dossiers officiels actuels, état du v11 sélectionné et raisons de non-évaluation.
- `couverture_kristals_14_langues.csv` — 14 lignes par Kristal officiel.
- `resolution_identifiants_14_langues.csv` — détail (namespace, KQ/KP, langue, forme, source, preuve).
- `identifiants_non_resolus.csv` — vrais non-résolus et conflits (pas de mots « à traduire »).
- `raccordements_a_qualifier.csv` — autres catalogues et observations Q/P à contrôler avant publication.
- `sources_dictionnaires.csv` — inventaire et statut des catalogues locaux trouvés, y compris sources refusées.
- `sources_gf_candidates.csv` — handoffs GF candidats ; zéro forme grammaticale certifiée.

Aucun fichier source n'est modifié, aucun `exactMatch` n'est approuvé automatiquement, aucun résultat n'est écrit hors du dépôt diK. Une erreur majeure empêche de publier le nouveau dossier de rapport ; les rapports antérieurs restent en place.

## Limites restantes

La disponibilité de dépôts de code GF, de ressources sans schéma v11, de dumps non importés ou de listes de ressources Wikidata ne suffit pas à les considérer comme des dictionnaires résolus. Un connecteur supplémentaire spécifique, avec licence/provenance/identité vérifiées, est nécessaire pour chaque format non v11. Le patch raccorde les **catalogues compatibles effectivement disponibles**, sans affirmer que la totalité des dictionnaires mondiaux est déjà fonctionnelle.
