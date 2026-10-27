# Traçage précis : ce que les archives démontrent, ce que diK 1.0 propose

## Contrats constatés dans les fichiers fournis

| Sources inspectées | Assertions étayées |
|---|---|
| Framework `spec/v11/Identity-and-Wikidata.md` | identités KQ/KP/KA/KS opaques et namespacées ; crosswalk approuvé ; Wikidata externe |
| Framework `spec/v11/Lexical-Boundary.md` | aucun label dans canon ; résolutions lexicales externes ; ambiguïté explicite |
| Framework `spec/v11/Dictionary-Management.md` | sources Wikidata/externes/curatées ; catalogue, priorités, SHA ; 300+ locales sparse |
| Framework `spec/v11/diK-Interoperability.md` | couverture KQ/KP, direct/fallback/missing/conflict, plan de conversion non exécutable |
| Framework `spec/v11/Legacy-Resolution.md` | aucun remplacement global ; original et commitments préservés ; plans soumis à revue |
| Framework `spec/v11/Conformance.md` | profils de conformité mais `V11-Full` pas revendiqué par draft fournie |
| diK 0.3 `src/dik/compact.py` | graphe canon unique + lexicon dédupliqué + anchors/digests ; profil diK applicatif |
| diK 0.3 `src/dik/cli.py` | project/dictionaries/coverage/wikidata import-local/projection export-verify-restore existent |
| diK 0.3 `README.md` | CLI hors ligne, projection compact/verbose, import sélectif, pas UI/sync massive |
| patterns archive #08/#10/#12/#15/#18/#25/#31/#07 | explication de principes architecturaux ; leur adoption diK est une **décision proposée** |

## Propositions de diK 1.0 qui NE SONT PAS encore livrées

Rapprochements multisource avec workflow GUI/revue ; index inverse et FTS durable ; synchronisation Wikidata complète/reprise réseau ; API locale, GUI et autorisations ; tâche d'import idempotente atomique et réparation d'index ; patch éditorial structuré ; rapports multi-Kristals ; TCK complet/benches massifs. Les nouveaux fichiers de `contracts/` sont des **propositions du produit** et ne doivent jamais être qualifiés de normes Framework existantes.

## Questions de produit laissées à ratifier avant la release

- Mode GUI (desktop natif vs interface web locale) ; lib de stockage SQL choisie ; politique de signatures multi-acteurs ; budget machines de performance ; granularité exacte des rôles review ; politique de téléchargement et distribution légale des dumps ; extension sharded des projections massives ; nomenclature et sémantique finales des nouvelles API.

Ces choix n'autorisent pas de déroger aux invariants du Framework ; les développeurs peuvent avancer sur les ports/contrats indépendants et soumettre une ADR quand un point bloquant est rencontré.
