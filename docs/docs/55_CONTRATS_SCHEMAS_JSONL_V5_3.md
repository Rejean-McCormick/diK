# 55 — Registre de schémas et adaptateurs JSONL (contrat cible V5.3)

> **Mise à jour du 23 novembre 2026 :** les composants dont les formats sont prouvés sont implémentés dans **alpha.11**. Lire le [chapitre 61 — état réellement livré](61_IMPLEMENTATION_EFFECTIVE_V5_3.md). Les parties visant des schémas locaux encore inconnus demeurent des spécifications, non des fonctionnalités certifiées.

**Document de conception, pas un schéma déjà supporté par diK.** Les exemples sont fictifs lorsqu'ils ne viennent pas explicitement du fichier QID fourni. Ne jamais utiliser les exemples comme dictionnaire de production.

## 1. Une famille de données ≠ un adaptateur universel

Le champ de classification `wikidata_thematic_candidate` de V5.2 est une **classe d'inventaire**, non une preuve que les JSONL portent tous `qid` et `labels`. Un adaptateur V5.3 doit être sélectionné à partir d'un **profil de schéma vérifié sur le contenu**, avec `family`, `schema_version`, `root_shape`, `id_fields`, `roles`, `label_fields`, `locale_encoding`, et `evidence`. Un suffixe `.jsonl`, le mot `wikidata` dans le chemin ou la présence de `Q123` dans du texte brut ne suffisent pas.

## 2. Familles prévues, état des preuves

| Famille | Exemple de chemin | Preuve actuelle | Adaptateur proposé |
|---|---|---|---|
| `qid_keyed_labels` | `gf-wikidata-tools/extraction/data/qid-lexicon.jsonl` | 50 enregistrements transmis avec `Q...` clé d'un objet de locales | **Connu** : mapping Q/P → locale exacte → chaîne |
| `id_labels` | JSONL avec `qid`/`id` et `labels` | Déjà pris en charge par V5.1/V5.2, pas certifié pour les 40 thématiques | **Conditionnel** : format validé par profil |
| `identity_candidates` | `Kristal/locals/.../identity-candidates.jsonl` | Nom et lignes analysées seulement ; contenu réel absent du bilan | **À découvrir** : rôles et statut du candidat, sans promotion |
| `wikidata_statements` | `Kristal/locals/.../statements.jsonl` | Nom et lignes analysées seulement ; contenu réel absent du bilan | **À découvrir** : sujet/prédicat/objet typés, pas un lexique implicite |
| `gf_wikidata_topic` | `City`, `Country`, `University`, `Part_of world` | Chemins, tailles, lignes parcourues ; schéma non fourni | **À découvrir** : champs d'identité, formes, langue, droits |
| `wikidata_lexeme` | Wikidata L/S/F | Aucune preuve d'alignement dans ce bilan | **Autre adaptateur** ; pas assimilé à Q/P |

## 3. Extraction d'identifiants par rôle

Chaque extraction doit produire `identifier` (forme stricte `Q[1-9][0-9]*` ou `P[1-9][0-9]*`), `role` (`entity_subject`, `property_predicate`, `entity_object`, `lexical_entity`, `crosswalk_candidate`…), `field_path`, `schema_id`, `record_location`. Un ID trouvé comme *objet d'une assertion* ne doit **pas** être utilisé comme identité lexicale de la ligne sans règle expresse. Les chaînes `L...`, `S...`, `F...` restent de type distinct. La *normalisation* ne doit pas transformer `Q00012` en `Q12` de manière silencieuse : rejeter les valeurs non conformes et consigner le cas.

Exemples conceptuels de chemins d'extraction : `$.qid`, `$.id`, `$.entity.id`, `$.subject.id` ou clé externe de l'objet `$.Q...` ; leur usage n'est autorisé **que si le schéma correspondant l'établit**. Ne jamais chercher récursivement des QID partout dans le JSON pour déclarer une correspondance.

## 4. Extraction de formes linguistiques

Accepter exclusivement une forme lexicalement explicite, sous un champ dont le rôle de libellé est attesté par le profil : dictionnaire de locales, tableau `labels[]` avec `language`/`value`, ou structure propre au dataset **après inspection des exemples réels**. Conserver `locale_originale`, `locale_cible`, `champ`, `valeur_source`, `type` (`label`, `alias`, `description`, `lemma`, `form`), et la version du schéma. Pour la couverture des 14 langues, **seuls les `label` autorisés dans la locale exacte** peuvent entrer dans les cellules ; alias/descriptions/lemmes ne sont pas des labels par défaut.

Ne jamais :

- deviner une langue par la graphie ou le texte ;
- traduire ou translittérer une forme ;
- choisir la première entrée d'un tableau en cas d'ambiguïté ;
- combler `no` avec `nb` ou `nn` ;
- convertir une valeur `statements` ou une fonction GF en forme publiable sans contrat distinct.

## 5. Profilage prudent et statut de sortie

1. Vérifier pointeur SHA/taille/racine.
2. Lire un échantillon borné et diversifié en conservant la position des enregistrements (début + fenêtres déterministes pour gros fichiers) ; l'échantillon ne prouve **jamais** l'absence d'un schéma ailleurs.
3. Générer un profil avec catégories de champs, types JSON, fréquence, taux de conformité et exemples **expurgés**.
4. Sélectionner un adaptateur uniquement si les critères d'identification sont suffisants et documentés ; sinon `schema_unknown` ou `schema_ambiguous`.
5. Parcourir ensuite **tous** les enregistrements avec le même adaptateur ou produire explicitement `incomplete`.
6. Conserver les erreurs de lignes, leur position et le motif sans abandonner silencieusement la source.

**Sorties** : `schema_profile.json` par source, `schema_registry.json` global avec version des adaptateurs et empreintes, compteurs distincts `rows_valid_json`, `rows_matching_schema`, `rows_with_qp`, `rows_with_label`, `rows_matching_accepted_qp`. Les noms des futurs fichiers et champs sont proposés, pas encore des sorties de V5.2.

## 6. Exemples et garde-fous

Voir [`docs/examples/wikidata-v5_3/README.md`](../examples/wikidata-v5_3/README.md) pour des lignes de test illustratives et leurs résultats attendus. **Les véritables schémas des 40 sources restent à qualifier sur le poste Windows** ; le futur développement doit obtenir des échantillons anonymisés ou effectuer un profilage local avant de figer le contrat.

**Critère de fin de lot :** les 35 sources V5.2 ne peuvent plus sortir `no_accepted_qp_overlap` si aucune identité Q/P n'a été extraite ; `schema_unknown` ou `no_qp_extracted` doit prévaloir, et toute conclusion « aucun Q/P commun » exige un parcours intégral valide.
