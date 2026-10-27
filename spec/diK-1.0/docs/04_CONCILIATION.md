# 04 — Conciliation multisource et résolution inverse

## XW-001 — Recherche candidate, pas attribution d'identité

Entrée obligatoire : `term`, `locale`, `expected_kind` (`KQ`/`KP`), `namespace_id` et facultativement domaine KQ, provenance et type de source. La recherche explore exact Unicode normalisé, alias, descriptions, relations existantes et types contextuels ; les variantes fuzzy sont **des candidats**. Sortie : ensemble déterministe de candidats identifiés, raison par signal, distance/type de relation, preuves, dictionnaires/snapshots consultés et état `ambiguous|unique_candidate|no_candidate`. Un seul candidat n'est **pas** une équivalence définitivement approuvée.

## XW-002 — Machine d'états des rapprochements

`proposed -> reviewed -> accepted | rejected`; `accepted -> superseded` avec nouvelle décision. Les rapprochements `closeMatch/broadMatch/narrowMatch/relatedMatch` ne deviennent jamais `exactMatch` implicitement. Une acceptation exige : identifiant de décision, réviseur autorisé, méthode, lien d'évidence `KS`, version des sources, justification et contrôle d'unicité active. Il n'existe pas d'acceptation simplement parce que le score est > 0.99.

## XW-003 — Multi-dictionnaires

- Comparer les sources sans confondre les clés locales des fournisseurs avec les clés KQ.
- Sources contradictoires : conserver les deux options avec score explicatif ; priorisation d'affichage dans le catalogue ; alignement sémantique via décision distincte.
- Importer uniquement si droit d'usage compatible ; stocker attribution/licence et obligations de redistribution par source.
- Conserver chaque décision, y compris rejet ; une prochaine synchronisation ne doit pas re-proposer en boucle un rejet identique sans nouvel élément de preuve.

## XW-004 — Crosswalk Wikidata

`(namespace,KQ) ↔ (wikidata,Q)` et `(namespace,KP) ↔ (wikidata,P)` seulement, sans mélange. Les contraintes de mapping `accepted exact` du Framework s'appliquent à chaque vue active. Pour un nouveau Q Wikidata : créer `candidate`, évaluer puis publier une révision ; **aucun KQ modifié**. Pour Q redirigé, supprimé, scindé, fusionné : événement de revue + éventuel superseding, pas substitution immédiate.

## XW-005 — Corrections et annulations

Toute promotion/rejet/supersession s'écrit dans un journal append-only pour audit et est matérialisée dans une nouvelle vue active. Les prévisualisations peuvent être annulées sans effet. Les décisions déjà publiées sont contredites par un événement nouveau, jamais éditées rétroactivement.

## TCK conciliation

- `XW-T1` mot identique lié à deux KQ -> deux candidats, aucun auto-mapping.
- `XW-T2` accepted exact sans KS/reviewer -> rejet.
- `XW-T3` double exact accepté actif dans la même vue -> rejet ou supersession explicite.
- `XW-T4` Q externe associé à KP -> rejet.
- `XW-T5` snapshot externe change de libellé -> KQ et anciennes décisions intacts.
- `XW-T6` couche externe sans licence -> quarantaine.
- `XW-T7` reverse lookup par locale incorrecte -> ne pas silencieusement rechercher dans toutes les langues.
