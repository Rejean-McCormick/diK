# ADR — DIK-LEX-1 : registre de découverte de dictionnaires mondiaux

**Statut : proposed (non ratifié)** · **Date : 2026-11-04**
**Exigences : LEX-001/002/003/004/005/020/021/022/023, XW, IMP.**
**Autorité : Framework 11.0.0-draft.3 (schémas vendoriés inchangés).**

## Contexte

Les catalogues Framework v11 publient des couches `wikidata`, `external` et `curated` liées aux identifiants internes `(namespace, KQ/KP)`; un répertoire mondial d'adresses de dictionnaires ne possède ni leur niveau de preuve ni leurs correspondances approuvées. Le modèle Wikidata L/forme/sens est distinct de l'import existant Q/P. La couche GF/SemantiK réalise la grammaire sans allouer des KQ/KP.

## Décision proposée

1. Introduire un **inventaire de découverte** applicatif `dik.dictionary-source-inventory/0.1-candidate`, séparé du catalogue normatif Framework et des journaux de revue. Il décrit des sources, leurs usages candidats, les droits déclarés et des locales **sans mesurer** leur couverture.
2. Un enregistrement dans l'inventaire **ne publie rien** : ni traductions, ni `exactMatch`, ni `curated`, ni données vérifiées. Les fichiers de dictionnaire et leurs hashes restent gérés par les schémas Framework existants.
3. Traiter **Wikidata Q/P labels** comme candidats à la couche lexicale soumis aux crosswalks exacts acceptés; traiter **Wikidata lexèmes L/S/F** comme observations lexicales séparées en attendant un adaptateur versionné.
4. Distinguer « licence déclarée » et « droits vérifiés pour une redistribution ». Les dictionnaires tiers sont bloqués pour import vérifié jusqu'à preuve de licence et de provenance.
5. Les tags de langue sont vérifiés syntaxiquement à ce stade, **pas** certifiés BCP 47 : l'intégration d'un registre IANA/CLDR versionné et les tests d'alias/script sont un travail requis avant une publication mondiale.
6. Le benchmark `DIK-LEX-1` reste un **profil de qualification proposé**, pas une norme Framework ni une certification effective.

## Options écartées

- Remplacer KQ/KP par les Q/P de Wikidata : viole la séparation normative des identités.
- Fusionner lexèmes L et libellés de concepts Q/P : mélange sens, formes et identité conceptuelle.
- Générer une matrice KQ × toutes les langues : couverture fictive et coût inutile.
- Utiliser directement GF comme dictionnaire de référence : mélange couche de réalisation et autorité sémantique.

## Compatibilité, sécurité et réversibilité

Ajout uniquement. Aucun schéma Framework, fichier récupéré, catalogue curaté, crosswalk ou graphe historique n'est modifié. Le registre de découverte est **inactif** pour la résolution courante. L'enlever ne change pas la projection existante. Tests positifs et négatifs sur références, statuts, namespaces implicites interdits et séparation L/QP.

## Conditions avant acceptation

Validation humaine de l'ADR; revue du contrat de l'inventaire; politique de licence tierce; validation IANA BCP 47, inventaire des sources avec provenance; fixtures S0-S4, tests inter-dépôts et benchmarks mesurés. Aucune de ces conditions n'est réputée satisfaite par le seed.
