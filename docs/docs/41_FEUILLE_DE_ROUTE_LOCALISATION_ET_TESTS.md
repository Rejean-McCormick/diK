# 41 — Plan de raccordement : de la carte à la résolution prouvée

**Ce chapitre est un plan de travail, pas une annonce de fonctionnalités livrées.** Il respecte le principe « localiser → référencer → qualifier → activer → mesurer ».

## Lot 0 — Référentiel documentaire (livré par ce pack)

- Guide maître, carte des ressources et des contrats, séparation des 126 officiels et des copies.
- Terminologie « résoudre une forme par ID » à la place de « traduire un Kristal ».
- Rapport V3 figé avec dénominateurs, traces et limites.
- ADR/fixtures non normatifs et scénarios de tests.

**Acceptation** : tous les liens relatifs des nouveaux documents fonctionnent et aucune documentation n'affirme une connexion GF/Wikidata globale non démontrée.

## Lot 1 — Diagnostic local ciblé (À développer)

- Détecter les racines listées dans [35](35_CARTE_DES_RESSOURCES_LOCALES.md) ; autoriser des racines supplémentaires explicites.
- Énumérer répertoires/fichiers sans suivre les jonctions imprévues, respecter budget et exclusions.
- Inventorier `.gf`, `.pgf`, JSON/JSONL, `.gz`, `.bz2`, catalogues v11, manifests, licences et versions.
- Enregistrer `path`, présence, `size`, SHA-256 optionnel, source d'information et motif de refus.

**Acceptation** : sur un jeu de fixtures mixte, 100 % des fichiers éligibles ciblés sont inventoriés sans écrire dans les sources, sans interpréter un index comme preuve d'existence et sans ignorer les JSON racine-liste.

## Lot 2 — Registre persistant du Source Manager (À développer)

- Créer un registre de références **propre à diK** et versionné, hors du canon Framework.
- Stocker chemin logique, chemin résolu, type, snapshot, empreinte, licence et état de preuve.
- Permettre re-découverte, détection des déplacements, déduplication par digest **sans fusion d'objets sémantiques**.
- Ajouter rapport avant/après et historique `append-only`.

**Acceptation** : relocaliser une ressource déplacée seulement si une correspondance de contenu unique et de politique existe ; faute de quoi alerte plutôt qu'une substitution silencieuse.

## Lot 3 — Adaptateurs de format (À développer)

### v11
Valider catalogue, graphe, registre, crosswalk et couches par les validateurs Framework épinglés. Une couche isolée ne devient pas sûre sans clé canonique et checksums.

### Wikidata Q/P
Identifier les dumps Q/P **réellement disponibles** ; charger uniquement les correspondances `exactMatch accepted` sans contradiction, et enregistrer les observations par locale. Ne pas convertir des `qid-lexicon.jsonl` thématiques en dump global par supposition.

### Wikidata L/S/F
Préserver lexèmes, sens, formes et features ; mapping GF explicite à approuver. Aucun lien KQ implicite.

### GF
Parser la structure et la version de `Dict*.gf`, `Lexicon*.gf`, modules RGL, interfaces GF WordBench ; demander table de mapping signée/revue, locale et paradigme. Enregistrer seulement les formes prouvées, **pas de génération de milliers de mots comme étape de réparation**.

**Acceptation** : tests négatifs pour homonymes, collisions de namespace, Q/P candidats, modules GF homonymes, révisions incompatibles et droits inconnus.

## Lot 4 — Compositeur de résolution (À développer)

- Un seul chemin logique `(namespace,KQ/KP,locale)` ; sources éligibles ordonnées explicitement.
- Résoudre par ID dans la locale demandée ; repli optionnel étiqueté.
- Différencier `forme_directe`, `forme_externe_observee`, `candidat_non_approuve`, `source_non_configuree`, `mapping_non_prouve`, `conflit`, `absent_apres_sources_activees`.
- Expliquer chaque résultat avec preuve et garder l'option de refuser un affichage non qualifié.

**Acceptation** : aucune résolution depuis une autre langue ; tests de reproductibilité à mêmes digests et décisions.

## Lot 5 — Audit des 126 officiels × 14 (À développer)

- Conserver tous les 126 dans l'inventaire ; auditer seulement les ensembles v11 complets, avec diagnostic explicite pour les autres.
- Séparer « autres copies sources » des Kristals officiels.
- Produire JSON/CSV par ID et locale, journaux, manifeste source et un ZIP de partage **sans les dictionnaires eux-mêmes**.
- Comparer V3 et V4 uniquement à périmètre et métrique constants ; expliquer les nouvelles résolutions par type d'adaptateur.

**Acceptation** : un rapport peut dire « 69 non évaluables » sans leur attribuer une forme fictive ; les nombres de sources actives et d'échecs de qualification sont toujours disponibles.

## Priorités et non-objectifs

**Priorité 1** : détecter et référencer sans copier. **Priorité 2** : alignement prouvé. **Priorité 3** : audit complet et reproductible. Pas de traduction, pas de fusion inter-namespace, pas de migration des sources, pas de push Git ni publication externe.

## Traçabilité des tests

| ID | Test | Classe |
|---|---|---|
| LOC-01 | Racines Spek et GF non existantes restent `declared`, pas `found` | découverte |
| LOC-02 | ZIP/dossier contenant `../` ou symlink sortant refusé | sécurité |
| LOC-03 | JSON liste hors contrat GF ne provoque pas d'exception | robustesse |
| LOC-04 | Gros dump lu par flux avec budget | ressources |
| ID-01 | KQ/Q suffixe numérique égal n'implique rien | sémantique |
| ID-02 | Candidate Q/P jamais utilisée pour affichage | revue |
| ID-03 | Conflits inter-catalogues explicités | priorité |
| LANG-01 | 14 tags conservés ; `no != nn` sauf règle revue | locale |
| GF-01 | Fichier GF sans mapping KQ non activé | grammaticale |
| PORT-01 | 126 officiels, copies non comptées | portefeuille |
| PORT-02 | 69 non évaluables exclus du dénominateur lexical | métriques |
| REPRO-01 | Même manifeste/snapshots => même résultat | reproductibilité |
| SEC-01 | Audit ne modifie aucun source | mutabilité |
| SEC-02 | Aucun trafic réseau déclenché sans demande | réseau |

Ces tests sont **des critères proposés**, pas une affirmation de leur présence dans la suite `pytest` actuelle.

## Suivi d'avancement V4 (2026-11-22)

- **Lot 1 — partiellement réalisé** : découverte ciblée de chemins GF, Wikidata JSONL, catalogues v11, exclusions, empreintes bornées et CSV ; l'analyse exhaustive de toutes les racines, des licences et des formats complexes reste à développer.
- **Lot 2 — partiellement réalisé** : registre JSON persistant et daté plus pointeur `latest`, vérification des empreintes. Relocalisation automatique par digest et décisions de publication **non livrées**.
- **Lot 3 — partiellement réalisé** : raccordement de catalogues v11 **déjà audités**, pointage explicite de dumps Wikidata Q/P candidats. Aucune activation GF ou L/S/F↔KQ.
- **Lot 4 — non achevé** : résolution V3 avec sources choisies via registre, pas de compositeur universel de morphologie GF.
- **Lot 5 — partiellement réalisé** : portefeuille officiel et 14 langues déjà pris en charge par V3 ; V4 ajoute provenance du registre. Les 69 non évaluables restent à diagnostiquer.

L'implémentation mesurable est détaillée dans [44](44_SOURCE_MANAGER_V4_IMPLEMENTATION.md) et les tests dans [46](46_VALIDATION_ET_LIMITES_V4.md).
