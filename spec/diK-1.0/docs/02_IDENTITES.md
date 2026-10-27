# 02 — Identités sémantiques et registre

## ID-001 — Clé canonique

La seule clé référentielle d'un KQ/KP est `(namespace_id, id)`. `KQ1001` dans `alpha` et `KQ1001` dans `beta` **ne sont pas interchangeables**. Toutes les API/domain objects portent le namespace ; l'affichage abrégé de `KQ1001` n'autorise pas sa résolution hors contexte.

## ID-002 — Types stricts

`KQ…` = entity; `KP…` = property; `KA…` = assertion; `KS…` = source. Le parser rejette `Q8018`, `P31`, `wikidata:Q8018`, `has_property`, `urn:legacy:…` **dans un rôle d'ID canonique**. Il peut les reconnaître dans des *champs externes* typés, des demandes de migration ou une valeur littérale.

## ID-003 — Allocation

- Allocation durable et non réutilisable au sein du namespace, y compris après suppression logique.
- Avant l'émission : chercher identités internes existantes ; consulter miroir externe **si disponible**, sans rendre Wikidata indispensable à l'émission locale.
- Retourner l'identifiant alloué + séquence/transaction d'émission + portée. Échec atomique en cas de compétition ; aucun recyclage sur rollback après émission publiée.
- Ne pas déduire le numéro du KQ du numéro Q externe ; ne pas précréer des Q Wikidata « en réserve ».
- **diK ne devient pas autorité d'allocation** : il demande un mint au registre/producteur désigné, ou propose des identités candidates via un canal séparé.

## ID-004 — Statuts, fusion, scission

Une erreur d'identité se corrige par des déclarations de remplacement/supersession versionnées et une décision auditée, pas en remplaçant la clé de l'histoire. Les fusions/splits Wikidata ne fusionnent pas les KQ de Kristal. La dépendance à Wikidata est la table de correspondance, jamais l'ID maître.

## ID-005 — Contrôles systématiques

- Champs `entities`, `properties`, assertions et sources v11 validés contre le schéma officiel et le registre.
- Références manquantes et KS inexistantes = erreur.
- Un ID peut apparaître dans mille assertions mais reste une identité unique pour les métriques de couverture.
- Le texte libre dans une citation doit rester inchangé.

### Cas de rejet obligatoires

`ID-R1` namespace absent, `ID-R2` Q brut en sujet, `ID-R3` KP comme entité, `ID-R4` allocation concurrente du même KQ, `ID-R5` source KS orpheline, `ID-R6` mutation rétroactive du registre déjà publié.

**Source upstream :** `spec/v11/Identity-and-Wikidata.md`, `kristal-identity-registry.schema.json`, `kristal-semantic-graph.schema.json`.
