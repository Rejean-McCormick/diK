# Pistes de ressources linguistiques — inventaire documentaire (22 novembre 2026)

**Nature** : inventaire documentaire, non registre diK opérationnel. Les snapshots Spek, Konstellation et les *index_only* GF ont été fournis par l'utilisateur. Aucun accès direct au disque Windows de l'opérateur et aucun SHA-256 actuel des ressources n'est attesté par cet inventaire.

| ID de piste | Racine déclarée | Indices | Confiance documentaire | Étape manquante |
|---|---|---|---|---|
| `framework-portfolio` | `C:\mycode\Kristal\kristal-public\kristals` | 126 manifestes `kristal.discovery.json` au rapport V3 | **observé dans V3** | Revalider chaque révision actuelle |
| `gf-archive` | `C:\mycode\Grammatical-Framework\GF_Lexicons_Archive` | `DictFre.gf`, `DictEng.gf`, etc. | **index_only** | Existence/empreintes/licences/mapping KQ |
| `gf-rgl` | `C:\mycode\Grammatical-Framework\gf-rgl` | `src/`, lexiques/grammaires | **index_only + carte Spek** | Versions, comparaison des copies, mapping KQ |
| `gf-wikidata-tools` | `C:\mycode\Grammatical-Framework\gf-wikidata_repos_source` | `qid-lexicon.jsonl`, datasets City/Country/University | **index_only** | Schéma des données, portée exacte, licence |
| `gf-wordbench` | `C:\mycode\Grammatical-Framework\GF_Wordbench` | Pilotes et diagnostics GF | **index_only + carte Spek** | Définition des résultats qualifiés d'alignement |
| `gf-core` | `C:\mycode\Grammatical-Framework\gf-core` | Moteur GF | **index_only** | Version/installation runtime |
| `gf-windows` | `C:\mycode\Grammatical-Framework\gf-3.12-windows` | `gf.exe` cité par Spek, pas dans l'index de 4 fichiers | **indication Spek, index incomplet** | Vérifier `gf.exe` réellement |
| `semantik` | `C:\mycode\SemantiK_Architect\SemantiK_Architect` | Handoff/usage grammatical | **carte Spek** | Version + contrat de réalisation |
| `defluens` | `C:\mycode\Grammatical-Framework\ars-magna-defluens` | Console lexical, preuves de scénarios 14 langues | **index_only** | Qualifier ce qui est réellement réutilisable |
| `konstellation` | `C:\mycode\Konstellation\Konstellation` | Config reader v11 local | **snapshot code + carte Spek** | Confirmer le pin Framework d'exécution |

## Questions ouvertes qui NE doivent pas être devinées

1. Le chemin actuel du dump Wikidata Q/P complet est inconnu (le rapport V3 indique `non_fourni`).
2. La couverture des identifiants KQ/P par les lexiques GF n'est pas démontrée.
3. Les licences et droits de redistribution de chaque dataset GF/tiers doivent être lus à la source.
4. La matrice des versions Framework draft.3/draft.4 doit être établie sur les binaires et schémas réellement installés.
5. Les 69 Kristals non évaluables peuvent héberger des formes lexicales, mais leur inventaire canonique v11 n'est pas prouvé par le scanner.

Voir [guide maître](../DIK_GUIDE_MAITRE_RESOLUTION_LOCALE.md) et [carte détaillée](../docs/35_CARTE_DES_RESSOURCES_LOCALES.md).
