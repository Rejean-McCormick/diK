# 50 — Actions concrètes après le registre local des 5 269 ressources

## Ce que l'on sait réellement

Le fichier `resource-registry.json` fourni décrit 5 269 chemins dans 12 racines ; l'index est complet (`truncated=false`) et les chemins ont des empreintes locales. Il n'embarque **aucun contenu** des fichiers `.gf`, `.pgf` ni des JSONL. Une source non autorisée n'est pas forcément mauvaise : elle n'a pas reçu les preuves nécessaires.

### Points prioritaires

1. **Wikidata Q/P** : vérifier le vrai schéma de `gf-wikidata-tools/extraction/data/qid-lexicon.jsonl`. Les 40 JSONL thématiques ne forment pas un dump global. Les lexèmes L/S/F requièrent un connecteur distinct.
2. **GF** : hiérarchiser RGL, archive et sources WordBench ; ignorer les `.pgf` de tests. Ne pas confondre un dictionnaire GF de 5 Mio avec 5 Mio de formes alignées KQ/KP.
3. **Framework v11** : auditer les 486 catalogues et les 392 couples registre/crosswalk sous leurs namespaces ; vérifier empreintes des couches, décisions et pièces KS, puis rendre visibles les collisions ou les raisons de refus.
4. **126 officiels** : la situation observée avant V5 était 57 officiels évaluables et 69 non évaluables ; aucune nouvelle commande ne transforme mécaniquement les 69 en v11 valides.
5. **Droits** : interdire la publication de sources tiers sans qualification de licence et provenance.

## Critères d'acceptation pour la suite

- `sources discover` couvre les emplacements ciblés, sans suivre de liens et sans écrire à l'extérieur de `diK/reports`.
- `sources verify` signale explicitement les sources modifiées ou non hashées.
- `sources qualify` produit une ligne par source, un motif et une action ; zéro activation implicite.
- `resolve14 --observe-qid-lexicon` ne compte aucune forme candidate comme résolue. Une collision Q/P+locale est exclue.
- Aucun texte FR→EN ; aucune corrélation de graphie ; aucun lien GF ou L/S/F inventé.
- Les tests Python sont des preuves de code isolées, non des preuves de fonctionnement natif sur Windows ou de résolution des 14 langues sur des dumps complets.

## Traces attendues

- `diK/reports/resources/DISCOVERY_*/resource-registry.json`
- `diK/reports/resources/QUALIFICATION_*/rapport.json`
- `diK/reports/resolution_14_langues/RESOLUTION_*/rapport.json`
- `diK/reports/installations/DIK_V5_*/install.json` ou `failure.json`

Les sources restent à leur emplacement initial ; seules les **références** et les **rapports** sont écrits sous diK.


## Progression V5.2

L'exploration et le recoupement des 40 sources Wikidata thématiques sont désormais **implémentés pour l'observation candidate** via `resolve14 --observe-wikidata-thematic`. Les fichiers restent locaux et leur format réel doit être vérifié sur Windows. Les liaisons et formes candidates ne deviennent pas des publications ; voir [52](52_AUDIT_WIKIDATA_THEMATIQUE_V5_2.md). Le raccordement mondial Wikidata et GF demeure à développer.
