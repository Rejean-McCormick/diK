# 02 — Architecture technique

## Répartition des responsabilités

| Système | Propriétaire | Peut modifier |
|---|---|---|
| Registre d'identité KQ/KP/KA/KS | Framework (règles) + producteurs autorisés | Identités via allocations gouvernées |
| Graphes sémantiques Kristal | Producteurs conformes Framework | Nouvelles révisions, jamais état historique engagé |
| Crosswalk externe | diK (opérations sous contrats Framework) | Versions et décisions d'alignement |
| Couche importée Wikidata / tierce | diK | **Nouveau** snapshot uniquement |
| Couche locale révisée | diK | Nouvelles versions avec décisions explicites |
| Index, cache, recherche inverse | diK | Régénérable, non canonique |
| Plans de conversion | diK | Propositions/revue, **non exécutables** |
| Application d'un plan | Authoring Kit, futur contrat | Nouvelle révision conforme et vérifiée |
| Projection d'échange | Integration Pack | Lecture / export sans modifier l'identité |

## Composants logiques de diK

**Project Manager.** Ouvre un workspace, inventorie Kristals, registries, namespace, langues et versions. Vérifie l'accès, ne devine pas les champs identitaires hors schéma.

**Source Manager.** Enregistre une source (fichier, snapshot, URI optionnelle, hash, droits), lance un dry-run, installe la couche immuable seulement après validation. Les sources étrangères ne sont pas des identités canonisées.

**Identity & Crosswalk Resolver.** Résout `(namespace, KQ/KP)`, puis les correspondances Wikidata/Q/P *acceptées exactes* ; expose les liens proches comme candidats seulement. Gère divergences, scissions, redirections et décisions supersédées.

**Lexical Layer Composer.** Combine catalogues, révisions et priorités. Expose `render(id, locale, domain)` et `reverse_lookup(term, locale, kind, domain)` sous formes explicables. L'index de recherche inverse sert aux propositions, **pas à l'identité**.

**Coverage Engine.** Extrait les KQ/KP distincts utilisés dans un graphe v11, calcule par langue `direct/fallback/missing/conflicted`, consolide les tableaux inter-Kristals sans effacer leurs périmètres, produit un artefact de rapport.

**Legacy Analyzer.** Analyse uniquement les emplacements où un champ joue un rôle de référent ou propriété ; prépare des candidats par mots/URN ; émet un plan avec JSON Pointer, digest source, justification et statut de revue.

**Review & Audit Ledger.** Conserve qui, quand, pourquoi et sur quelle version chaque décision a été prise, notamment les refus ; permet d'expliquer un affichage ou une suggestion a posteriori.

## Stockage file-backed et index dérivés

```text
.diK/
  project.json                    # manifeste projet : format propre à diK, à stabiliser
  sources/                        # manifestes des miroirs, sources, licences et digests
  registries/                     # références vers les registres Framework, non copies maîtresses
  crosswalks/                     # mapping KQ/KP ↔ Q/P, versionné
  dictionaries/
    catalog.json                  # contrat Framework 11.0
    imported/wikidata/<snapshot>/<langue>.jsonl[.gz]
    imported/other/<source>/<snapshot>/<langue>.jsonl
    curated/<domain>/<langue>.json
  indexes/                        # SQLite/FTS facultatif, jetable
  reports/                        # sorties reproductibles
  conversions/                    # plans et décisions, pas de remplacement direct
  audit/                          # journal append-only (format diK à définir)
```

Le répertoire est **proposé**, pas imposé par le Framework ; seuls les **schémas `schemas/v11/`** sont normatifs à ce jour. Les gros dumps bruts ne sont pas embarqués automatiquement dans un Kristal ni dans les commits de code. Les chemins du catalogue restent relatifs au répertoire du catalogue, avec validation stricte contre la traversée de chemin.

## Cycle de données

1. Découvrir la source → vérifier format, hash, provenance et droits.
2. Importer en staging → produire une couche **nouvelle et immuable** → valider.
3. Réconcilier les correspondances externes en file d'attente de revue.
4. Publier un catalogue qui fixe les couches, la priorité et le fallback.
5. Construire un index dérivé ; calculer des rapports et des candidats de migration.
6. Approbation humaine ; publier nouvelles couches/versions. Aucune étape ne modifie rétroactivement l'archive source.

## Reproductibilité / limites

Un rapport doit identifier au minimum graphe/namespace et empreintes du graphe + catalogue. L'exécution en lot multi-Kristals devra en plus figer la liste des graphes et des snapshots de crosswalk dans un manifeste diK versionné. Un service/API n'est qu'une façade de lecture ou de workflow par-dessus les mêmes fichiers, jamais une deuxième source de vérité.


<!-- DIK-DOCS-LOCAL-1 -->
## Actualisation documentaire — 22 novembre 2026

L’architecture Source Manager prévoit la gestion de sources ; le localisateur persistant multi-repo et ses adaptateurs ne sont pas encore prouvés opérationnels. Voir le [guide maître](../DIK_GUIDE_MAITRE_RESOLUTION_LOCALE.md), les [chapitres 34–43](../DIK_GUIDE_MAITRE_RESOLUTION_LOCALE.md) et l’[ADR DIK-LEX-2](../decisions/ADR-DIK-LEX-2-localiser-et-referencer.md). Ce complément est documentaire et ne change pas les contrats du Framework.

## Implémentation V4 — Source Manager local

`src/dik/resource_locator.py` introduit une couche d'inventaire **hors du canon** : racines ciblées, pointeurs absolus sous racine autorisée, métadonnées, hashes optionnels, rapport et registre daté sous `reports/resources`. Le résolveur `src/dik/resolution14.py` accepte un registre et utilise seulement les **catalogues v11 validés par Framework** comme couche lexicale raccordée ; un GF ou JSONL thématique reste une référence non alignée. Voir [44](44_SOURCE_MANAGER_V4_IMPLEMENTATION.md).


## Addendum V5.3 (documentation proposée, non implémentée)

L'inspection thématique Wikidata doit devenir un **pipeline typé**, sans confondre découverte, lecture, correspondance acceptée et publication : pointeur SHA → profil de schéma → adaptateur JSONL → extraction Q/P selon rôle de champ → jointure avec crosswalk officiel accepté → label de locale explicite **candidat** → décision de droits et d'activation séparée. Un parseur ne peut conclure à une absence de recoupement si le schéma est inconnu ou si la lecture s'arrête avant EOF. Voir [54](54_ARCHITECTURE_LECTURE_WIKIDATA_V5_3.md) et [55](55_CONTRATS_SCHEMAS_JSONL_V5_3.md). Aucun état « source active » nouveau n'est livré dans V5.2.
