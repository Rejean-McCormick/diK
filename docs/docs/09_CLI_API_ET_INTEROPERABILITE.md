# 09 — CLI, API et interopérabilité

## État réel des outils

Les commandes `tools/v11/dik_coverage.py`, `tools/v11/dik_conversion_plan.py`, `tools/v11/resolve_legacy.py`, `tools/v11/dictionaries.py` et `tools/v11/validate_v11.py` font partie du **Framework draft.3** ; ce sont des références **hors ligne**, et non l'application diK. Les commandes `dik …` ci-dessous sont une **proposition d'interface future**. Ne pas les présenter comme déjà exécutables.

## Commandes proposées

| Commande | Entrées | Effet | Écrit dans le canon ? |
|---|---|---|---|
| `dik project inspect` | projet / registre / catalogues | Inventaire, erreurs, namespaces | Non |
| `dik sources add-local` | fichier/dossier, licence | Prépare un snapshot source | Nouvelle référence de source |
| `dik wikidata import-local` | dump + crosswalk | Construit couches lexicales gelées | Nouveau snapshot uniquement |
| `dik wikidata download` | URI officielle, destination | Télécharge sur demande avec reprise et hash | Fichier source explicite |
| `dik sources diff` | 2 snapshots | Changements, retraits et nouveautés | Non |
| `dik dictionaries audit` | catalogue + couches | Intégrité, priorités, conflits | Non |
| `dik reconcile propose` | sources + registre | Correspondances candidates | File de revue |
| `dik reconcile review` | candidat + décision | Crosswalk révisé | Nouvelle version |
| `dik coverage report` | graphe, catalogue, locales | Rapport v11 + CSV dérivé | Rapport seulement |
| `dik legacy propose` | ancien Kristal + contexte | Plan de conversion non exécutable | Plan seulement |
| `dik legacy review` | plan + décisions | Plan révisé | Nouvelle version du plan |
| `dik validate` | artefacts | Contrôles v11 | Non |

Chaque commande modifiante doit posséder `--dry-run`, afficher la version d'entrée et refuser un chemin hors du workspace autorisé. Les noms et arguments exacts seront stabilisés au lancement du repo diK.

## Exemples réels du Framework

Depuis la racine du Framework v11 draft.3 :

```bash
python tools/v11/dik_coverage.py \
  --graph examples/v11/semantic-graph.example.json \
  --registry examples/v11/identity-registry.example.json \
  --crosswalk examples/v11/external-crosswalk.example.json \
  --catalog examples/v11/dictionaries/catalog.json \
  --locales fr,en,fr-CA \
  --output /tmp/rapport-diK.json

python tools/v11/dik_conversion_plan.py \
  --plan examples/v11/dik-conversion-plan.example.json \
  --registry examples/v11/identity-registry.example.json \
  --source examples/v11/dik-legacy-sample.json
```

Ces commandes lisent et vérifient ; elles **ne migrent pas** le fichier original.

## Artefacts d'échange normatifs

| Type | Schéma Framework v11 |
|---|---|
| Registre d'identités | `kristal-identity-registry.schema.json` |
| Graphe canonique | `kristal-semantic-graph.schema.json` |
| Catalogue | `kristal-dictionary-catalog.schema.json` |
| Termes Wikidata importés | `kristal-wikidata-lexical-record.schema.json` |
| Dictionnaire curaté | `kristal-curated-dictionary.schema.json` |
| Terminologie externe | `kristal-external-lexical-record.schema.json` |
| Crosswalk Q/P | `kristal-external-crosswalk.schema.json` |
| Complétude | `kristal-dik-coverage-report.schema.json` |
| Conversion | `kristal-dik-conversion-plan.schema.json` |

Tous sous `schemas/v11/` et `schema_version = "11.0"` lorsque requis. **N'ajoutez pas de champs non autorisés** directement dans ces artefacts ; créer un manifeste complémentaire diK plutôt que de les rendre incompatibles.

## API éventuelle — à définir ultérieurement

Un service local pourrait exposer lecture du catalogue, recherche d'un identifiant, aperçu de couverture et journal de décisions, mais ce n'est **pas un contrat Framework existant**. Un éventuel serveur doit refuser l'accès cross-namespace non autorisé, versionner les réponses par snapshot et ne jamais devenir source d'identités concurrente. L'usage hors ligne doit rester possible sans API.

## CI et codes de sortie proposés

`0` validation réussie ; `2` erreur de schéma/format ; `3` conflit lexical ; `4` identité ou namespace non résolu ; `5` source/hash/provenance invalide ; `6` approbation de migration manquante. Cette nomenclature est **une proposition diK** à tester, pas une valeur implémentée par le Framework.
