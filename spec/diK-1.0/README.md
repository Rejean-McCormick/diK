# diK 1.0 — Spécification normative de référence

**Statut : SPECIFICATION CIBLE / candidate 1.0 (et NON produit 1.0 livré).**  
**Langue principale : français.**  
**Sources figées :** diK `0.3.0`, Kristal Framework `11.0.0-draft.3`, Kristal Authoring Kit `4.0.0-draft.2`, Kristal Integration Pack `0.2.0-alpha.1`, archive de 33 patterns d'architecture fournie.  
**Référence de conformité primaire :** les schémas et textes normatifs de Kristal Framework v11 draft.3. Un document diK ne peut pas les remplacer unilatéralement.

## Mission

diK gère les dictionnaires lexicaux, les correspondances entre référentiels, les projections linguistiques et les migrations *proposées* de Kristals vers le modèle canonique. **Une identité sémantique ne doit jamais dépendre d'un mot.** Les graphes canoniques utilisent exclusivement des identifiants de leur espace de noms (`KQ`, `KP`, `KA`, `KS`). Les mots sont dérivés et les correspondances Wikidata sont externes.

### Non négociable

1. **Le canon reste unique :** graphe/registre Framework ; ni diK, ni SQLite, ni Wikidata, ni la langue n'en deviennent la source d'autorité.
2. **KQ n'est pas Q Wikidata :** clé interne composée `(namespace_id, KQ…)`; `KP` propriétés, `KA` assertions, `KS` sources. Aucune fabrication de Q/P Wikidata.
3. **Deux répertoires distincts :** couches lexicales locales/importées d'une part ; *crosswalk* externe KQ↔Q/KP↔P de l'autre.
4. **Aucun remplacement aveugle de texte :** les littéraux, citations et documents ne sont pas des identifiants.
5. **Projections réversibles :** conserver l'identité exacte et le canon ; le Markdown « clean » est une **vue non réversible à lui seul**.
6. **Provenance, décisions, immutabilité :** un rapprochement reste candidat jusqu'à revue ; publication versionnée, jamais mutation silencieuse.
7. **Absence ≠ traduction :** langue sans entrée = état `missing`, sans libellé inventé ; fallback explicitement déclaré ≠ couverture directe.
8. **Backward compatibility :** lecture des anciens formats et anciens engagements sans altération ; nouvelle révision lors d'une migration approuvée.

## Ordre de lecture et priorité des normes

1. [`AGENTS.md`](AGENTS.md) et [`SPEC_LOCK.md`](SPEC_LOCK.md) — consignes obligatoires au développeur et aux agents IA.
2. [`docs/01_CONTRATS_ET_FRONTIERES.md`](docs/01_CONTRATS_ET_FRONTIERES.md) — périmètre, statuts des exigences.
3. [`docs/02_IDENTITES.md`](docs/02_IDENTITES.md), [`docs/03_DICTIONNAIRES.md`](docs/03_DICTIONNAIRES.md), [`docs/04_CONCILIATION.md`](docs/04_CONCILIATION.md).
4. [`docs/05_WIKIDATA.md`](docs/05_WIKIDATA.md), [`docs/06_PROJECTIONS.md`](docs/06_PROJECTIONS.md), [`docs/07_MIGRATION.md`](docs/07_MIGRATION.md), [`docs/08_COMPLETUDE.md`](docs/08_COMPLETUDE.md).
5. [`docs/09_ARCHITECTURE.md`](docs/09_ARCHITECTURE.md), [`docs/10_STOCKAGE_INDEXATION.md`](docs/10_STOCKAGE_INDEXATION.md), [`docs/11_API_CLI.md`](docs/11_API_CLI.md), [`docs/12_INTERFACE.md`](docs/12_INTERFACE.md).
6. [`docs/13_SECURITE.md`](docs/13_SECURITE.md), [`docs/14_PERFORMANCE.md`](docs/14_PERFORMANCE.md), [`docs/15_TESTS_TCK.md`](docs/15_TESTS_TCK.md), [`docs/16_RELEASE.md`](docs/16_RELEASE.md).
7. [`docs/17_TRACABILITE.md`](docs/17_TRACABILITE.md), [`docs/18_INTEGRATION.md`](docs/18_INTEGRATION.md), [`docs/19_LOCALES.md`](docs/19_LOCALES.md), [`docs/20_ETATS_ET_TRANSACTIONS.md`](docs/20_ETATS_ET_TRANSACTIONS.md), [`docs/21_ERREURS_OBSERVABILITE.md`](docs/21_ERREURS_OBSERVABILITE.md), [`docs/22_EVOLUTION_DES_CONTRATS.md`](docs/22_EVOLUTION_DES_CONTRATS.md).

