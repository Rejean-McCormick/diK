# AGENTS.md — Règles obligatoires pour toute IA générant du code diK

**Portée :** intégralité du dépôt, tous langages, PR, assistants et agents. Ce document est normatif pour l'implémentation visée.

## Procédure de travail imposée (anti-drift)

1. **Lire** `SPEC_LOCK.md`, la présente page, puis l'exigence pertinente et le schéma Framework correspondant. Si aucun contrat disponible : **stopper la modification concernée et marquer `BLOCKED`**.
2. **Étiqueter** chaque demande avec au moins un identifiant d'exigence `ID-`, `LEX-`, `XW-`, `PRJ-`, `MIG-`, `COV-`, `IMP-`, `OPS-`, `SEC-`, `PERF-`, `UI-`, `API-`. Voir `docs/17_TRACABILITE.md`.
3. **Écrire d'abord** un test qui prouve l'invariant positif ET au moins un test de refus en cas de danger sémantique. Ne pas coder d'abord en « devinant » le comportement.
4. **Modifier uniquement** le module propriétaire : le cœur identités ne connaît ni SQLite ni réseau ; imports et formats historiques passent par adaptateurs.
5. **Lancer** les tests du module + TCK transversal + validation des exemples Framework. Aucune exception du linter/validateur pour faire passer une fonctionnalité.
6. **Rendre compte** avec tableau `exigence / fichiers modifiés / tests PASS, FAIL, NOT RUN / divergence / données préservées`, SHA des fixtures de comparaison ; ne pas déclarer la version stable si la suite n'a pas fini.
7. **Changer de contrat ?** Arrêter le patch ; écrire une ADR et une proposition de nouvelle version, demander validation humaine avant toute modification incompatible.

## Interdits absolus

- `label`, `name`, `preferred_label` ou une propriété en langage naturel dans le **graphe canonique v11** ; pas de `wikidata:Q…` ou `Q…` comme identifiant interne.
- Création d'un KQ par traduction, recherche textuelle ou score seul ; réutilisation d'un ID émis ; fusion implicite de KQ.
- Équivalence « accepted exact » basée sur la similarité des noms sans revue + preuve `KS` ; `relatedMatch`, `closeMatch`, candidats ≠ `exactMatch`.
- Réécriture en masse de chaînes, citations, valeurs littérales ou engagements historiques ; modification in situ des anciens Kristals.
- Inférence d'identité en restaurant une projection à partir du Markdown ou d'une traduction. La restauration provient des identifiants conservés.
- Écriture silencieuse d'un label automatique parmi les termes vérifiés ; invention de langues couvertes.
- Modification automatique des schémas Framework vendoriés, de leurs tests ou de leurs empreintes.
- Utilisation du cache SQLite comme registre canonique ; suppression d'une couche curatée lors de la mise à jour Wikidata.
- Appel réseau implicite pendant une opération purement locale, ni exécution de code depuis un dictionnaire.
- Déclaration « 300 langues complètes », « certifié Wikidata massif », « final » sans mesures/preuves.

## Règles d'interprétation

- `MUST` / **DOIT** : condition bloquante ; `SHOULD` : recommandation justifiée ; `MAY` : extension compatible.
- Source-of-truth : registre + graphe Framework, catalogues/crosswalks versionnés ; toute vue est dérivée.
- L'identifiant de référent sémantique **IRS** désigne KQ, pas KP ni KA/KS.
- Une traduction est une donnée linguistique contextualisée, pas un fait doctrinal ni une preuve d'identité.
- En cas d'ambiguïté : préserver les originaux, produire candidat+raison, bloquer l'application automatique.

## Contrat de sortie d'une IA (à inclure dans chaque PR)

```text
Exigences: ID-..., LEX-...
Autorité Framework: 11.0.0-draft.3, schémas SHA connus
Type de changement: additive | correction compatible | incompatible(BLOCKED)
État migration des données: aucune | proposition | appliquée par producteur autorisé
Tests: N pass, M fail, K not-run (liste)
Preuves: commandes, checksums, fichier de comparaison
Exceptions/ouvertures: ...
```

**Un agent ne peut ni inventer l'autorisation d'une migration ni approuver ses propres rapprochements en prétendant à une revue humaine.**

## Addendum candidate.2 — obligations vérifiables

- Traiter le **profil local** de `docs/23_...` comme le choix proposé par défaut seulement ; aucun agent ne peut marquer `ADR-0003` accepted ou décider du propriétaire du namespace KQ.
- Ne jamais annoncer une certification quand seule la commande documentaire passe : `--strict` exige 13/13 sources et les vrais schémas Framework. `tools/verify_reference_vectors.py` vérifie les oracles documentaires, pas le logiciel final.
- Toute implémentation doit relier sa PR aux IDs exacts de `tests/requirements.json`, à au moins un test positif et négatif ainsi qu'aux preuves de résultats `PASS / FAIL / NOT_RUN`. Zéro succès implicite.
- Conserver le comportement Framework pour la priorité lexicale (maximum numérique) et pour le fallback (ordre déclaré, locale demandée avant fallback). Pas d'algorithmes alternatifs inventés.
