# 37 — Connecteurs Wikidata, GF et catalogues consolidés

## 1. Pourquoi trois adaptateurs différents ?

**Wikidata Q/P** décrit des entités et propriétés externes. **Wikidata L/S/F** décrit des lexèmes, sens et formes. **GF** décrit des catégories, lexiques, paradigmes et la réalisation grammaticale. Aucun format n'est un remplacement universel des deux autres.

```text
(namespace,KQ/KP) --[exactMatch accepté + preuve]--> Wikidata Q/P
       |                                                |
       +-- catalogue v11 direct ----> (locale, libellé)  +-- snapshot Q/P, label(locale)
       |
       +-- [mapping grammatical revu] --> fonction GF / paradigme --> forme fléchie

Wikidata L/S/F --- observation(s), référence(s) ---> candidats GF/SemantiK
                    (jamais identité KQ/P imposée)
```

## 2. Adaptateur Q/P — exigences

- Entrées : `identity-registry.json`, `external-crosswalk.json`, snapshot Q/P local ou couches v11 importées, locales.
- Éligibilité : `exactMatch accepted` et preuve KS exigée par le contrat; namespace et famille concordants ; doublons/contradictions bloqués.
- Extraction : récupérer les libellés à partir de l'objet `Q/P` dans la locale demandée ; conserver l'ID externe, la révision du dump et le hash.
- Sortie : `wikidata_observe` tant que non publié comme couche auditable ; un label peut manquer dans une locale sans que le Q/P manque.
- Un `approved-sha256` obtenu indépendamment vérifie l'intégrité contre une empreinte attendue ; un hash calculé localement ne certifie pas l'origine.
- Un `qid-lexicon.jsonl` ou `City.jsonl` ne prouve pas un dump Q/P global ; détecter leur schéma et périmètre réel avant de les lire.

La V3 ne charge un dump Q/P que s'il est explicitement renseigné via `--wikidata-dump`. Le rapport `RESOLUTION_20261123T005959Z` indique `wikidata_dump_local.etat=non_fourni`, donc **0 label Q/P observé** dans ce scan. Ne pas conclure à zéro label disponible sur l'ordinateur.

## 3. Adaptateur L/S/F — exigences

L'import diK observé dans [28](28_WIKIDATA_LEXEMES_GF_PIPELINE.md) produit un snapshot `dik.wikidata-lexeme-observations/0.1-candidate`. Chaque `L...`, `L...-S...`, `L...-F...` reste une clé externe. Les champs de liaison à KQ et de fonction GF sont initialement `null`. La ressemblance d'une forme et d'un label KQ ne fait pas preuve.

Les tags de langue sont reconnus via une validation BCP 47/IANA lorsque configurée ; un alias `no` ne peut pas être considéré identique à `nn` sans une règle explicitement vérifiée. Les distinctions `no`, `nb`, `nn` doivent être conservées au moins dans les observations.

## 4. Adaptateur GF — exigences

GF n'est pas un dictionnaire de traduction KQ/KP. Ses fichiers `.gf` peuvent porter des noms de lexèmes, fonctions et réalisations linguistiques, sans contenir un `namespace_id` de Kristal. L'adaptateur devra fournir, **sous revue**, une table `semantic_key -> gf_abstract_function -> gf_concrete_module/locale -> category/paradigm` avec preuves.

| Dépôt | Fonction cible | Ce qui ne suffit pas |
|---|---|---|
| `GF_Lexicons_Archive` | Lexique et paradigmes de référence | Présence de `DictFre.gf` |
| `gf-rgl` | Ressource grammaticale et module de langue | Présence de `src/french/LexiconFre.gf` |
| `gf-core` / GF 3.12 | Compiler et moteur GF | Binaire installable, pas identité |
| `GF_Wordbench` | Valider des scénarios GF concrets | Un pilote réussi n'est pas un alignement KQ |
| `GF_Observatory` / `gf-audit` | Observabilité / diagnostics | Un log ou un test ne devient pas source lexicale |
| `ars-magna-defluens` / SemantiK | Propositions/qualification et réalisation | Un handoff `candidate` n'est pas un RuntimeSet approuvé |

La provenance doit porter le digest du module et la version GF ; l'activation nécessite une **décision de liaison** (sens/catégorie, locale, contraintes, licence). La compilation ne réconcilie pas automatiquement un homonyme.

## 5. Contrat diK ↔ SemantiK/GF déjà décrit

Le document [30](30_SEMANTIK_GF_HANDOFF_V09.md) décrit des artefacts de connaissances `use_for=knowledge`, `binding_kind=lexeme_ref`, `source_kind=wikidata` et un gabarit de revue ; **pas de règle morphologique activée**. Spek délègue le diagnostic des pilotes Fre à WordBench. Le propriétaire des décisions de réalisation est SemantiK Architect.

## 6. Ordre et conflits

Une couche actuelle v11 auditable a sa priorité déclarée ; un Q/P accepté ne déplace pas silencieusement cette priorité ; un candidat GF n'impose pas une expression préférée. Deux sources compatibles contradictoires restent explicites (`conflit` ou alerte de divergence) jusqu'à revue. Le graphe canonique ne change jamais du fait d'une nouvelle étiquette.

## 7. Matrice de tests d'adaptateurs (cible)

| Cas | Résultat attendu |
|---|---|
| Q/P accepté + dump contenant le label de locale | Forme observée et sourcée, **pas** automatiquement publiée |
| Q/P seulement candidat | Pas de forme promotionnelle |
| Q/P contradictoire entre snapshots | Conflit et refus de priorité implicite |
| L/S/F sans mapping Q/P/KQ | Observation externe uniquement |
| `.gf` sans fonction et catégorie revues | Ressource découverte, pas forme KQ résolue |
| Module GF validé mais langue non qualifiée | Refus de cette locale |
| `nn` disponible, `no` demandé sans règle | Aucun substitut implicite |
| Valeurs absentes | Statut relatif au périmètre des sources, pas « mot à traduire » |

Voir [41](41_FEUILLE_DE_ROUTE_LOCALISATION_ET_TESTS.md) pour l'ordre de développement.

## Actualisation V4 : limites des adaptateurs

`resolve14 --resource-registry` sélectionne les catalogues v11 enregistrés, **pas** les lexiques GF comme couches actives. `--wikidata-source-id` permet de désigner explicitement un candidat de dump Q/P découvert et dont l'empreinte locale est contrôlée ; il ne transforme ni `qid-lexicon.jsonl` en dump global, ni L/S/F en labels Q/P, ni GF en KQ. Il n'y a pas de génération de flexions GF dans alpha.8. Voir [44](44_SOURCE_MANAGER_V4_IMPLEMENTATION.md).
