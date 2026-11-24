# 65 — V5.7 : DIK-LEX-1, construction des quatorze dictionnaires locaux à partir d’EncyK

**Livré : moteur de consolidation lexical en lecture seule côté source.** Cette étape
matérialise réellement des observations lexicales dans **14 fichiers SQLite** indépendants,
mais ne certifie ni l’exhaustivité des langues, ni les droits de redistribution, ni une
équivalence avec KQ/KP. Le dictionnaire est **candidat**, jamais publié automatiquement.

## Décision architecturale

- Le corpus intégral présent sur `D:\EncyKlopedia` a priorité sur les téléchargements ciblés V5.6.
  **Aucun accès Internet dans ce connecteur** ; aucun re-téléchargement des archives Kaikki,
  UniMorph ou Wikidata existantes.
- La source est l’index EncyK `30_working/lexical/harvester/index-v1/lexical.sqlite3`.
  Les manifestes `latest.json` et `dik-source-handoff.candidate.json` doivent
  désigner exactement cette base, déclarer les droits **non approuvés** et interdire la publication.
  Les bases `dik-reconciliation-v1` et `dik-enrichment-v1` restent des gisements de
  preuves supplémentaires ; elles ne remplacent pas la lecture **de toutes les observations**
  de l’index principal, y compris celles sans homographes intersources.
- Les données de travail sont placées, par défaut, dans `D:\diK\lexical\collection-v57`.
  EncyK est ouvert avec SQLite `mode=ro` et `PRAGMA query_only=ON`, sans `immutable=1`
  (qui pourrait masquer le WAL), sans `VACUUM` ni checkpoint. Un lecteur SQLite
  de base en WAL peut nécessiter des fichiers techniques `-shm` gérés par SQLite ;
  aucune écriture de données n’est autorisée sur EncyK.
- Chacune des 14 langues exactes (`en fr es de nl sv da no nn fi et af it pt`) obtient
  sa propre base SQLite. Les sources `status=complete` seules sont éligibles.
  Les autres sont **exclues explicitement**, jamais comptées comme couverture.
- Le **norvégien `no` n’est pas `nb`** ; `nn` reste distinct ; aucun repli `nob`/`nno` n’est
  fabriqué. Les éventuelles absences apparaissent en `NO_DATA`.

## Contenu réel d’un dictionnaire candidat

- Table `lexemes` : graphie exacte, clé de recherche héritée d’EncyK, catégorie
  grammaticale. Deux graphies identiques dans deux sources peuvent partager une
  tête lexicale, **mais ce partage orthographique ne prouve aucune identité de sens**.
- Table `observations` : une entrée **par ligne de l’index EncyK** avec identifiant
  stable de source, ligne d’origine, variante de langue originale, forme fléchie et
  traits grammaticaux tels qu’observés, identifiants lexicaux externes `L/Q`, et
  **comptages** de sens, de formes et de traductions.
- Table `sources` : chemins relatifs, famille, édition, état `complete`, vérification
  de SHA officiel observée, champ droits non approuvés.
- Table `meta` : point de reprise (dernier `lemma_key`/id), nombre de lignes,
  empreinte de l’index et statut `IN_PROGRESS`, `NO_DATA`, `COMPLETE` ou anomalie.

**Attention importante :** l’index EncyK stocke des *comptes* de sens et de traductions,
**pas toutes leurs gloses ni tous les IDs individuels L/S/F**. Cette livraison n’invente
aucune définition à partir de ces comptes. L’import de la v0.6 EncyK, qui échantillonne
5 millions d’ancrages mais n’est pas exhaustif, et une extraction en flux des données
primaires seront traités dans une étape de sens/provenance distincte.

## Commandes Windows PowerShell 7

```powershell
$env:PYTHONPATH = 'C:\mycode\diK\diK\src'
py -3 -m dik world local-plan14 --encyk-root 'D:\EncyKlopedia'
py -3 -m dik world local-build14 --encyk-root 'D:\EncyKlopedia' --output-dir 'D:\diK\lexical\collection-v57'
py -3 -m dik world local-status14 --collection-dir 'D:\diK\lexical\collection-v57'
py -3 -m dik world local-lookup --collection-dir 'D:\diK\lexical\collection-v57' --language fr --term chat
py -3 -m dik world local-export14 --collection-dir 'D:\diK\lexical\collection-v57' --output-zip 'C:\mycode\diK\diK\reports\DIK_V5_7_BILAN_MANUEL.zip'
```

L’exécution complète n’a **aucune limite de lignes** par défaut. Les paramètres
`--languages fr,en` et `--max-rows-per-language 1000` servent à des pilotes explicites,
marqués `PARTIAL` tant que l’index n’est pas épuisé.

La reprise est transactionnelle par blocs de 4 000 lignes avec doublons évités par
`source_row_id`. Les données existantes ne sont pas écrasées ; si le fichier source
ou son WAL change, le moteur **refuse de continuer** avec un instantané incohérent.
Une nouvelle collecte doit alors utiliser un **nouveau répertoire de sortie**.
Le verrou de construction empêche deux instances concurrentes. Réserve minimale
libre configurable : 10 Gio. Les 14 SQLite peuvent demander beaucoup d’espace ;
on ne peut pas promettre un poids cible sans exécution réelle sur D:.

## Rapport partageable

`local-export14` produit **un ZIP de moins de 1 Mio**, contenant `summary.json`,
`langues.csv`, `SHA256_EXPORT.json` : uniquement des **comptages, statuts et empreintes**.
Les mots, textes tiers, fichiers massifs, chemins Windows et licences incertaines ne
sont pas transmis. Chaque SQLite reste local et privé.

## Frontières non franchies

- Aucune copie de Wikidata, Kaikki ou UniMorph sur Internet.
- Aucune entrée présentée comme approuvée ou redistribuable sans preuve des droits.
- Aucune déduction de sens à partir d’une graphie, d’une traduction ou d’un POS.
- Aucune augmentation de la résolution canonique `11 188 / 294 364` sans revue.
- Pas de raccordement KQ/KP, GF, publication Framework v11, ni d’affirmation
  « tous les mots de chaque langue » à ce stade.
- Pas d’import automatique des sources primaires non encore indexées par EncyK ; cela
  exige d’abord de qualifier les neuf archives `no_data` et les sources hors index.

## Vérification technique

Tests unitaires et de bout en bout sur SQLite au schéma v0.2 EncyK, absence
`no/nb`/`nn` de repli, sources incomplètes exclues, reprise après interruption,
rechiffrage de manifestes, droits non approuvés, résistance à une modification de
source, extraction ZIP sans mots et sans chemins, réinstallation et rollback.
**Le corpus SQLite réel de plusieurs Gio n’était pas joint au dossier de
travail ; l’exécution complète sur D: doit être confirmée par le bilan utilisateur.**
