# 04 — Gestion des dictionnaires et des langues

## Les dictionnaires ne sont pas le graphe

Un dictionnaire lexical associe `(namespace, KQ/KP, locale, domaine facultatif)` à un **libellé principal**, des variantes et éventuellement une définition. Un dictionnaire de correspondance (crosswalk) associe un **identifiant Kristal** à un **identifiant externe** avec une relation typée. Ces deux ensembles sont séparés : l'existence d'un label Wikidata ne prouve pas une correspondance exacte et inversement.

## Sources et couches

| Couche | Entrée | Règle de gestion |
|---|---|---|
| `wikidata` | JSON/JSONL extrait d'un snapshot Wikidata sur `exactMatch` validé | Immuable par snapshot, avec référence Q/P et langues |
| `external` | Terminologie externe avec preuve d'alignement et licence | Admission contrôlée, source et preuve obligatoires |
| `curated` | Traduction, correction ou terme préféré local validé | Nouvelle révision, nom du réviseur et justification |

Le **catalogue** déclare explicitement les langues, leur repli et les couches ordonnées avec `layer_id`, `kind`, `priority`, `path` et `sha256`. Pour les couches externes, il déclare `source_system`, `source_snapshot`, `license`. Pour Wikidata, `source_snapshot`. Aucune couche non déclarée ne prend priorité par simple présence sur disque.

## 300 langues ou davantage

- Les langues sont des **étiquettes BCP 47**, par ex. `fr`, `en`, `fr-CA`, `zh-Hant`, `ar`, `sr-Latn`. Le Framework draft.3 en valide la **syntaxe** ; diK devra compléter par IANA/CLDR (validité, alias et canonicalisation).
- Une langue déclarée peut avoir **zéro entrée**. Ne pas générer de fichiers vides contenant une entrée fictive pour chaque KQ.
- La couverture sera souvent inégale : un dictionnaire contient seulement les référents effectivement disponibles pour cette langue.
- L'interface gère Unicode, les écritures droite-à-gauche et les directions de texte (aucune translittération forcée). Les mêmes lettres peuvent désigner plusieurs KQ.
- Une variante comme `fr-CA` ne récupère `fr` que si **fallback explicitement déclaré** et sans boucle. L'utilisation de ce mot est catégorisée `fallback` et non `direct`.

## Résolution des libellés : contrat comportemental

1. Confirmer namespace, identité et genre attendu (`KQ` ou `KP`).
2. Chercher une entrée directe dans la locale sélectionnée, en tenant compte du domaine documenté.
3. Composer les couches du catalogue par priorité déclarée, puis décision éditoriale auditée ; la sémantique exacte de tri doit être stabilisée par tests contre le Framework.
4. Si les meilleures couches **à priorité égale** se contredisent, retourner `conflicted`, jamais trancher au hasard.
5. Si direct absent, essayer **uniquement** la chaîne de replis du catalogue, en identifiant langue source et chemin de repli ; ne pas marquer direct.
6. Si rien, retourner `missing` + `semantic_id` visible pour diagnostic, sans inventer de traduction.

Les synonymes peuvent être indexés pour la recherche et les propositions de conversion ; ce ne sont pas automatiquement des préférences d'affichage. L'égalité de termes de deux KQ n'est pas une collision d'identité. Une contradiction de préférences sur le **même KQ** et au même niveau est un conflit à résoudre.

## Enrichissement et révision

- L'édition crée une **nouvelle couche `curated`** qui ne modifie pas l'import.
- Chaque correction comporte un identifiant de décision, son réviseur, sa justification et une nouvelle empreinte.
- Les traductions assistées par modèle demeurent `proposed`/non certifiées tant qu'elles ne sont pas validées.
- Publier simultanément les nouveaux fichiers + le catalogue correspondant, idéalement par écriture atomique/renommage du snapshot complet.

## Mesures qualité distinctes

DiK devrait mesurer séparément la **présence du libellé**, celle d'une **définition**, la couverture des **alias**, la révision humaine et le droit d'utilisation. Un libellé présent n'est pas une preuve de bonne traduction. La mesure canonique v11 draft.3 porte sur la présence/usable du libellé KQ/KP ; les autres mesures sont des indicateurs proposés pour de futures versions.
