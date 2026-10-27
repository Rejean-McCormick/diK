# 25 — Gates CI anti-drift : du dossier à l'implémentation

## Différence cruciale entre 3 niveaux de preuve

- **D1 : validation du dossier.** Schémas candidats, liens, référence SHA, matrice, vecteurs oracles, aucun résultat TCK inventé.
- **D2 : conformité du logiciel.** Même jeux de vecteurs exécutés sur **diK 1.0 réel** et sur validateurs Framework officiels ; preuves liées à commit, versions et environnement.
- **D3 : qualification produit.** Tests de reprise/crash, sécurité, cross-repo, benchmarks et restauration sur corpus représentatifs, 301 langues sparse, revue humaine des écarts.

**Jamais D1 ⇒ D2 ni D2 ⇒ D3.** Exécuter `--strict` sur D1 est un garde-fou documentaire, pas une certification produit.

## Commandes D1 reproductibles

```bash
python -m pip install 'jsonschema>=4.21,<5'
python tools/validate_documentation.py
python tools/verify_reference_vectors.py
# Blocage si les fichiers source et le Framework montés ne correspondent pas au verrou :
DIK_SOURCE_DATA_ROOT=/mnt/data KRISTAL_FRAMEWORK_ROOT=/mnt/data/work_kristal_v11_draft3 \
  python tools/validate_documentation.py --strict
```

Sans montages, la commande stricte **DOIT échouer** : il est interdit d'émettre `PASS` au lieu de `NOT_VERIFIED`. Une CI diK 1.0 réelle installera les sources épinglées dans un emplacement dédié de façon reproductible.

## Gates D2/D3 (à développer dans le dépôt applicatif)

| Gate | Tests obligatoires | Bloque release stable si |
|---|---|---|
| G1 Documentation | D1 strict + schémas et versions | sources absentes, SHA différents, contrats inconnus |
| G2 Module | positifs+négatifs liés aux IDs des exigences | scénario attendu `NOT_RUN/FAIL` |
| G3 Invariants | fuzz/Unicode/RTL, intégrité, aucun Q dans canon, non-fusion | un seul contre-exemple |
| G4 Framework | validateurs réels, golden fixtures, graphe v11, compat v0.2/v0.3 | hash ou sortie diverge |
| G5 Intégrations | Authoring Kit et Integration Pack en versions verrouillées | interprétation différente d'un même graphe |
| G6 Sûreté | corruption, crash chaque étape, quarantaine, import malveillant, rollback | mutation canonique ou perte de snapshot |
| G7 Performance | banc mesuré et budgets ratifiés, mémoire et tailles | dépassement ratifié, rapport absent |
| G8 Packaging | reproductibilité, installation offline, SBOM et attribution | manifeste divergent ou install impossible |

## Traçabilité bloquante

`tests/requirements.json` fournit un identifiant **individuel** pour les 87 exigences titrées de la spécification ; chaque ligne doit pointer vers un test positif ET un test négatif (ou justification de non-applicabilité signée en ADR), une preuve d'exécution et une version source. Tant que `NOT_RUN`, la couverture D2/D3 est 0 %, non pas « implicite par la documentation ». Les résultats doivent être produits par CI, pas édités à la main.

## Revue automatique de dérive

Échec si le diff introduit une identité interne `Q[0-9]+` à la place de KQ, un champ `label` de propriété canonique, un accès réseau implicite dans une fonction pure, une suppression d'historique, une approbation construite avec score seul, une désactivation de schéma ou un changement de profil compact sans version. Analyse statique heuristique = alerte ; les validateurs structurés/fixtures sont la preuve. On ne « corrige » pas la CI en supprimant son test.

## Résultats et gouvernance

Chaque PR conserve `.evidence/<sha>/` (outside documentation spec) : commandes exactes, logs structurés avec PASS/FAIL/NOT_RUN, SHA entrées/sorties, version Python et plateforme. Un agent n'est pas habilité à signer une revue humaine. Avant release, toutes décisions bloquantes passent par une ADR approuvée par propriétaire réel.
