# diK — Contrats, tests et définition du « terminé »

## Artefacts consommés / produits

| Nom | Source de vérité | diK |
|---|---|---|
| `kristal_identity_registry` | Framework v11 / producteurs autorisés | Lecture, vérification de KQ/KP/KA/KS |
| `kristal_semantic_graph` | Framework v11 | Lecture, extraction d'identifiants |
| `kristal_dictionary_catalog` | Framework v11 | Lecture, composition des couches, contrôle empreintes |
| `kristal_wikidata_lexical_record` | Import source Wikidata | Immuable par snapshot |
| `kristal_external_lexical_record` | Import externe **approuvé** | Source/version/licence/preuves |
| `kristal_curated_dictionary` | Révisions humaines | Édition séparée, nouvelle version |
| `kristal_external_crosswalk` | Référentiel d'alignement | QID/PID ↔ KQ/KP, décision et preuve |
| `kristal_dik_coverage_report` | Généré depuis graphe+catalogue | Produit et audité, sépare KQ/KP et fallback |
| `kristal_dik_conversion_plan` | Proposition de migration | Produit / soumis à revue ; jamais appliqué automatiquement |

Le `kristal_dik_coverage_report` calcule le dénominateur des KQ et KP du graphe courant, séparément. Le `kristal_dik_conversion_plan` contient des chemins JSON Pointer précis, valeurs originales, KQ/KP proposés et statuts `pending`, `approved`, `rejected`. Les schémas exacts se trouvent dans `schemas/v11` du Framework draft.3. La vérification de la structure **n'est pas une preuve de justesse sémantique**.

## Exemple CLI Framework existant

```sh
python tools/v11/dik_coverage.py \
  --graph examples/v11/semantic-graph.example.json \
  --registry examples/v11/identity-registry.example.json \
  --crosswalk examples/v11/external-crosswalk.example.json \
  --catalog examples/v11/dictionaries/catalog.json \
  --locales fr,en,fr-CA \
  --output /tmp/couverture.json

python tools/v11/dik_conversion_plan.py \
  --plan examples/v11/dik-conversion-plan.example.json \
  --registry examples/v11/identity-registry.example.json \
  --source examples/v11/dik-legacy-sample.json
```

Ces outils sont des **références hors-ligne** déjà ajoutées au Framework. Ils ne constituent pas encore l'application diK, ni un moteur de migration, ni un indexeur Wikidata à grande échelle.

## Tests prioritaires du futur dépôt diK

**P0 — Identité / sécurité :**
- Refuser « même libellé » comme motif suffisant d'exactMatch.
- Refuser toute collision entre `wikidata:Q123` et `KQ123`.
- Isoler la portée `(namespace_id, KQ)` entre deux projets.
- Interdire la réécriture des citations et valeurs littérales lors d'une migration.
- Refuser une migration si source SHA-256, revue, schéma ou provenance ne correspondent pas.

**P0 — Dictionnaires :**
- Gérer 301 langues déclarées et clairsemer les entrées sans générer de placeholders.
- Préserver les corrections locales après mise à jour du snapshot Wikidata.
- Refuser un dictionnaire externe sans provenance, droits connus et décision d'alignement.
- Bloquer les contradictions de même priorité ; gérer alias et homonymes sans fusion.

**P0 — Complétude :**
- Calculer « KQ traduits / KQ employés » indépendamment de « KP traduits / KP employés ».
- Compter `fr-CA → fr` en fallback, pas en direct.
- Afficher 0 % pour une langue réellement absente de données, pas « non applicable » ni 100 %.
- Refuser tout score global certifié si des mots restent sans IRS dans un Kristal ancien.

**P1 — Production :**
- Import JSON/JSONL officiel et compressé Wikidata, sans charger tout le dump en RAM.
- Reprise d'import, index reproductible, diff d'instantanés et export des manques complets.
- Contrôle de licences et de confidentialité sans communication réseau implicite.

## Livraison de la première version de diK

La v0.1.0 **fonctionnelle** serait atteinte si l'interface ou la CLI peut inventorier un Kristal v11, auditer et concilier des couches lexicales, importer localement un dump Wikidata, mesurer la complétude pour des langues choisies et exporter un plan de migration non destructif, avec tests négatifs. Les approbations et l'application des plans pourront être un jalon ultérieur si elles ne sont pas encore intégrées à l'Authoring Kit.

Le présent dossier est la **spécification de diK v0.1.0**, pas une déclaration de livraison de l'application.
