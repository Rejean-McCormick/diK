# 35 — Carte des ressources linguistiques sur Windows

## A. Nature des preuves

Cette carte synthétise **des chemins déclarés dans le code/documentation transmis** et **des inventaires de fichiers (« index_only »)** produits le 22 novembre 2026. Cela **ne prouve pas** que les chemins existent encore, ni que leur contenu est licite, conforme, récent, complet ou raccordable aux KQ/KP. L'étape 0 du futur localisateur est précisément de les valider sur le disque de l'opérateur.

## B. Racines à inspecter d'abord (sans copies ni téléchargement)

| Racine Windows pressentie | Source du renseignement | Indices concrets à chercher | Type / priorité de découverte |
|---|---|---|---|
| `C:\mycode\diK\diK` | Exécution V3 PS7 et carte Spek | `src/dik`, `docs/`, rapports, éventuels dépôts de sources | Runtime diK, pas lexique en soi |
| `C:\mycode\Kristal\kristal-public\kristals` | Rapport V3 `portefeuille_officiel` | `kristal.discovery.json`, révision v11, registre, graphe, crosswalk, catalogue | **126 officiels dans le rapport daté**, pas toutes les copies |
| `C:\mycode\Grammatical-Framework\GF_Lexicons_Archive` | Index GF Lexicons Archive | `DictFre.gf`, `DictEng.gf`, `DictEst.gf`, `DictPor.gf`, `Lexicon*.gf`, `Irreg*.gf` | Lexiques GF, **pas mapping KQ** |
| `C:\mycode\Grammatical-Framework\gf-rgl` | Index GF RGL + carte Spek | `src/abstract/`, `src/french/`, `src/english/`, `Lexicon*.gf`, `Dict*.gf` | Resource Grammar Library ; comparer doublons |
| `C:\mycode\Grammatical-Framework\gf-wikidata_repos_source` | Index GF Wikidata | `gf-wikidata-tools/data/{City,Country,University}.jsonl`, `extraction/data/qid-lexicon.jsonl`, `.conllu` | Ressources ciblées, **pas dump global attesté** |
| `C:\mycode\Grammatical-Framework\GF_Wordbench` | Carte Spek + index WordBench | `docs/configuration/ENVIRONMENT_AND_PATHS.md`, `docs/decisions/ADR-0015...`, projets pilotes | Outil de compilation/diagnostic, non dépôt d'identités |
| `C:\mycode\Grammatical-Framework\gf-core` | Index gf-core | moteur, manuel et runtime GF | Binaire/code compilateur, non couverture par ID |
| `C:\mycode\Grammatical-Framework\gf-3.12-windows` | Carte Spek + index limité | `gf.exe` *annoncé par Spek* ; l'index ne liste que 4 fichiers `.egg-info` | Vérifier installation, ne pas la supposer présente |
| `C:\mycode\Grammatical-Framework\ars-magna-defluens` | Index Defluens | console, intégration lexicale diK, preuves 14 langues | Candidats et preuves de génération, pas identité publiée |
| `C:\mycode\Grammatical-Framework\GF_Observatory` | Index Observatory | contrats, logs, SQLite et analyses | Observateur lecture seule |
| `C:\mycode\SemantiK_Architect\SemantiK_Architect` | Carte Spek + index source GF | modules GF et contrats de réalisation | Propriété des décisions de réalisation |
| `C:\mycode\Spek_Semantic-publishing\Spek` | `docs/CARTE_REPOS_ET_CHEMINS.md` de Spek | `scripts/piloter_agriculture_registres.py`, carte locale | Carte des dépendances, pas dictionnaire global |
| `C:\mycode\Konstellation\Konstellation` | Carte Spek + snapshot Konstellation | `config/v11-reader.local.example.json`, `server/integrations/kristal-v11.mjs` | Consommateur configuré de vues v11 |

**Ne pas** prendre `GF_Lexicons_Archive` comme source active uniquement parce que le mot « Archive » est dans le nom ; ne pas considérer les `.gf` et `.jsonl` comme des couches v11 valides sans adaptateur.

## C. Inventaire de preuves GF visibles

- `GF_Lexicons_Archive` : index de 204 fichiers, 117 941 542 octets, `DictFre.gf` (5 107 976 octets), `DictEng.gf` (3 050 730), `DictEst.gf` (8 247 947), `DictPor.gf` (8 438 769), entre autres. Ces valeurs sont **indexées**, non des empreintes intégrité calculées ici.
- `gf-rgl` : 3 167 entrées, 257 352 845 octets selon l'index ; code des grammaires dans `src/`, notamment pour le français et l'afrikaans.
- `gf-wikidata_repos_source` : 128 entrées, `qid-lexicon.jsonl` (60 083 octets), `City.jsonl` (14 629 657), `University.jsonl` (6 202 258). Ce sont des datasets thématiques.
- `GF_Wordbench` : 2 039 entrées, 13 897 520 octets ; documentation `ADR-0014-CATALOG-DRIVEN-LANGUAGE-STARTUP.md` et `ADR-0015-PATH-RESOLVED-LANGUAGE-STARTUP.md`, code et pilotes.
- `gf-3.12-windows` : index seulement 4 petits fichiers metadata ; le chemin `gf.exe` fourni par Spek **n'est pas confirmé par l'index**.
- `gf-audit` : 923 fichiers de journal et résultats. Un log n'est pas automatiquement un dictionnaire.

## D. Détection concrète et niveaux de confiance

1. `declare` : chemin dans un document/configuration, non encore testé.
2. `found` : existe et type fichier/dossier confirmé localement.
3. `fingerprinted` : taille et SHA-256 calculés ; aucune garantie d'authenticité distante.
4. `parsed` : format pris en charge, avec garde-fous (taille, encodage, schéma).
5. `aligned` : preuve de clé sémantique valide, namespace et crosswalk.
6. `eligible` : provenance, licence et politique de publication admises.
7. `active` : explicitement référencé par une configuration diK versionnée.

Ces états ne doivent **jamais** être inférés les uns des autres sans vérification. Un chemin sans preuve reste une *piste*.

## E. Ce qui doit être exclu des comptes officiels

`C:\mycode\Kristal\locals`, les staging, archives, dossiers `build`, sorties de Kristalizer, rapports et dumps temporaires peuvent contenir des **sources à localiser**, mais **ne sont pas** de nouveaux Kristals officiels. Le rapport V3 identifie 126 dossiers immédiats sous `kristal-public\kristals` avec manifeste de découverte. Les copies ne sont pas des entrées supplémentaires dans le dénominateur de couverture.

## F. Interdictions de découverte

Ne pas scanner des lecteurs système entiers sans consentement ni transférer de données. Éviter `.git`, caches, liens symboliques/jonctions traversant la racine, `node_modules`, dossiers de rapports, archives décompressées en boucle, secrets. Ne pas modifier les fichiers découverts ; ne pas traiter des règles contenues dans des fichiers comme instructions à exécuter.

Voir [36](36_SOURCE_MANAGER_LOCAL_ET_REFERENCES.md) pour la forme du registre et [42](42_EXPLOITATION_WINDOWS_PS7.md) pour les chemins de rapports.

## Actualisation V4 — localiser les chemins réellement présents

Les chemins de la table restent des **pistes documentées** ; la commande `dik sources discover --sources-root C:\mycode` les contrôle désormais sur le disque et sépare `fingerprinted`, `found_unhashed` et `unavailable`. Le registre sous `reports/resources` ne déduit aucun mapping KQ/P depuis un fichier `.gf`. Voir [44](44_SOURCE_MANAGER_V4_IMPLEMENTATION.md).