**Priorité en cas de contradiction :** Framework v11 draft.3 > contrats applicatifs diK existants de v0.3 pour la rétrocompatibilité > nouvelles exigences cibles du présent dossier. Une contradiction = `BLOCKED: CONTRACT_CONFLICT`, jamais une correction silencieuse.

## État du logiciel vs exigences cibles

| Fonction | diK 0.3 existant | diK 1.0 requis |
|---|---|---|
| Inspecter graphe/registre/crosswalk | Oui | Durcir invariants et indexation |
| Audit catalogues + empreintes | Oui | Publication atomique, audit incrémental |
| Import Wikidata local sélectif | Oui, hors réseau | Dump complet + reprise/synchronisation contrôlées |
| Couverture graphe/locale | Oui | Multi-Kristal + qualité + exports |
| Projection compacte réversible | Oui, profil applicatif | Contrat figé + compat v0.2 + quotas |
| Concilier plusieurs sources | Non complet | Oui, provenance + approbation |
| Recherche inverse lexicale | Non complète | Index/contextes/désambiguïsation |
| Plan de migration | Framework : schéma seulement | Production/soumission, exécution déléguée sous autorisation |
| API + interface | Non | Oui, utilisables hors ligne |
| Gros volumes + 300+ langues | Structure, pas qualification | Mesures réelles et budgets explicites |

## Livrables et utilisation

Cette archive est un **cahier des charges exécutable par des équipes/agents**, pas le code diK 1.0. `contracts/` contient des schémas **proposés de l'application diK**, placés dans un namespace de contrat distinct des schémas officiels Framework. `examples/` et `tests/` servent de base à la qualification. Aucun schéma Framework n'est redéfini.

Pour obtenir `1.0.0` stable, satisfaire tous les `MUST` et les critères bloquants de [`docs/16_RELEASE.md`](docs/16_RELEASE.md), avec résultats d'essais vérifiables sur le code produit. Un tableau de conception ou des tests de schémas ne prouvent pas la certification du produit.

## Addendum candidate.2 — dernière consolidation avant implémentation

- [`REVISION.md`](REVISION.md) : portée, limites et changements de cette révision.
- [`docs/23_PROFIL_LOCAL_GOUVERNANCE.md`](docs/23_PROFIL_LOCAL_GOUVERNANCE.md) : profil local par défaut, sans ajout d'un serveur obligatoire.
- [`docs/24_ALGORITHMES_ORACLES.md`](docs/24_ALGORITHMES_ORACLES.md) : algorithmes précis de résolution, restauration, complétude et migration.
- [`docs/25_GATES_CI_EXECUTABLES.md`](docs/25_GATES_CI_EXECUTABLES.md) : validation documentaire stricte et gates de future certification.
- [`docs/26_BANC_PERFORMANCES.md`](docs/26_BANC_PERFORMANCES.md) : banc de mesure reproductible, pas de performances inventées.
- [`tests/requirements.json`](tests/requirements.json) et [`tests/reference_vectors.json`](tests/reference_vectors.json) : exigences par ID et cas d'oracle documentaire.

**Statut de la présente révision :** `1.0-candidate.2`, spécification améliorée, encore soumise à ratification des décisions produit avant de geler l'API. Les 5 nouveaux contrats demeurent candidats.
