# 07 — Conversion contrôlée des anciens Kristals

## Règle fondamentale

**On ne remplace jamais « tous les mots » dans un Kristal.** On remplace, dans une **nouvelle révision**, seulement les valeurs dont le schéma et le contexte indiquent qu'elles jouent **le rôle d'identifiant conceptuel ou de propriété**. Les citations, les textes doctrinaux et les valeurs littérales restent du texte.

## Pipeline

### A — Inventorier

Lire le format historique exact, identifier les chemins d'identité (sujet, prédicat, objet-référent, qualifiers…) et séparer les chemins de texte documentaire. Produire l'identifiant de l'artefact source, son digest SHA-256, sa version déclarée et son namespace. Un adaptateur de schéma explicite est requis par format ancien.

### B — Résoudre et proposer

Ordre des candidats : (1) ancien ID directement relié à KQ/KP et validé ; (2) registre local ; (3) Q/P externe déjà relié par `accepted + exactMatch` ; (4) recherche lexicale inverse avec langue, type attendu, domaine, voisins et provenance. Les mots identiques peuvent pointer sur des référents différents. Conserver la liste des candidats et raisons du classement.

### C — Réviser

Chaque proposition est revue indépendamment. Possibilités : accepter l'identifiant, le refuser, déclarer ambigu, demander création d'un KQ/KP, ou conserver le champ non résolu. L'acceptation d'une suggestion lexicale demande une preuve sémantique appropriée ; le score IA n'a jamais valeur d'autorisation.

### D — Exporter un plan

Le plan Framework `kristal_dik_conversion_plan` liste `plan_id`, `source` (artefact, sha256, version), `catalog_id`, `crosswalk_id` et des `operations` comprenant `source_path` (JSON Pointer), `original_value`, `semantic_role`, `target_id` et `decision`. Chaque opération cible explicitement un rôle d'identité.

### E — Appliquer (future intégration Authoring Kit)

diK **n'exécute pas** de migration dans la v0.1 fonctionnelle envisagée. Un producteur autorisé doit revérifier la source, le hash, les rôles des chemins, le namespace, le registre, les décisions approuvées, les preuves, et produire un nouvel artefact. Le processus doit être transactionnel et annuler toute sortie partielle en cas d'échec.

### F — Prouver le résultat

Conserver l'ancien fichier **octet pour octet**, l'ancien engagement v9, les correspondances avant/après, les contrôles v11, les rapports d'ID non résolus, le journal de décision et l'information nécessaire à un retour (sans altérer l'historique).

## Statuts d'une opération

- `pending` : proposition, interdiction d'exécution.
- `approved` : décision enregistrée ; elle reste sujette aux validations du producteur.
- `rejected` : doit rester exclue de toute application.

Même un plan dont chaque opération semble approuvée n'est **pas une commande d'exécution**. Son schéma garantit des types et des champs, pas la qualité sémantique de chaque correspondance.

## Exemple

Ancien graphe simplifié :

```json
{"subject":"Augustin d'Hippone","predicate":"parle_de","object":{"kind":"entity","id":"grâce"},"citation":"Le mot grâce apparaît ici comme citation."}
```

Un plan peut proposer `/subject → KQ1001`, `/predicate → KP2001`, `/object/id → KQ1002`. Ce sont des **candidats** dépendants d'un contexte et d'une décision. Le champ `/citation` **ne doit pas** être réécrit, même s'il contient le même mot. Ces chemins correspondent à un exemple présent dans les artefacts Framework.

## Cas bloquants

- Ambiguïté de sens, proposition de propriété à un emplacement d'entité, ou namespace absent.
- Source modifiée depuis la préparation du plan ; digest différent.
- Correspondance fondée seulement sur `closeMatch` ou sur la traduction d'un libellé.
- Une opération vise une citation ou une valeur littérale.
- Ancienne source engagée qui serait modifiée in situ.
- Décision absente, refusée ou explicitement supersédée.

Le résultat en cas d'échec est un **rapport**, jamais une migration partielle présentée comme complète.
