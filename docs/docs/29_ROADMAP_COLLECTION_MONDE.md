# 29 — DIK-LEX-1 : programme de construction de la collection mondiale

## Point de départ de cette livraison

- 7 910 **codes candidats** ISO 639-3, avec SHA-256 et provenance (`pycountry 24.6.1`).
- 7 910 **emplacements clairsemés et vides** dans un index mondial (`collection-slots-v0.3/`).
- 25 **ressources documentaires ou lexicales candidates** dans `resource-catalog.json`; **zéro licence approuvée** et **zéro donnée importée**.
- Un parseur IANA local et des contrôles BCP 47 prudents; récupération HTTPS officielle sur demande.
- Un pipeline local Wikidata L/S/F jusqu'à observations + relais candidat GF.
- Aucun corpus intégral de Wikidata, Wiktionary, GF ou autres ressources n'est inclus.

## Trajectoire de production — ordre de dépendances

### A — Autorités linguistiques et codes

1. Geler un registre officiel IANA avec date et SHA approuvé à part; valider les tags BCP 47 employés par le projet.
2. Réconcilier ISO 639-3 et IANA en identifiant les aliases, variantes, scripts et régions qui exigent un examen humain.
3. Optionnel : greffer CLDR/Glottolog/ISO 15924 comme sources indépendantes, jamais comme traduction du corpus lexical.

### B — Sources linguistiques et permissions

1. Établir pour chaque source : identifiant, URL exacte, version, hash, licence, preuve de réutilisation, langues couvertes *mesurées*, limites contractuelles et mode d'extraction.
2. Refuser toute diffusion de texte tiers sans autorisation; les **identifiants Wikidata** vers des dictionnaires fermés n'emportent aucun droit de copier leur contenu.
3. Publier des snapshots externes inchangés, puis des transformations réversibles ou explicitement partielles, avec rapports séparés.

### C — Alignements sémantiques

1. Importer labels Q/P seulement avec crosswalks Kristal `exactMatch` acceptés et preuves KS.
2. Conserver lexèmes L/S/F dans le canal lexical indépendant.
3. Unifier les domaines, préférences de libellés, variantes de langue, conflits et provenance via diK; ne jamais joindre sur le texte seul.

### D — Réalisation grammaticale

1. Établir le mapping explicite `Wikidata Q grammatical -> GF`, avec vérification par linguistes.
2. Lier SemantiK à la grammaire GF ciblée par langue et domaine.
3. Qualifier les formes générées, les homonymes, les voix et scripts, sans confondre forme grammaticale et définition sémantique.

### E — Qualification inter-dépôts

1. Comparer diK / Framework / Authoring Kit / Integration Pack sur le même catalogue versionné.
2. Exécuter des tests de conflits, fallbacks, alignements, licences, audits de SHA, rollback et idempotence.
3. Mesurer la performance P95 sur un **vrai** corpus massif avant de certifier les budgets prévus.

## Statuts de couverture non interchangeables

`code_connu` → `tag_iana_controle` → `source_declaree` → `source_licence_revue` → `donnees_observees` → `alignement_revu` → `libelle_curated` → `dictionnaire_publie`.

Une source observée en 2026 n'implique pas que le vocabulaire d'une langue ancienne, d'une macrolangue ou d'une variante locale soit complet. Chaque statut doit avoir sa preuve et ses compteurs indépendants; on ne fabrique pas un grand tableau `KQ x 7910` rempli de chaînes vides.
