# Épinglage du contrat Kristal Framework

Source : archive `Kristal-Framework-v11.0.0-draft.3.zip` reçue, datée du 2026-10-16. Aucun appel à GitHub n'est nécessaire pour compiler et vérifier l'exemple livré.

| diK | Source upstream Framework draft.3 | Changements locaux |
|---|---|---|
| `src/dik/_framework/dictionaries.py` | `tools/v11/dictionaries.py` | `SCHEMAS` pointe vers les schémas embarqués |
| `src/dik/_framework/coverage.py` | `tools/v11/dik_coverage.py` | Import Python relatif vers `dictionaries` |
| `src/dik/_framework/schemas/v11/*.json` | `schemas/v11/*.json` | Aucun : copies exactes |
| `examples/demo/*` | `examples/v11/*` | Fixtures d'origine inchangées, manifeste diK ajouté |

La copie du code de référence est une mesure provisoire : elle évite toute dépendance réseau et tout *drift* d'identité pendant le développement de diK. Lorsqu'une distribution officielle du moteur Framework est disponible, utiliser une dépendance épinglée et supprimer le doublon après les tests croisés.

**Règle de maintenance :** ne pas modifier la sémantique des fonctions vendoriées sans versionner la compatibilité contractuelle et revoir les assertions des tests.
