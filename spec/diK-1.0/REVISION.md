# Révision de la spécification diK 1.0 — candidate.2

**Statut :** spécification *cible* consolidée, pas certification du produit diK 1.0. Cette révision **ne modifie pas** Kristal Framework v11 draft.3 ni le code diK v0.3.0.

## Corrections apportées après revue

1. **Décisions d'implémentation :** un profil local mono-utilisateur/hors ligne est défini pour lever les ambiguïtés qui bloquaient le codage ; ce sont des décisions **candidates de ce dossier**, non des acceptations de gouvernance effectuées par un humain. Le réseau multi-acteurs, les signatures, les nouvelles versions de formats et les choix de rétention organisationnels restent des *extensions conditionnelles*.
2. **Algorithmes reproductibles :** déductions de labels et fallbacks, résolution inverse, vérification d'alignements, couverture, changements de snapshots, ordre de tri, idempotence et migration sont décrits par entrées, sorties, codes d'échec et invariants (voir docs/24).
3. **Test oracle documentaire :** `tests/reference_vectors.json` + `tools/verify_reference_vectors.py`. Les cas exécutables vérifient les décisions du dossier ; ils ne certifient **pas** une future implémentation diK.
4. **CI bloquante :** `python tools/validate_documentation.py --strict` échoue en absence de tous les fichiers `SOURCE_LOCK` et de Framework monté ou en cas de hash incorrect ; la vérification standard reste utilisable pour consulter la documentation isolée.
5. **Traçabilité structurée :** `tests/requirements.json` énumère les identifiants normatifs, l'oracle attendu, les preuves positives/négatives et leur état futur `NOT_RUN`. L'exécutable documental ne transforme aucun test produit en `PASS`.
6. **Performances :** objectif chiffré séparé de budget **ratifié** et profil machine ; protocole froid/chaud, comparaisons brut/compressé, mémoire/disque, seuils de régression et datasets vérifiables.
7. **Critères release :** le blocage en absence de preuves (cross-repo, restore, crash, taille Wikidata, 301 langues, sécurité) est écrit comme un contrôle automatisable et non une déclaration générale.

### Décisions encore humaines

- Validation formelle du profil local et des interfaces applicatives candidates ; aucune IA ne peut auto-approuver une ADR.
- Choix des politiques de distribution multi-acteurs / signatures / SLA de production si ces modes deviennent obligatoires.
- Ratification des budgets performance sur matériel de référence après premières mesures.

Pour comprendre la portée : `VALIDATION.md`, `SPEC_LOCK.md`, `tests/requirements.json` et `docs/25_GATES_CI_EXECUTABLES.md`.
