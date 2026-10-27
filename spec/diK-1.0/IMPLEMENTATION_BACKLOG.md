# Backlog découpé pour les agents — diK 1.0

Chaque tâche est **atomique**, avec préconditions et critères précis. Les agents ne doivent pas coder une tâche future en supposant que ses prérequis sont déjà disponibles.

| Ordre | Lot / exigences | Entrée | Sortie / Done when | Dépendance |
|---|---|---|---|---|
| A01 | Pin et TCK [ID,LEX,PRJ] | Code diK 0.3 + Framework draft.3 | harnais TCK, goldens, 36 tests historiques conservés | aucune |
| A02 | Domaine/ports [OPS-001..006] | A01 | règles extraites sans IO ; tests de frontières | A01 |
| A03 | Index reconstruisible [OPS-010..015] | snapshots Framework | recherche ID et lexique par index, rebuild bit-à-bit des réponses | A02 |
| A04 | Reverse search [XW-001, LEX-024] | ID, locale, type, domaine | candidats ordonnés + provenance, jamais preuve automatique | A03 |
| A05 | Moteur de décision [XW-002..005] | candidat, preuve KS, reviewer | workflow de statut, refus des doublons actifs exact | A04 |
| A06 | Composition multisource [LEX-002..006] | sources avec licence, catalogue | nouvelle révision curatée/externe, audit strict | A05 |
| A07 | Projection durcie [PRJ-001..007] | diK 0.3 compact/verbose | round-trip, ancres, clean et fallback sûr | A02, A03 |
| A08 | Migration candidate [MIG-001..005] | legacy adapter, crosswalk, source hash | plan Framework non exécutable, revue et refus de citation | A05 |
| A09 | Adaptateur producteur [MIG-004..006] | plan approuvé, Authoring Kit | révision nouvelle, ancien état intact, rollback | A08 |
| A10 | Import massif [IMP-001..005] | dump local, version, accepted exact crosswalk | staging/checkpoints/idempotence, version publiée atomiquement | A03, A06 |
| A11 | Multi-projet couverture [COV-001..006] | plusieurs graphes et catalogue | matrice KQ/KP, 301 langues, digest et delta | A03, A06 |
| A12 | Interface & API [UI,API] | cas d'usage stables | application locale usable, API locale, revue/rôles, RTL | A04..A11 |
| A13 | Sécurité/release [SEC,TCK,PERF] | logiciel complet | G1–G8, benchmarks/reprise/licences/packaging et docs | A01..A12 |

## Décomposition obligatoire de chaque lot

Pour chaque ligne : créer une branche, lier exigences, spécifier contrat d'entrée/sortie, écrire tests négatifs, coder, valider, vérifier backward compatibility, produire diff+rapport. Si une dépendance n'est pas satisfaite, bloquer avec une interface mock et documenter ce qu'elle ne prouve **pas**. Ne pas cocher A13 après les seuls tests du schéma de ce dossier.
