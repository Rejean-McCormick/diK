# 38 — Audit du portefeuille officiel : 126 Kristals, 14 langues

## 1. Une seule définition de « Kristal officiel »

Pour l'exécution V3 considérée : les **126 sous-dossiers immédiats** de `C:\mycode\Kristal\kristal-public\kristals` ayant `kristal.discovery.json`. Un dossier `locals`, `staging`, `archive`, une sortie Kristalizer ou une copie n'est **pas** un 127e Kristal. Ces dossiers peuvent néanmoins héberger une ressource linguistique à inventorier séparément.

Ne pas coder `126` comme une vérité éternelle : c'est la cardinalité **observée sur le portefeuille daté**, à contrôler lors de l'exécution suivante. La source de vérité est le manifeste de découverte et la racine officielle explicitement sélectionnée.

## 2. Deux dénominateurs à ne pas mélanger

- `kristals_officiels` : 126. Ceux sans registre/ensemble v11 exploitable restent dans le portefeuille.
- `kristals_evalues` : 57 au rapport V3. Les 69 autres sont `non_evaluable`, **ni 0 % lexical ni 100 %**.
- `identites_par_kristal` : somme des KQ/KP par Kristal évalué, soit 21 026 au rapport. Ce n'est pas le nombre mondial d'IDs uniques.
- `cellules_evaluees` : 21 026 × 14 = 294 364 couples **(Kristal, namespace, KQ/KP, locale)**. Pour un partage inter-Kristal, conserver les namespaces et dédupliquer seulement les copies prouvées.

## 3. Mesure datée — fichier livré par l'utilisateur

Source : `RESOLUTION_20261123T005959Z.zip / RESOLUTION_20261123T005959Z/rapport.json`, horodatage UTC 2026-11-23 00:59:59. Il s'agit d'un **résultat d'exécution**, pas d'une garantie concernant l'état actuel du disque.

| Mesure de V3 | Valeur | Interprétation |
|---|---:|---|
| Officiels / évaluables / non évaluables | 126 / 57 / 69 | V11 complet exigé pour les cellules |
| Catalogues détectés / v11 audités | 616 / 201 | Détection ne signifie pas source active |
| Catalogues qualifiés sur registre officiel | 9 | Réutilisation limitée, à examiner avant publication |
| Identités Q/P acceptées / candidates | 1 776 / 3 473 | États de crosswalk, pas nombre de mots |
| Formes `catalogue_courant` | 11 175 | Directes des catalogues sélectionnés |
| Formes `catalogue_raccorde` | 13 | Autres catalogues validés dans le périmètre du scan |
| Labels `wikidata_observe` | 0 | Aucun dump Q/P local fourni à ce scan |
| Candidats GF reconnus | 0 | Ne prouve pas l'absence des lexiques GF sur disque |
| Couples `non_resolu` | 283 176 | Absence de forme dans les sources **réellement auditées** |

Ainsi `11 188 / 294 364 ≈ 3,8 %` est un taux de **résolution attestée dans ce run**, **pas** le pourcentage de mots existant dans le monde et **pas** un indicateur de traduction.

## 4. Les 14 locales exactes

`en`, `fr`, `es`, `de`, `nl`, `sv`, `da`, `no`, `nn`, `fi`, `et`, `af`, `it`, `pt`.

Le norvégien générique `no` et le nynorsk `nn` restent distincts. Les tags sont des unités de politique de résolution ; ne pas sommer silencieusement leurs étiquettes ni déduire une identité de variante.

## 5. Statuts de la V3 et granularité

| Statut de la V3 | Signification relative à l'exécution |
|---|---|
| `catalogue_courant` | Forme directement présente dans la couche sélectionnée du Kristal |
| `catalogue_raccorde` | Forme issue d'un autre catalogue v11 vérifié et rattaché sans changement de namespace |
| `wikidata_observe` | Label observé depuis dump Q/P fourni, via exactMatch accepté |
| `conflit` | Sources concurrentes incompatibles nécessitant revue |
| `non_resolu` | Pas de forme qualifiée dans les sources auditées : *à investiguer* |
| `non_evaluable` | Pas de révision complète disponible : *à traiter côté format/registre* |

L'audit `scan14` de projet et l'audit `kristals14` de dossiers ne sont **pas** interchangeables avec `resolve14`. Ils calculent des métriques différentes : ne jamais mélanger les pourcentages V1, V2 et V3 sans définition explicite.

## 6. Exemple de chaîne de preuve par cellule

```text
portfolio_snapshot_id
  -> kristal_id + selected_v11_revision + namespace
  -> KQ/KP (exact semantic key) + locale
  -> catalog layer + SHA / crosswalk accepted + KS (si nécessaire)
  -> source version + resolved string + display status
  -> rapport.json + CSV + scan.log
```

Pour toute cellule `non_resolu`, documenter aussi `sources_consultees`, `sources_non_reconnues`, `sources_non_actives` et `raisons` dans un futur audit. Sinon un échec de connecteur ressemble à tort à un manque de lexique.

## 7. Ce qu'exige un rapport de production

- 126 sous-dossiers officiels **répertoriés une seule fois**, copies dans un inventaire séparé.
- Pour les 69 non évaluables, raison, chemins candidats et étapes de reconstruction de preuve ; **pas** de métrique lexicale artificielle.
- Contrôle de conformité v11 et sélection déterministe de révision.
- Résultat par `(kristal_id,namespace,id,locale)` avec source, hash, statut, ambiguïté, qualité et version.
- Comptes séparés pour `non_configure`, `source_absente`, `mapping_non_prouve`, `non_resolu_apres_sources_actives`, `fallback`, et `conflit` dans la future V4 ; ne pas rabattre tout sur « traduction manquante ».
- Pas de publication automatique et pas d'accès réseau implicite.

Voir [43](43_PREUVES_STATUTS_ET_LIMITES.md) pour le vocabulaire des preuves.

## Actualisation V4

Les comptes **126/57/69** documentent le scan V3 daté et ne sont pas des constantes du moteur. V4 autorise `--resource-registry` pour limiter la recherche aux fichiers v11 localisés, mais l'inventaire peut être incomplet ou tronqué ; les pourcentages d'un scan V4 ne doivent donc pas être comparés à ceux de V3 sans vérifier le périmètre des sources. Voir [44](44_SOURCE_MANAGER_V4_IMPLEMENTATION.md).
