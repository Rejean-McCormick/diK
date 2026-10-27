# 15 — Test de conformité (TCK) et non-régression

## TCK-001 — Sources

Toujours exécuter : (a) tests unitaires/domain diK ; (b) tests des schémas et vecteurs réels Framework v11 draft.3 ; (c) tests compat `dik.compact-projection/1.0` et verbose v0.2 ; (d) cross-repo Authoring Kit + Integration Pack ; (e) tests historiques v9/v10 lecture ; (f) attaques et tests de reprise.

Les cas spécifiés dans ce dossier ne sont **pas déjà exécutés** ; c'est une liste normative destinée à la future implémentation.

## TCK-002 — Catégories bloquantes

| ID | Propriété | Test positif | Rejet exigé |
|---|---|---|---|
| ID | Canon KQ/KP et namespace | graphe exemple validé | Q brut, label canon, namespace croisé |
| LEX | Couches/fallback | `fr-CA -> fr` déclaré | conflit égal, fallback implicite, SHA faux |
| XW | Crosswalk approuvé | accepted exact avec KS | unreviewed, 2 exact actifs, mauvais type |
| PRJ | Round-trip | `restore(export(G))==G` | restaure depuis clean.md, graph altéré |
| MIG | Migration supervisée | plan approuvé puis nouveau commit producteur | global replace, citation convertie |
| COV | Couverture séparée | KQ/KP et direct/fallback | 100% avec missing/conflict |
| IMP | Idempotence/snapshot | import répétable | écrit sous ID publié différent |
| OPS | Crash atomique | ancien catalogue visible | partial catalogue visible |
| SEC | Entrées malveillantes | escaping et quotas | traversal, injection, chaîne hostile |
| PERF | Indices/rebuild | index supprimé puis reconstruit | SQLite devient canon |

## TCK-003 — Tests d'invariants génératifs

- Générer des IDs valides de multiples namespaces, y compris mêmes numéros ; vérifier non-fusion.
- Générer littéraux arbitraires, emojis, Unicode combinant, caractères RTL et Markdown ; round-trip exact sur valeurs sémantiques.
- Générer couches dans différents ordres de fichiers ; si priorité identique, sortie stable ou erreur de conflit, jamais choix dépendant de l'énumération.
- Générer 301 tags et couverture clairsemée ; zéro langage fictivement « complet ».
- Perturber dump ou annuler job à chaque frontière de publication ; aucune mutation partielle canonique.

## TCK-004 — Oracles

Un test doit comparer sorties diK au **calcul de référence Framework** quand il existe : validation v11, couverture, audit crosswalk ; pour projection comparer equality structurelle du graphe, pas comparaison de Markdown seul. L'Integration Pack doit afficher les mêmes IDs et le même décompte de couverture que diK. L'Authoring Kit doit revérifier un plan avant migration.

## TCK-005 — Gates CI

`G1` lint/docs + schémas, `G2` tests unitaires, `G3` négatifs et propriétés, `G4` contrats Framework, `G5` interop Authoring + Integration, `G6` sécurité + reprise, `G7` bench performance, `G8` package déterministe/manifest signature selon politique. Aucun `G1–G6` en échec ou non exécuté pour RC/stable. `G7` selon budgets ratifiés ; preuves jointes.

## TCK-006 — Traçabilité

Chaque nouveau test porte un ID exigence et un cas d'essai ; chaque MUST a au moins un test positif et un test d'échec. La matrice [`17_TRACABILITE.md`](17_TRACABILITE.md) est le registre initial, à compléter par lien précis vers fichier/méthode/résultat lorsque le code sera produit.

## Révision candidate.2 — preuves machine et périmètres

`tests/requirements.json` inventorie individuellement les exigences `ID`, `LEX`, `XW`, `IMP`, `PRJ`, `MIG`, `COV`, `OPS`, `API`, `UI`, `SEC`, `PERF`, `TCK` ; pour chaque exigence, un scénario positif et négatif requis, initialement `NOT_RUN`. `tests/reference_vectors.json` sert d'oracle de décisions locales. Exécuter `tools/verify_reference_vectors.py` pour vérifier l'oracle, puis l'implémentation diK réelle contre **les mêmes vecteurs**. Le premier résultat ne remplace pas le second.
