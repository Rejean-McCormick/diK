# diK — overlay cumulatif DIK-LEX-1 v0.3 (4 novembre 2026)

**Ce ZIP est fait pour être décompressé directement à la RACINE du dépôt `diK/` avec écrasement des fichiers.**

La racine cible doit déjà contenir `README.md`, `pyproject.toml`, `src/dik/`, `tests/`, `examples/` et `docs/`.

L'archive n'a **pas** de dossier enveloppe `diK/` : elle commence directement par `src/`, `tests/`, `examples/`, `docs/` et quelques fichiers Markdown à la racine.

## Procédure sans Git, sans patch

1. Faire une copie de sauvegarde du dépôt local actuel (ou archiver le dossier).
2. Ouvrir `diK_DIK-LEX-1_v0.3_OVERLAY_ROOT.zip` et **extraire tout au-dessus de la racine existante `diK/`**.
3. Répondre **Remplacer / Écraser** lorsque demandé.
4. Vérifier depuis la racine :

```sh
python tools/verify_dik_lex_overlay.py
python -m pip install -e .
python -m pytest -q
python -m dik world collection-audit --dir examples/world-dictionaries/collection-slots-v0.3
python -m dik world resource-audit --catalog examples/world-dictionaries/resource-catalog.json
```

Si `python` n'est pas le Python de votre environnement, utiliser la commande habituelle du projet, avec `PYTHONPATH=src` au besoin.

## Ce qui est inclus (cumulatif)

- **Toute la v0.1 et la v0.2** : contrat de source de découverte, registre de sources candidates, 7 910 codes ISO 639-3 de `pycountry 24.6.1` avec manifestes SHA.
- **Nouvelle v0.3** : 7 910 **emplacements de collection non peuplés**, 25 ressources candidates, parseur IANA BCP 47, récupération HTTPS opt-in du registre officiel, réconciliation ISO→IANA, observation lexicale Wikidata L/S/F, relais candidat GF, CLI `dik world`, exemples, validations et tests négatifs.
- **Documentation** : ADR proposée, guides IANA, lexèmes/GF, programme de qualification par langues.

L'overlay n'altère **pas** `spec/diK-1.0`, les schémas de Framework vendoriés ni les identités/crosswalks du projet. Les manifestes de release historiques présents dans le dépôt ne sont pas réécrits : **ce package est un overlay de développement candidat, pas une nouvelle release signée**.

## À ne pas confondre

- 7 910 *codes* ≠ 7 910 langues distinctes parfaitement recensées.
- 7 910 *emplacements* ≠ 7 910 dictionnaires.
- 25 *sources candidates* ≠ 25 sources sous licence approuvée.
- 2 lexèmes dans les **fixtures synthétiques** ≠ données Wikidata de production.
- Handoff GF ≠ grammaires GF compilées.

Aucune traduction et aucun dictionnaire de cet index de découverte n'est annoncé comme vérifié ou publié. La validation IANA est conservatrice, la fixture IANA est **synthétique**, et aucun téléchargement réseau réel n'a été testé dans cette qualification.

## Commandes utiles

```sh
python -m dik world --help
python -m dik world languages-audit --index examples/world-dictionaries/language-code-candidates.jsonl --manifest examples/world-dictionaries/language-code-candidates.manifest.json
python -m dik world sources-audit --inventory examples/world-dictionaries/source-inventory.json
python -m dik world resource-audit --catalog examples/world-dictionaries/resource-catalog.json
python -m dik world iana-audit --registry examples/world-dictionaries/iana-fixtures/synthetic-language-subtag-registry.txt
```

Pour les commandes sur le vrai registre officiel IANA et les imports de vrais dumps :
- `docs/docs/27_BCP47_IANA_ET_RECONCILIATION.md`
- `docs/docs/28_WIKIDATA_LEXEMES_GF_PIPELINE.md`
- `docs/docs/29_ROADMAP_COLLECTION_MONDE.md`

## Vérification du ZIP sans Git

`tools/verify_dik_lex_overlay.py` compare les SHA-256 des fichiers suivis avec `DIK-LEX-1-OVERLAY-MANIFEST.json`.

Il sert à vérifier la copie **immédiatement après extraction**. Si tu modifies ensuite un fichier, c'est normal qu'il signale un écart de hash. Si ton dépôt contient déjà des éditions non sauvegardées, les fichiers portant les mêmes chemins seront remplacés : faire une copie de sauvegarde avant l'extraction.

## Limites et périmètre

Tests locaux effectués sur une copie du **snapshot utilisateur du 4 novembre 2026** + overlay cumulatif. Aucun PR GitHub n'est requis pour installer cette mise à jour. Les droits d'écriture du connecteur GitHub sont actuellement insuffisants pour pousser au dépôt distant; cela n'empêche pas cet overlay local.
