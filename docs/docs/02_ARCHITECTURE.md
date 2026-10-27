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
