# 12 — Interface utilisateur complète

## UI-001 — Espaces principaux

1. **Vue Projets** : état de validité, Framework lié, namespace, graphes, dictionnaires, fraîcheur du miroir, tâches en cours.
2. **Sources de dictionnaires** : ajouter source Wikidata/tiers/fichier, licence, langues, provenance, statut, snapshot, priorité proposée ; jamais importer une source externe comme fiable sans contrôle.
3. **Atelier lexical** : chercher un KQ/KP ou un terme, comparer termes par langue et par domaine, revoir synonymes/corrections, preview des priorités/fallbacks.
4. **Conciliation** : file de candidats, vues côte à côte, relations exact/close/broad/narrow/related, preuves, décideur, raisons, refus/supersession.
5. **Complétude** : matrice Kristals × langues, filtres `KQ/KP`, direct/fallback/missing/conflicted, exports, delta entre snapshots.
6. **Projections** : choix graphe, langue/variante, clean/annotated, preview, export JSON réversible + rendu non réversible, verify, restore.
7. **Migration** : inventaire des rôles legacy, propositions/rejets, revue de chaque JSON Pointer, rapport source/commitment, plan envoyé au producteur.
8. **Audit et jobs** : historique, versions/hashes, erreurs structurées, téléchargements/imports/reprises et annulations.

## UI-002 — Modèle de confiance visible

Afficher **toujours** ce qui est `verified`, `candidate`, `unreviewed`, `missing`, `fallback`, `conflicted`. Aucun code couleur seul : statuts textuels, tooltip avec source et décision, icônes accessibles. Distinguer `un label disponible` de `une identité correctement alignée`. Un bouton « Accepter » doit indiquer les conséquences et nécessite un rôle autorisé.

## UI-003 — Lecture légère

Rendu clean ne montre pas obligatoirement les KQ mais chaque fragment peut ouvrir son détail (ID/namespace/source/langue/provenance). Les KQ manquants restent visibles comme lacune au lieu d'être remplacés par un mot conjectural. Mode annoté pour IA affiche références contextualisées, sans alourdir le canon. Un sélecteur de langue ne charge pas 300 dictionnaires.

## UI-004 — UX de revue

Vue diff avant/après ; afficher la phrase, l'ID cible, contexte type/propriété, source, licence et éventuelles ambiguïtés ; actions `proposer`, `rejeter`, `accepter avec preuve`, `différer`. La revue doit résister à double clic et perte réseau (clé idempotente, révision attendue). Impossible de passer `candidate` à accepted via simple tri/filtre.

## UI-005 — Accessibilité

Support navigation clavier, lecteurs d'écran, internationalisation, RTL (arabe, hébreu…), scripts multiples, très longs labels, et affichage d'alias non romains sans translittération forcée. Langue UI indépendante du choix de dictionnaire. La qualité des textes de 300 langues reste mesurée, non prétendue.

## UI-006 — Déploiement

Application locale utilisable sans compte cloud ; interface GUI portable selon technologie retenue. Une implémentation web locale ne doit pas exposer par défaut fichiers privés/dumps sans permission. Pas de télémétrie réseau cachée.
