# 19 — Langues, scripts, variantes et registres

## LEX-020 — Normalisation

Utiliser une bibliothèque/registre BCP 47 approprié, versionné et documenté : validité de la langue, canonicalisation (alias/variante/script/région) et tag source conservé à des fins d'audit. Une simple regex `fr-CA` ne prouve pas une langue valide. Choisir une seule politique d'égalité de tags et la tester sur `fr`, `fr-CA`, `zh-Hans`, `zh-Hant`, `sr-Latn`, `ar` et tags inattendus.

## LEX-021 — Fallback

Chaque repli est un arc déclaré dans le catalogue. `fr-CA -> fr` n'autorise pas `fr -> en` sans déclaration ; interdire cycles et ambiguïtés de priorité. Un libellé en langue de repli ne compte pas comme `direct`. Ne pas supposer que `zh-Hant` et `zh-Hans` sont interchangeables, ni qu'une translittération constitue une traduction.

## LEX-022 — Unicode et rendu

Conserver Unicode d'origine, normaliser pour **comparaison** par NFC si nécessaire, mais ne pas perdre les distinctions significatives ; sécuriser rendus HTML/Markdown ; RTL et scripts combinants testés ; normalisation ne sert jamais à fusionner des concepts. Les formes fléchies, sens lexicographiques et lemmes Wikidata L sont hors import Q/P par défaut.

## LEX-023 — 300+ langues

Les langues sont déclarées même avec zéro entrée ; couverture sparse évaluée avec `missing`. Le catalogue doit permettre shards compressés et nombreux locales sans charger l'ensemble pour résoudre une locale. TCK inclut **301 langues déclarées** et plusieurs scripts, avec fallback vérifié.

## LEX-024 — Préférence contextuelle

Terme de spécialité (théologie, physique) peut l'emporter sur le dictionnaire général par profil de domaine/version, jamais sur la seule orthographe ; termes homographes distincts peuvent référer à plusieurs KQ. Une interface affiche la provenance et la langue effective du terme rendu.
