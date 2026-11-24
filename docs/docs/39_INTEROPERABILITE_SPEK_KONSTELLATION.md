# 39 — diK, Spek, Konstellation, SemantiK et GF : frontières concrètes

## 1. Spek : carte et consommation lexicale, pas autorité d'alignement

La carte `Spek/docs/CARTE_REPOS_ET_CHEMINS.md` du snapshot du 22 novembre cite des chemins GF, SemantiK, WordBench et diK. Elle explicite `use_for=knowledge` pour le handoff lexical et indique que **WordBench** se charge des précontrôles et compilations GF, tandis que **SemantiK Architect** décide de l'opération et de la réalisation. Spek précise que la similarité d'un mot ne fonde aucune identité lexicale approuvée.

Le script `scripts/piloter_agriculture_registres.py` est un contrôleur orienté registres d'agriculture et un diagnostic WordBench ; **ce n'est pas** l'inventaire mondial des ressources diK. Son chemin de source Agriculture v8 ne prouve pas une révision v11 complète.

## 2. Konstellation : lecteur de jeux v11 explicitement configurés

Le snapshot Konstellation contient `config/v11-reader.local.example.json` : racines Framework et Integration Pack, une allowlist de principaux, `datasets[]`, et pour chaque dataset `registry`, `graph`, `crosswalk`, `catalog`, `locales`. L'exemple vise des fichiers de démonstration, **pas** tous les Kristals ni un registre de sources mondiales.

Le lecteur `server/integrations/kristal-v11.mjs` :
- impose un profil `local-only`, refuse le partage public/LAN,
- exige des chemins absolus de fichiers d'entrée et des limites de taille,
- vérifie les empreintes du script d'intégration et du Framework épinglé,
- délègue la validation et la vue lexicalisée au Framework et à l'Integration Pack,
- ne confère **aucun droit de publication** à un jeu de données local.

**Attention :** l'exemple de Konstellation montre un pin Framework `11.0.0-draft.4`, tandis que le snapshot diK décrit un contrat `11.0.0-draft.3`. Ce décalage de version doit être testé contre l'installation locale ; ne pas proclamer une compatibilité automatique des couches.

## 3. RACI minimal cible

| Fonction | Autorité primaire | Consommateurs ou contrôles |
|---|---|---|
| Identités et schémas v11 | Kristal Framework / producteurs autorisés | diK, Kristal Manager, Integration Pack |
| Découverte, registres lexicaux, crosswalk, qualité de source | diK (sous contrat Framework) | Spek, Konstellation |
| Réalisation linguistique et choix grammatical | SemantiK Architect | GF WordBench, GF Core, RGL |
| Test/compilation GF | GF WordBench avec GF Core/RGL | diK reçoit seulement preuves qualifiées |
| Diagnostics et statut GF | GF Observatory et audits | WordBench, SemantiK |
| Composition de contenus | Spek | Lectures diK approuvées, sans promotion d'identités |
| Consultation graphique de vues v11 | Konstellation | Integration Pack, Framework, diK pour les formes admises |

## 4. Contrat d'échange cible diK → consommateur

Un résultat stable doit inclure : `semantic_key`, `requested_locale`, `resolved_locale`, `label`, `status`, `source_id`, `snapshot_sha256`, `crosswalk_decision_id` si pertinent, `confidence_policy` et `publication_authorized` **explicite**. Le JSON dans `docs/examples/resource-locator/` est un exemple documentaire, pas une API déjà stable.

Le consommateur ne doit jamais recevoir un mot isolé présenté comme identité canonique. Il ne modifie ni les registres KQ/KP ni le statut de crosswalk.

## 5. Interop : tests à réaliser

1. `registry/graph/crosswalk/catalog` v11 identiques ou clairement référencés par revision dans diK et Konstellation.
2. Réévaluer le pin draft.3/draft.4 et le schéma avant activation.
3. Une source GF trouvée n'est pas importée dans Konstellation par le simple fait que WordBench la compile.
4. Une identité `candidate` reste un candidat dans Spek et dans Konstellation.
5. Un fallback est marqué comme tel et porte la locale réellement affichée.
6. Une source non autorisée/licence non qualifiée n'est pas exposée dans des sorties publiques.

Voir [37](37_CONNECTEURS_WIKIDATA_GF.md), [40](40_SECURITE_DROITS_PROVENANCE.md).
