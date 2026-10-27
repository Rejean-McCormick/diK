# 03 — Dictionnaires multilingues et gouvernance des couches

## LEX-001 — Deux catégories qui ne fusionnent jamais

**Lexical** : `(namespace, KQ/KP, locale[, domaine]) → label, alias, définition descriptive, provenance, statut et priorité`. **Crosswalk** : `(namespace, KQ/KP) ↔ (source externe, Q/P ou autre)`, relation, statut, preuve, revue. Le libellé externe ne devient utilisable que via l'alignement approprié et la couche lexicalement admise. Un mot commun n'est pas une clé de jointure sémantique fiable.

## LEX-002 — Catalogue et fichiers

- Catalogue unique sélectionne les langues, fallbacks, couches ordonnées, chemins relatifs, SHA-256 et versions. **Ne jamais déduire la priorité d'un nom de fichier ou d'un ordre d'itération du dossier.**
- Couches `wikidata` (snapshot importé immuable), `external` (source tiers/licence/preuve) et `curated` (corrections revues, séparées et préservées).
- Entrée curatée supérieure = choix d'affichage, pas vérité sur l'identité ni droit d'altérer le dump importé.
- Égalité de priorité et labels contradictoires = `CONFLICT`, pas premier arrivé gagnant.
- **Les fichiers restent la source de vérité** ; index SQLite, recherches FTS et caches sont reconstruisibles.

## LEX-003 — Sélection et déterminisme

Pour `(namespace, semantic_id, locale, domaine)` : valider ID + langue ; consulter couches déclarées ; ordonner par priorité du catalogue ; en cas de tie incompatible -> erreur ; sinon rendre `{label,status,effective_locale,layer_id,provenance}`. Fallback uniquement si déclaré et sans cycle. Si aucun libellé : `{label:null,status:"missing"}` et ID conservé. Pas de traduction de secours silencieuse par IA.

## LEX-004 — Versions et corrections

Une correction crée un nouvel objet curaté/reviewed, journalise auteur, décision, justification, avant/après, KS le cas échéant, source et date. Les anciens snapshots restent accessibles pour reproduire une projection historique. Une mise à jour Wikidata ne supprime ni n'édite une couche curatée. Dictionnaire externe absent de licence ou d'alignement validé : `untrusted`, exclu du canal vérifié.

## LEX-005 — Sparsité et domaines

- 300+ langues supportées comme **données clairsemées** ; pas de matrice dense `KQ×300` à créer à l'import.
- Synonymes, sens multiples, variantes régionales et domaines coexistent sans fusion automatique.
- Les préférences lexicales selon domaine doivent être explicites et versionnées ; en absence de domaine unique, signaler la concurrence.
- Préserver Unicode ; politique de comparaison NFC, sans translittération ASCII ni minuscule destructrice par défaut.

## LEX-006 — Publication

Staging privé -> validation JSON Schema + hash + licences + collision + fallback -> écriture de tous shards -> publication atomique du pointeur de catalogue -> audit postpublication. Réexécuter avec la même clé idempotente retourne le snapshot existant, jamais un nouveau contenu conflictuel sous le même ID.

## Défauts bloquants

- LEX-R1 label d'identité dans graph ; LEX-R2 fallback implicite ; LEX-R3 conflit de même priorité résolu par hasard ; LEX-R4 overwrite curated par Wikidata ; LEX-R5 licence inconnue promue comme verified ; LEX-R6 empreinte incorrecte ; LEX-R7 source non déclarée utilisée ; LEX-R8 entrée d'un autre namespace.

**Référence upstream :** `spec/v11/Dictionary-Management.md` et schémas `kristal-*dictionary*`, `kristal-external-lexical-record.schema.json`.
