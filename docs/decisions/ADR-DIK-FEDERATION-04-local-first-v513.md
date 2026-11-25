# ADR diK V5.13 — priorité au canon local

Statut : **proposition additive**, soumise aux règles diK 1.0 et Framework v11.

## Décision

Les artefacts canoniques des Kristals sont modifiés ou révisés **dans chaque espace local propriétaire** (`C:\mycode\Kristal\locals`), jamais par édition directe de `kristal-public`. La collection publique est une surface de lecture **dérivée et sélectionnée**. Les révisions originales et toutes les assertions sourcées restent préservées.

La clé sémantique fédérée exige le couple `namespace_id + identifiant local KQ/KP`; `KQ1001` seul n'est pas global. Un QID ou PID Wikidata n'est pas une identité canonique Kristal. Les liens `exactMatch` exigent une preuve externe et une revue indépendante; des labels semblables ou un `audited_rule` automatique n'en constituent pas une validation humaine.

**Ne jamais supprimer les libellés ou leurs sens** : conserver les couches lexicales multilingues, la provenance, les variantes, les révisions, les rapports d'ambiguïtés et les mappings de retour Wikidata. La résolution de conflits n'est pas une inférence à partir des chiffres.

## Contrôles

- Diagnostic `kristal_manager audit-local-public` : compare les octets du `state.index.json` et des artefacts canoniques déclarés et visibles sur les deux surfaces. Il ne fait aucune mutation.
- Sélection diK V5.12 : vue dérivée uniquement lorsque les cinq hachages, **y compris celui du graphe**, sont épinglés; refuser les révisions incomplètes ou ambiguës sans accord propriétaire.
- Préparation : Authoring Kit et Manager sur copie privée explicite, puis contrôles C3; aucun `push` sans reçus C1/C2 indépendants et vérification de l'exact commit.
- Bootstrap : drift des fichiers gérés traité séparément, sur plan propriétaire; aucun rafraîchissement arbitraire de `.kristal/bootstrap-state.json`.

Cette décision n'installe pas de registre sémantique total globalement qualifié. Les inventaires et parités de schéma déjà réussis sont des **vérifications d'intégrité**, pas une ratification de toutes les correspondances. Le bilan de snapshot du 24 novembre 2026 relève 127 locaux, 126 publics, 985 artefacts communs identiques et 7 fichiers locaux volontairement absents des manifestes publics.
