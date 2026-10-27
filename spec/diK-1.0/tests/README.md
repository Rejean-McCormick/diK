# TCK diK 1.0 — catalogue de tests à exécuter

`TCK_CASES.json` décrit 30 cas de conformité initiaux, **tous `NOT_RUN` dans cette documentation**. Lorsqu'on code diK 1.0, créer de vrais tests automatisés et enregistrer leur exécution (`PASS`, `FAIL`, `NOT_RUN`) avec commandes, environnement et SHA du code. Aucun résultat du catalogue n'est une affirmation de test déjà réussi.

Pour valider le contenu de ce dossier (sans tester diK 1.0), exécuter :

```bash
python tools/validate_documentation.py
```

Le script vérifie les schémas applicatifs et fixtures, le lock des sources si celles-ci sont disponibles, les liens Markdown locaux et la cohérence du manifeste TCK. Les **36 tests unitaires de diK 0.3** ont été exécutés séparément sur le snapshot source : ils ne démontrent pas la conformité 1.0.

## Éléments candidate.2

- `requirements.json` : liste exhaustive des **87 identifiants réellement titrés** dans `docs/17_TRACABILITE.md`. Paires de tests encore `NOT_RUN`.
- `reference_vectors.json` : cas compacts, lisibles par machine, pour les principes hors-Framework de la cible.
- `../tools/verify_reference_vectors.py` : exécute les cas documentaires, **pas** la future application.
