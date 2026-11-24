# 47 — Revue du paquet diK V4.1 et cohérence des sources

**Date : 23 novembre 2026. Statut : correctif audité sur la copie Linux ; Windows à confirmer.**

## Périmètre effectivement livré

- Une **copie complète du dépôt** de référence sous `repo/` dans le ZIP. Le lanceur n'installe pas aveuglément tout `repo/` : il applique un **patch ciblé** contrôlé par `FILES_SHA256.json` et les empreintes locales autorisées, dans le répertoire diK déjà existant.
- Découverte hors ligne et inventaire sans activation automatique de ressources. Références conservant les fichiers à leur chemin d'origine. Les SHA calculés localement vérifient la stabilité, pas l'authenticité du producteur.
- Résolution de `(namespace, KQ/KP, locale)` par catalogues v11 audités et Q/P Wikidata **acceptés**. Aucun passage d'une langue à une autre. Les fichiers GF `.gf`, `.pgf` et JSONL thématiques Wikidata restent de simples candidats.
- 126 dossiers officiels attendus sous le portefeuille connu. 57 évaluables et 69 non évaluables correspondaient au rapport antérieur, pas à un invariant du nouveau scanner.

## Erreurs détectées et corrigées dans le pack

1. **Bug PS7 :** une pipeline de filtrage de chemins peut retourner une seule chaîne. Avec `[0]` le script passait le caractère `C` au lieu du chemin complet. Désormais une capture `@(...)` force un tableau.
2. **Vérification d'inventaire :** une empreinte modifiée ou une ressource disparue rend `sources verify` en erreur ; les entrées sans hash produisent le statut `INCOMPLETE`.
3. **Information de version :** les manifestes `RELEASE*` existants attestent une distribution antérieure alpha.7 et `docs/MANIFEST_SHA256.json` atteste une ancienne documentation 0.2.0. Ils restent historiques. Le ZIP V4.1 fournit un manifeste SHA-256 propre au dépôt inclus, séparé des attestations historiques.

## Risques et limites non levés

- **Aucun banc d'essai PowerShell 7 natif Windows** dans l'environnement de revue. L'élévation UAC n'est pas requise en usage normal mais les droits locaux peuvent bloquer les écritures.
- La classification de ressources dépend de racines connues et de noms de fichiers : elle peut manquer des ressources hors de ce périmètre. Les racines supplémentaires sont explicitement paramétrées.
- Les gros dumps au-dessus de la limite de hachage sont inventoriés mais non certifiés ; une recherche tronquée (`truncated=true`) rend l'inventaire non exhaustif.
- Aucun alignement GF ↔ KQ/KP automatique. Aucun import Lexème/L/S/F global ni homologation des licences GF/Wikidata.
- Les 69 Kristals sans ensemble v11 exploitable sont recensés mais ne participent pas au dénominateur des résolutions.
- La commande `sources verify` est stricte vis-à-vis des sources modifiées ; elle ne transforme pas des candidats GF en libellés résolus.

## Contrôles réalisés

- `PYTHONPATH=src python -m pytest -q` : 270 tests réussis, 1 ignoré, 11 sous-tests réussis.
- Compilation de tous les modules Python.
- Vérification des empreintes de chaque fichier du correctif, de leur correspondance avec le dépôt inclus et du manifeste global du ZIP.
- Analyse statique de l'installateur : validation avant remplacement, sauvegardes, refus des chemins inconnus ; transaction de restauration en cas d'exception. Aucun déploiement Windows réel attesté.
