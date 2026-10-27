# Manuel d'exécution pour l'IA — développer diK 1.0 sans drift

Ce document est une **procédure**, pas un prompt « fais tout ».

## Protocole d'une tâche

1. Vérifier le **SOURCE_LOCK.json** et la version de la branche courante ; énoncer ce qui est connu vs ce qui est encore proposé.
2. Choisir **une** fonction et ses exigences correspondantes dans `docs/17_TRACABILITE.md`. Ne jamais combiner simultanément renumérotation KQ, migration legacy et synchronisation Wikidata dans une seule PR.
3. Lire les sections Framework listées dans l'exigence et les schémas réels ; citer les chemins exacts, pas la mémoire d'une conversation.
4. Créer un ticket d'implémentation suivant le gabarit ci-dessous ; déclarer les préconditions, non-objectifs et risques.
5. Écrire tests positifs, négatifs et de non-régression **avant** la fonction. Import d'une source : inclure reprise/corruption ; projection : round-trip et cas clean.md ; conciliation : ambiguïtés/candidats.
6. Implémenter dans les modules désignés en injectant adaptateurs via interfaces. Interdire les hacks dans les validateurs Framework vendoriés.
7. Exécuter : tests module, 36 tests hérités v0.3, TCK pertinentes, tests de schéma, cross-repo si impact. Si timeout : rapporter les tests `NOT_RUN` et ne pas déclarer succès global.
8. Vérifier manuellement une fixture contrastant « mot label » et « identité sémantique », et une fixture contenant littéral/citation. Exiger que l'original historique soit toujours identique au SHA d'entrée.
9. Générer un diff et un compte rendu factuel. Ne pas publier ni merger sans revue humaine des changements normatifs.

## Gabarit de ticket/ordre de travail

```text
FEATURE: <nom court>
REQUIREMENTS: <liste IDs ex. LEX-003, XW-002>
UPSTREAM: <fichiers Framework concernés + SHA>
AS_IS: <comportement diK 0.3 vérifié, pas supposé>
TARGET: <comportement exact demandé par la spécification>
INVARIANTS: <KQ namespace; no text->identity; no mutable canon ...>
INPUT/OUTPUT CONTRACT: <schema & version, DTOs, error codes>
BOUNDARY: <domain/application/adapter, propriétaire de la mutation>
NEGATIVE TESTS: <noms et résultats attendus>
BACKCOMPAT: <verbose v0.2, compact v0.3, graphes anciens>
SAFETY/ROLLBACK: <idempotency, snapshots, preuves>
DONE WHEN: <commandes de vérification, pas promesses>
```

## Exemples de refus attendus d'une IA bien alignée

**Proposition** : « Remplace tous les `augustin` par `KQ1001` dans les JSON ».  
**Réponse** : *Refus de l'opération globale ; demander un inventaire des chemins à rôle d'identité, une désambiguïsation des références et un plan revu. Les citations ne doivent pas changer.*

**Proposition** : « Le dictionnaire anglais se trompe : corrigeons le KQ pour le rendre anglais ».  
**Réponse** : *Le KQ ne change pas ; proposer une nouvelle entrée curatée lexicale, versionnée, éventuellement liée au domaine.*

**Proposition** : « Wikidata vient de créer Q99999 : renumérotons KQ430 ».  
**Réponse** : *Conserver KQ430 ; enregistrer candidat crosswalk puis équivalence revue et versionnée.*

**Proposition** : « Retrouve KQ depuis la vue clean après modification ».  
**Réponse** : *Impossible de garantir la réversibilité d'un Markdown seul. Conserver l'enveloppe JSON, utiliser les ancres pour créer un patch candidat.*

**Proposition** : « 298 langues possèdent un fichier vide, donc complétude 100 % ».  
**Réponse** : *Non ; seules les traductions effectives directes comptent direct ; les fichiers vides sont manquants.*

## Checklist de fin d'une PR IA

- [ ] Fichiers et familles de contrats upstream identifiés et hashes vérifiés.
- [ ] Aucun nouvel ID ou prédicat textuel dans le canon.
- [ ] Aucune inférence d'équivalence à partir d'une similitude lexicale seule.
- [ ] Literal/citation inchangés ; provenance non perdue.
- [ ] Restauration sans reverse lookup ; ancien format lisible.
- [ ] Revue nécessaire pour toute promotion `exactMatch` / migration.
- [ ] Import reproductible, idempotent, sans écrasement.
- [ ] Index et cache reconstruisibles ; source de vérité inchangée.
- [ ] Tests positifs/négatifs, anciens tests, interop, statistiques réelles.
- [ ] Tableau PASS/FAIL/NOT_RUN et limites d'implémentation rendu.

## Addendum anti-drift candidate.2

Avant de générer un module : lire `docs/23` à `docs/26`, vérifier les sources avec `python tools/validate_documentation.py --strict`, puis exécuter `python tools/verify_reference_vectors.py`. Si l'un des contrôles ne peut être exécuté, inscrire le travail `BLOCKED` et ne pas prétendre terminer sa qualification. Ne pas modifier les décisions candidates en décisions humaines acceptées pour lever ce blocage.
