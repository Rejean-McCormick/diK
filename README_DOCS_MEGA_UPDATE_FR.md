# Mise à jour documentaire de diK — DIK-DOCS-LOCAL-1

**Contenu : documents uniquement. Pas de module Python modifié. Pas de nouveau scanner.**

## Priorités

- Un KQ/KP n'est pas une traduction : recherche indépendante de la forme dans la locale voulue.
- Référencer les dictionnaires locaux à leur emplacement ; ne pas les copier dans les 126 Kristals.
- Distinguer sources indexées, présentes sur le disque, alignées, licenciées et activées.
- Conserver Q/P Wikidata, L/S/F et GF comme systèmes distincts.
- Conserver la preuve des limites de V3 et les écarts de versions Framework.

## Installation

L'installateur `TOUT_AUTO_PS7.ps1` place les documents dans `C:\mycode\diK\diK\docs\...` (après vérification de la vraie racine). Il écrit un journal d'installation dans `reports\installations\DIK_DOCS_...`.

Il **n'écrase pas** un fichier déjà présent avec contenu inconnu : les documents nouveaux sont indépendants, les mises à jour des documents historiques ne sont appliquées que si l'empreinte du fichier local correspond au snapshot de référence utilisé pour cette mise à jour. Les fichiers historiques divergents sont laissés intactes et notés dans le rapport. Une sauvegarde est faite avant chaque remplacement autorisé.

## Lire après installation

`docs\DIK_GUIDE_MAITRE_RESOLUTION_LOCALE.md`, qui renvoie vers les dix nouveaux chapitres 34 à 43.

## Sources analysées

- `znapshot_diK_11211811.zip`, complété par les documents V3 livrés lors des correctifs précédents.
- `znapshot_Spek_11222007.zip` : `docs/CARTE_REPOS_ET_CHEMINS.md`.
- `znapshot_Konstellation_11222007.zip` : `config/v11-reader.local.example.json`, `server/integrations/kristal-v11.mjs`.
- Index-only des dépôts GF WordBench, RGL, Core, Lexicons Archive, gf-wikidata_repos_source, Observatoire, audits, etc.
- `RESOLUTION_20261123T005959Z.zip / rapport.json` : diagnostic V3 daté.

Les index ne contiennent pas les contenus complets des lexiques GF : les affirmations sur leur capacité à résoudre des KQ sont volontairement limitées.


## V5.7 — Collection locale intégrale de l’index EncyK dans diK

diK peut maintenant créer 14 dictionnaires candidats SQLite en streaming
à partir des fichiers déjà présents sur D:, sans réseau, sans transfert de
fichiers massifs. Voir `docs/docs/65_COLLECTION_LOCALE_14_LANGUES_ENCYK_V5_7.md`
pour les commandes, les contraintes SQLite/WAL, la reprise, les licences et
les limites des gloses d’EncyK v0.2.
