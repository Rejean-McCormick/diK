# 16 — Matrice de traçabilité produit → contrat → test

| Besoin | Source normative existante | Implémentation diK attendue | Test d'acceptation |
|---|---|---|---|
| Identifiants indépendants des mots | `kristal-identity-registry.schema.json`, `kristal-semantic-graph.schema.json` | Résolution namespacée | collision inter-namespace rejetée |
| Dictionnaires 300+ langues | `kristal-dictionary-catalog.schema.json` | Catalogue et résolveur lexical | 301 langues clairsemées, aucun mot fictif |
| Termes Wikidata | `kristal-wikidata-lexical-record.schema.json` | Import du dump en couches | snapshot conservé et hash validé |
| Terminologies externes | `kristal-external-lexical-record.schema.json` | Admission contrôlée avec licence/provenance | source invalide refusée |
| Édition locale | `kristal-curated-dictionary.schema.json` | Nouvelle couche après revue | import ultérieur ne l'écrase pas |
| Liens KQ↔Q / KP↔P | `kristal-external-crosswalk.schema.json` | Review queue et versions | closeMatch jamais exactMatch implicite |
| Couverture par langue | `kristal-dik-coverage-report.schema.json` | Matrice + JSON | direct et fallback séparés |
| Conversion des mots | `kristal-dik-conversion-plan.schema.json` | Propositions et revue | aucune citation remplacée |
| Application autorisée | À préciser avec Authoring Kit | Nouvelle révision transactionnelle | ancienne signature/empreinte inchangée |
| Report multi-Kristals | Extension de diK à définir | Agrégation par namespace sans fusion | aucun KQ homonyme fusionné entre projets |

**Principe de versionnement :** un besoin qui dépasse les schémas existants ne doit pas être « ajouté discrètement » à un JSON Framework. Il faut créer un artefact enveloppe/version de diK ou faire évoluer explicitement le Framework.
