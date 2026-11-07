# ADR proposée — DIK-LEX-1 v0.3 / Registre mondial et pipeline L/S/F

- **Date :** 2026-11-04
- **Statut :** PROPOSITION NON RATIFIÉE
- **Autorité actuelle :** Framework v11 draft.3 et SPEC_LOCK diK 1.0 candidate, inchangés.

## Décision proposée

1. Continuer de considérer diK comme agrégateur et arbitre lexical, **sans déplacer** l'autorité des identités canoniques KQ/KP hors du Framework.
2. Prendre ISO 639-3 comme **base de codes candidats**, IANA BCP 47 comme autorité de composantes des tags, avec CLDR et d'autres ressources à examiner comme couches futures.
3. Maintenir un index clairsemé d'emplacements candidats pour l'ensemble des codes disponibles, sans y fabriquer un dictionnaire vide ni un libellé automatique.
4. Importer séparément Wikidata `Q/P` (crosswalk accepté) et `L/S/F` (observations lexicales, non approuvées).
5. Produire vers GF/SemantiK un **handoff candidat** avec traits et formes non mappés; ne pas prétendre disposer de grammaires GF.
6. Tout texte externe exige une revue de licence propre à sa source, puis une revue de pertinence/conflit; aucune licence approuvée dans cette seed.
7. Les instantanés importés et les rapports portent des SHA-256; les sorties sont publiées dans des chemins nouveaux.
8. L'overlay est **additif** et laisse intacts `spec/diK-1.0`, les schémas Framework vendoriés et le modèle de crosswalk.

## Rejeté

- Remplacer KQ/KP par Q/P.
- Traiter 7 910 codes comme 7 910 dictionnaires, ou comme le nombre exhaustif des langues du monde.
- Inférer `exactMatch` d'une ressemblance orthographique.
- Étiqueter automatiquement des lexèmes Wikidata comme traductions vérifiées.
- Compiler automatiquement des paradigmes GF à partir de Q grammaticaux non mappés.

## Risques et validations nécessaires

Les tests du pipeline sont synthétiques, l'accès HTTPS réel n'a pas été exécuté ici, la validation BCP 47 est conservatrice, et aucun dump lexical industriel n'a été vérifié de bout en bout. Valider la licence, l'origine et les compatibilités d'un dépôt avant tout passage en production.
