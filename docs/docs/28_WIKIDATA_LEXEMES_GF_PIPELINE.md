# 28 — DIK-LEX-1 : lexèmes Wikidata (L/S/F) et interface candidate vers GF / SemantiK

**État** : implémentation candidate de *projection d'observations*; pas un importateur de dictionnaires `curated` et pas un compilateur GF.

## Frontières qui ne doivent jamais fusionner

| Système | Unité | Statut dans ce pipeline |
|---|---|---|
| Kristal Framework | `(namespace,KQ/KP)` | Identité canonique inchangée |
| Wikidata Items / Properties | `Q123`, `P456` | IDs externes ; alignement seulement par crosswalk revu |
| Wikidata lexicographique | `L123`, `L123-S1`, `L123-F1` | Observations externes conservées |
| Wikidata grammatical | `Q...` dans `grammaticalFeatures` | **Traits candidats non résolus** |
| SemantiK / GF | Fonctions, catégories, paradigmes | **Aucun généré** ; handoff à mapper |

Wikidata distingue le lexème, les **sens** et les **formes** : <https://www.wikidata.org/wiki/Wikidata:Lexicographical_data/Documentation>. Ces classes ne doivent pas être résumées à une table `mot -> traduction`. La licence des données structurées Wikidata est indiquée comme CC0 par la politique officielle : <https://www.wikidata.org/wiki/Wikidata:Licensing>. Les textes tiers et références externes conservent leurs propres droits.

## Import local et vérification

Le parseur prend des entités JSONL (une par ligne), des dumps au format tableau avec `[` et `]` sur leurs propres lignes, et des fichiers `.gz` ou `.bz2`. Il sélectionne les entités `L`, **sans tenter d'utiliser les Q/P du dump comme dictionnaire**. Les limites `--max-records` et `--max-line-bytes` entraînent un refus complet du snapshot si dépassées, jamais un état de demi-import déclaré complet.

```sh
dik world lexemes-import \
  --dump data/wikidata/latest-lexemes.json.bz2 \
  --snapshot wikidata-lexemes-2026-11 \
  --registry data/iana/language-subtag-registry-2026.txt \
  --output-dir data/lexemes/2026-11 \
  --max-records 5000000

dik world lexemes-audit --dir data/lexemes/2026-11
```

On peut également fournir `--expected-sha256` contrôlé indépendamment. Sans source IANA, `iana_valid` vaut `null` et chaque tag est explicitement `iana_not_checked`. Sans SHA attendu, l'empreinte locale ne constitue **pas** une attestation de provenance du serveur.

La sortie immuable contient :

- `lexemes.jsonl` : identifiants externes, `lemmas`, `forms`/`grammatical_features`, `senses`/`glosses` ; `kristal_identity=null`, `gf_mapping_status=unmapped`, `translation_status=not_reviewed`.
- `locale-stats.json` : comptage observé, pas couverture vérifiée.
- `manifest.json` : SHA source + sortie + statistiques, 0 dictionnaire publié et 0 crosswalk Kristal approuvé.

**Projection volontairement partielle :** les `claims`, `qualifiers`, `references`, les annotations internes des statements et les références GF ne sont **pas** transférés. L'original est indispensable si l'on veut une copie complète/fidèle du dump. L'outil ne complète aucune traduction et ne résout aucune homonymie.

## Handoff GF/SemantiK

```sh
dik world gf-handoff \
  --observations data/lexemes/2026-11 \
  --locale fr \
  --output-dir data/gf-candidates/fr-2026-11

dik world gf-audit --dir data/gf-candidates/fr-2026-11
```

Le handoff contient seulement les lemmes / formes observés pour la locale demandée, les catégories et traits Q *externes*. Les champs `gf_function`, `gf_category` et `gf_paradigm` sont `null` : aucune règle GF ne peut être inventée à partir de la simple présence de la forme.

Un futur adaptateur revu devra fournir explicitement la table `Wikidata grammaticalFeatures Q -> catégories/traits GF`, les fonctions/paradigmes GF et les correspondances Kristal validées, avec preuves par langue, domaine et révision.

## Démonstration sans réseau

```sh
dik world lexemes-import \
  --dump examples/world-dictionaries/wikidata-lexeme-sample.jsonl \
  --snapshot demo-lsf \
  --registry examples/world-dictionaries/iana-fixtures/synthetic-language-subtag-registry.txt \
  --output-dir /tmp/dik-demo-lsf

dik world gf-handoff \
  --observations /tmp/dik-demo-lsf \
  --locale fr \
  --output-dir /tmp/dik-demo-gf-fr
```

Les exemples sont **fictifs**, destinés aux tests de structure, et n'attestent aucune donnée Wikidata en direct.

## Limites de qualification

- Testé sur fixtures, pas sur le dump lexical complet ni sur 300 langues avec données linguistiques réelles.
- Pas de reprise par checkpoint pour le nouveau parseur L/S/F; une erreur annule la sortie et demande une nouvelle exécution.
- Pas de source Wiktionary/Apertium/UniMorph importée. Les données externes doivent faire l'objet d'un examen séparé des licences.
- Pas d'écriture dans le Framework v11 ou dans le catalogue `curated`.
