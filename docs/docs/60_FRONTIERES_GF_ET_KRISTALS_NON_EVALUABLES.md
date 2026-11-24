# 60 — Frontières : GF, Wikidata L/S/F et 69 Kristals non évaluables

> **Mise à jour du 23 novembre 2026 :** les composants dont les formats sont prouvés sont implémentés dans **alpha.11**. Lire le [chapitre 61 — état réellement livré](61_IMPLEMENTATION_EFFECTIVE_V5_3.md). Les parties visant des schémas locaux encore inconnus demeurent des spécifications, non des fonctionnalités certifiées.

**Note de périmètre documentaire V5.3 (non implémentée).** Le futur lecteur thématique Wikidata n'est **pas** un moteur universel de morphologie GF et ne convertit pas les Kristals historiques en v11.

## GF : forme grammaticale ≠ identité sémantique

Les sources déjà localisées incluent `GF_Lexicons_Archive`, `gf-rgl`, `GF_Wordbench`, `gf-core`, `gf-wikidata_repos_source` et divers PGF. Les grands fichiers `.gf` sont des lexiques/grammaires, pas des catalogues canoniques KQ/KP par défaut. Un raccordement GF nécessitera au minimum :

- une entrée GF, une catégorie et un paradigme identifiés et vérifiés ;
- une correspondance approuvée pour `(namespace_id,KQ/KP)`, indépendante de la ressemblance des mots ;
- une locale, un mode de réalisation et un résultat linguistique testés ;
- une provenance, licence et politique d'activation vérifiables ;
- un statut distinct de `label` Wikidata, avec trace de chaque forme produite.

En attendant, le Source Manager peut **référencer** les fichiers GF, mais le compositeur lexical ne doit pas les considérer implicitement comme des couches actives.

## Wikidata L/S/F : objets distincts de Q/P

Wikidata `Q...` et `P...` représentent items/propriétés ; `L...` un lexème, `L...-S...` un sens, `L...-F...` une forme. Une extraction de labels Q/P ne suffit pas à constituer un alignement vers un lexème ou une flexion. Ces liens requièrent leur propre schéma, leurs preuves et leurs tests. Aucun ID Wikidata L/S/F ne devient automatiquement KQ/KP.

## Les 69 Kristals hors audit v11

Le portefeuille officiel a 126 dossiers, mais les scans V3–V5.2 n'en évaluent que 57 en v11. Les 69 restants ne doivent pas être considérés comme sans vocabulaire ; il manque un jeu canonique v11 exploitable **dans le périmètre et les critères actuels du scanner**. Leur diagnostic/compatibilité peut être prévu dans un lot ultérieur, sans fusionner les archives, sans convertir un vocabulaire en graphe canonique et sans réécrire les sources.

## Sequencement recommandé

1. V5.3 : inspecter **correctement** les JSONL Wikidata thématiques et les liens Q/P acceptés, sans activation.
2. Après V5.3 : valider sources/licences et règles de publication via une décision séparée.
3. Adapter GF et Wikidata L/S/F sous contrat typé, avec fixtures réelles et mappings approuvés.
4. Diagnostiquer et rendre éventuellement évaluables les 69 Kristals sans dégrader les 57 existants.
5. Relancer la couverture officielle des 14 langues après chaque activation **effective**, et distinguer formes candidates et publiées.
