# 01 — Mission, frontières, terminologie et conformité

## 1. Portée diK 1.0

**Produit cible** : application installable localement et automatisable par CLI/API, capable de gérer des dictionnaires multilingues, réconcilier des sources, importer/synchroniser Wikidata, auditer la complétude de Kristals, générer/restaurer des projections linguistiques, préparer des migrations supervisées.

**Hors portée** : héberger Wikidata lui-même, créer des identifiants Q/P officiels, enseigner un modèle IA, fusionner des KQ automatiquement, modifier les commitments d'anciens Kristals, garantir 300 traductions complètes, exécuter seul des migrations v9/v10, inventer un format concurrent du Framework.

### Niveaux de maturité

- **AS-IS** : comportement vérifié dans le code diK 0.3.0, décrit sans extrapolation.
- **UPSTREAM** : obligation Framework v11 draft.3 à respecter ; pas « fonctionnalité finie » dans diK.
- **TARGET** : comportement obligatoire à développer pour diK 1.0.
- **OPTIONAL** : extension isolée sans effet sur les invariants.

Le fait qu'un schéma/outil upstream sache valider un JSON n'implique pas qu'une interface de gestion complète existe.

## 2. Définitions invariantes

- **Référent sémantique / IRS** : identité de personne, objet, événement, concept ; `KQ…` dans l'espace Kristal. Clé vraie : `(namespace_id, id)`.
- **Propriété** : relation `KP…`. Assertion : `KA…`. Source : `KS…`.
- **Crosswalk** : correspondances type+statut+preuve avec Wikidata ou autres référentiels.
- **Dictionnaire lexical** : noms, variantes, alias, descriptions, préférences locales ; ne définit pas le sens d'une identité.
- **Projection** : vue linguistique dérivée d'un graphe canonique. **Restauration** : restitution de la structure sémantique conservée, pas « traduction inverse ».
- **Migration legacy** : opération nouvelle et auditable, après résolution du rôle sémantique exact de chaque champ.
- **Snapshot** : état publié, content-addressed ou hashé, non modifié après publication.

## 3. Frontières

1. **Import** est impur (IO) mais n'accède pas en écriture au graphe source.
2. **Réconciliation** produit décisions proposées puis approuvées, pas d'inférence d'identité.
3. **Lookup** est pur avec un catalogue/crosswalk/registre verrouillés par version.
4. **Projection** lit les données canoniques et crée un dérivé ; peut être supprimée et recréée.
5. **Édition d'une projection** devient un patch sémantique candidat ; pas une mutation du canon.
6. **Publication** écrit par staging + vérification + commit atomique ; le lecteur ne voit jamais un catalogue incomplet.

## 4. Classification des exigences

- Critique `P0` : perte sémantique, confusion identité/langue, données écrasées, migration non autorisée, correspondance fausse, intégrité manquante.
- `P1` : correction de complétude, échelle 300 langues, index/transactions, interopérabilité.
- `P2` : ergonomie, exports, rapports enrichis.

Toute faille `P0` bloque la livraison stable même si le nombre de tests réussis paraît bon.
