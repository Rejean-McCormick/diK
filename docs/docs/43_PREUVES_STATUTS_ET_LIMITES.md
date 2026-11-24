# 43 — Preuves, états, rapport et vocabulaire normalisé

## 1. Règle générale

**Un état est toujours relatif à une source, une identité, une locale, une version et une date.** Éviter les affirmations globales du type « l'anglais manque dans le Kristal ». Privilégier « aucune forme anglaise vérifiable n'a été résolue avec les sources activées au scan X ».

## 2. Deux axes de statut : source et cellule

### Source (découverte et admission)

`declared` → `found` → `fingerprinted` → `parsed` → `aligned` → `eligible` → `active` ; états latéraux `rejected`, `unsupported`, `ambiguous`, `stale`, `license_unverified`. Cette liste est un **contrat proposé pour un futur registre diK**, pas une énumération codée dans V3.

### Cellule (résolution)

- `direct` : forme de locale demandée dans un catalogue actif et validé.
- `external_observed` : label dans source externe prouvée, mais non publié comme couche.
- `gf_realized` : forme grammaticale issue d'une liaison KQ/P↔GF **révisée et testée** (état cible non encore prouvé).
- `fallback` : forme d'une autre locale explicitement autorisée ; mentionner la locale effective.
- `candidate_only` : correspondance sémantique ou ressource non approuvée ; **pas une forme de production**.
- `not_configured` : la locale n'est pas activée dans les sources concernées.
- `source_unavailable` : chemin, dump ou format inaccessible.
- `alignment_unproven` : fichier lu mais clé sémantique non établie.
- `conflict` : plusieurs preuves incompatibles sans arbitrage.
- `unresolved_after_active_sources` : aucune forme utilisable après interrogation du périmètre déclaré.
- `not_evaluable` : pas d'ensemble canon v11 permettant de définir proprement le dénominateur.

**Ne pas mapper mécaniquement** tous ces états sur `missing` ou `translation_missing`. Dans V3, `catalogue_courant`, `catalogue_raccorde`, `wikidata_observe`, `conflit`, `non_resolu` et `non_evaluable` sont les statuts effectivement publiés.

## 3. Preuves requises selon l'usage

| Conclusion souhaitée | Preuves minimales | Ce qui ne suffit pas |
|---|---|---|
| Source sur disque | `exists`, type, chemin racine | Mention dans un index ancien |
| Fichier inchangé | SHA-256 vérifié | Même taille ou même nom |
| Authentique / utilisable | Origine indépendante, licence, version | Hash local seul |
| KQ/P ↔ Q/P exact | Crosswalk accepted+preuve, namespace stable | `Q123` ~ `KQ123`, même libellé |
| Forme Q/P en langue | Dump/snapshot valide + Q/P accepté + label locale | Présence d'une URI Q |
| Flexion GF sûre | Mapping KQ↔GF revu, fonction/catégorie et exécution/langue qualifiée | `DictFre.gf` existe |
| Couverture complète des 14 | 14 cellules vérifiées pour chaque identité évaluable + état des exclus | Un seul mot français ou un fallback |

## 4. Signature reproductible d'un scan (cible)

Un manifeste d'exécution devrait fixer : `portfolio_root`, liste et SHA des manifestes de découverte, révision choisie de chaque Kristal, graph/registry/catalog/crosswalk digests, liste des 14 locales, sources activées et leurs digests, version du moteur diK, version des validateurs Framework, règles de repli, mode sans réseau, date UTC, et limitations.

Ne pas inclure les dumps ou les données tierces brutes dans le ZIP de résultats sauf autorisation expresse. Les rapporteurs doivent citer les preuves qui permettent de retrouver une donnée sans déplacer sa source.

## 5. Table d'interprétation du rapport V3 daté

| Valeur observée | Ce qu'on peut dire | Ce qu'on ne peut pas dire |
|---|---|---|
| 126 officiels | 126 dossiers conformes au filtre à cette date | 1 153 Kristals officiels |
| 57 évalués | 57 ensembles ont une révision v11 auditée | Tous les 126 ont 14 langues prouvées |
| 69 non évaluables | 69 nécessitent autre structure/révision ou diagnostic | Ils n'ont aucun mot |
| 1 776 liens Q/P acceptés | Certaines identités ont un crosswalk accepté | Toutes ces identités ont 14 labels disponibles |
| 0 labels Q/P observés | Aucun dump Q/P fourni au scan | Wikidata n'existe pas localement |
| 0 candidats GF reconnus | Le scanner n'a pas reconnu de handoff compatible | Aucune ressource GF n'existe sur le PC |
| 283 176 non résolus | V3 n'a pu rattacher une forme à ces cellules | 283 176 traductions doivent être faites |

## 6. Formulation recommandée dans l'interface

Préférer : « **ID résolu en `fr` depuis le catalogue X, révision Y** » ou « **ID non résolu en `de` : aucune source active vérifiée ne le couvre dans ce scan** ». Ne pas écrire « traduit », « traduction à produire », « langue inexistante » ou « dossier historique = nouveau Kristal ».

## États effectivement implémentés dans le localisateur V4

Le registre de ressources implémenté utilise `fingerprinted`, `found_unhashed`, `unreadable`, ainsi que `allowed_for_resolution=false`. Ce dernier champ marque **la découverte**, et ne change pas implicitement quand un catalogue v11 passe ultérieurement un audit indépendant. Les statuts `parsed`, `eligible`, `active`, `gf_realized` sont des objectifs d'architecture et **non** des états de sortie du localisateur actuel. Voir [44](44_SOURCE_MANAGER_V4_IMPLEMENTATION.md).


## Précision V5.3 : aucun Q/P détecté ≠ aucune intersection possible

Le bilan V5.2 a lu 333 849 lignes de 37 sources thématiques sans reconnaître de Q/P. Les 35 sorties `no_accepted_qp_overlap` ne constituent **pas** une preuve d'absence exhaustive si le schéma des enregistrements est inconnu ou si des lignes sont exclues. La nomenclature cible doit séparer `schema_unknown`, `schema_verified_no_qp_extracted`, `partial_budget`, `complete_no_accepted_qp_overlap`, `candidate_labels_observed`, `eligible_not_active`. **Ce sont des statuts proposés pour V5.3, non des sorties actuelles du logiciel.** Voir [58](58_STATUTS_ET_RAPPORTS_V5_3.md).
