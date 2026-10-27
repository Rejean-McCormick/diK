# 24 — Algorithmes de référence et vecteurs exacts

**Autorité :** Framework v11 draft.3 pour l'identité et la résolution lexicale. Les algorithmes ci-dessous explicitent son emploi dans diK ; ils ne remplacent pas le code ou les schémas officiels.

## 24.1 Résolution d'un libellé (`LEX-003`)

Entrée : `(namespace_id, semantic_id, requested_locale, catalog_sha256, optional domain)`. Charger le catalogue validé par manifest, sans énumérer le disque librement. Lire la locale demandée puis, **dans l'ordre déclaré**, les locales fallback ; refuser cycles et langues non déclarées. Pour chaque locale effective, prendre les couches déclarées ; la **plus grande valeur numérique** `priority` l'emporte (conforme au résolveur de référence v11 draft.3). Si plusieurs termes différents sont à la priorité maximale : `conflicted`; un même terme répété à la même priorité n'invente pas plusieurs sens. Si aucune couche ne fournit le terme, passer au fallback explicite ; sinon `missing`. La locale demandée a préséance sur un fallback même si la couche fallback possède une priorité numériquement supérieure.

Sortie normative de base : `status, semantic_id, requested_locale`; si résolu, `effective_locale, fallback, term, layer`. Pour diK, ajouter provenance et digests dans une **enveloppe dérivée** sans réécrire la sortie Framework. Ne pas promettre qu'un label suffit à définir le sens.

## 24.2 Recherche inverse (`XW-001`)

Entrée `(namespace, term, locale, expected_kind KQ|KP[,domain], index_digest)`. Comparer Unicode NFC, rechercher exclusivement la langue demandée (à moins d'un paramètre séparé de fallback) et le type attendu, renvoyer les **identifiants candidats** triés par `(namespace_id, semantic_id)` pour une représentation déterministe. Pas de `exactMatch` par égalité du terme. Un seul candidat donne `unique_candidate`, jamais `accepted`. Plusieurs candidats : `ambiguous` ; zéro : `no_candidate`. Les alias ne sont pas nécessairement des traductions. Un moteur de similarité peut enrichir les candidats, mais doit fournir provenance, méthode et score sans pouvoir approuver.

## 24.3 Correspondance externe (`XW-002..004`)

Valider : espace de noms, classe KQ→Q ou KP→P, relation exacte, statut `accepted`, décision et méthode, identité de réviseur autorisé et preuves KS, unicité active des deux côtés dans le même snapshot. Toute correspondance `candidate|rejected|superseded` ou `related|close|broad|narrow` est non substituable. Réception d'un nouveau Q externe : proposer et réviser un nouveau crosswalk ; conserver le KQ, le graphe et les SHA historiques inchangés.

## 24.4 Couverture (`COV-001..006`)

Inventorier les *références distinctes* par `(namespace_id, KQ|KP)` dans le graphe, y compris les qualificatifs ; KA et KS n'entrent pas au dénominateur lexical. Pour chaque langue demandée : `direct` si label validé dans cette langue, `fallback` si label résolu uniquement par repli déclaré, `missing` sans terme, `conflicted` si conflit non résolu. Les classes sont disjointes ; leur somme = dénominateur. `complete_direct = (direct == denominator && conflicted == 0)` ; `complete_usable = (direct + fallback == denominator && conflicted == 0)`, **sous réserve que le dénominateur soit connu**. Un dénominateur vide est marqué `not_applicable`, pas « 100 % traduit », dans les tableaux diK (ce statut de présentation ne modifie pas le schéma Framework). Un graphe historique contenant un mot non résolu signale `legacy_denominator_unknown` et ne peut être déclaré complet à 100 %.

## 24.5 Projection et restauration (`PRJ-001..007`)

Export : charger le canon validé ; construire table des libellés une seule fois par ID utilisé ; conserver **le graphe canonique complet** dans l'enveloppe réversible et joindre digest du graphe/cat/version du résolveur. Rendu annoté inclut les IDs ; rendu épuré masque l'ID en UI/Markdown seulement. Restore : vérifier intégrité et provenance selon le profil ; renvoyer `canonical_graph` **sans** inférer depuis `label`/Markdown. Vue `clean.md` seule : `NOT_REVERSIBLE` ; changement sémantique en lecture : produire intent de patch, sans mutation canonique.

## 24.6 Écritures, reprise et idempotence (`OPS-001..015`)

Avant chaque mutation, calculer une clé stable à partir du manifeste et de paramètres fixés ou demander une clé explicite, liée au *digest de l'entrée*. Journaliser `idempotency_key`, `input_digest`, `tool_version`, `state`, `result_digest`. Même clé + même digest : retourner le résultat existant ; même clé + digest différent : `IDEMPOTENCY_CONFLICT`. Concurrence : sérialiser publication avec verrou et comparer pointeur actif attendu ; jamais deux publications concurrentes sous une révision. Écrire temporairement tous les fichiers, vérifier SHA et droits, synchroniser stockage, **puis seulement** publier atomiquement un manifeste/pointeur. Un crash antérieur ne doit pas rendre le staging visible. Un crash post-publication doit permettre une lecture cohérente ou un rollback explicite vers snapshot antérieur validé.

## 24.7 Migration des anciens graphes (`MIG-001..006`)

Identifier uniquement les champs jouant le rôle de références sémantiques, **pas** les citations/valeurs littérales ; enregistrer chemin JSON exact, ancien texte/URN, namespace, candidats, preuves et `source_graph_sha256`. Le plan reste non exécutable dans diK. Toute ambiguïté nécessite revue humaine. L'Authoring Kit/producteur valide de nouveau la source et chaque choix avant de publier une **nouvelle révision** ; l'original et son engagement sont inchangés.

## 24.8 Formes d'échec stables

`BLOCKED: CONTRACT_CONFLICT`, `INVALID_NAMESPACE`, `AMBIGUOUS_IDENTITY`, `UNVERIFIED_ALIGNMENT`, `LEXICAL_CONFLICT`, `MISSING_TRANSLATION`, `INTEGRITY_MISMATCH`, `STALE_SOURCE`, `IDEMPOTENCY_CONFLICT`, `NOT_REVERSIBLE`, `UNAUTHORIZED_MIGRATION`, `UNDECLARED_LOCALE`, `UNTRUSTED_SOURCE`. Le code CLI/API peut posséder une enveloppe typée additionnelle, mais ces erreurs ne doivent pas être transformées silencieusement en succès.

## 24.9 Source des oracles

`tests/reference_vectors.json` contient des cas **documentaires reproductibles**. `tools/verify_reference_vectors.py` les vérifie indépendamment d'une future implémentation. Les tests d'intégration de diK 1.0 doivent charger les mêmes vecteurs et produire les mêmes résultats, ainsi que les fixtures complètes Framework v11. Un succès de ce petit oracle documentaire **ne** prouve **pas** la conformité de diK.
