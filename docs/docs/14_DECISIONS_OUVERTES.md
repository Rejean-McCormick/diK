# 14 — Décisions ouvertes et questions d'implémentation

Ces points ne doivent pas être inventés pendant l'écriture de code : les documenter sous forme d'ADR avant de rendre les opérations concernées disponibles.

1. **Namespace partagé :** autorise-t-on une identité globale commune à plusieurs repos, et comment sécuriser les alias inter-namespace ? Jusqu'ici : séparation stricte.
2. **Allocation KQ/KP :** qui possède le registre d'allocation, quelle concurrence, quelle garantie de non-réutilisation lors d'un merge Git ? Le Framework draft.3 ne fournit pas de compteur global distribué.
3. **Révision d'exactMatch :** un réviseur suffit-il ou deux pour des concepts sensibles ? Quel schéma d'approbation signé et de révocation ?
4. **Curation multilingue :** distinguer « correct linguistiquement », « accepté dans ce domaine », « approuvé pour export » ; clarifier les priorités entre domaines et registres.
5. **Catalogue géant :** sharding par locale, par domaine ou plages d'ID ? Compression, FTS, ordre d'énumération et algorithme de hachage pour reproductibilité.
6. **Calcul d'une couverture nulle :** UI doit annoncer `non applicable` pour N=0, tandis que les rapports v11 conservent leurs champs numéraux / booléens selon le schéma.
7. **Portfolio de graphes :** nouveau contrat de rapport multi-Kristals ou enveloppe référant plusieurs rapports v11 inchangés.
8. **Lexèmes Wikidata L :** à traiter dans un modèle spécialisé ultérieur, distinct du crosswalk Q/P canonique.
9. **Migrations partielles :** quelles politiques pour un ancien Kristal où seuls certains référents sont résolus ? Interdire le label de « migration complète ».
10. **Synchronisation réseau :** mécanisme de téléchargement, stockage de miroir, quotas, gestion d'erreurs, contrôles des redirections et fin de validité d'une source.
11. **Politique de licences :** quels termes autorisent la redistribution publique vs usage local, et comment isoler les couches non redistribuables ?
12. **Métriques qualité :** couverture labels vs définitions, translittérations, variantes, alias, validation humaine ; ne pas les réduire à un chiffre unique.

### Décision déjà prise (à ne pas rouvrir implicitement)

Le stockage canonique demeure **file-backed et versionné**, avec index dérivés ; les mots restent dans les lexiques, pas dans les identités canoniques. Le rapprochement exact exige des preuves et une décision. La migration historique est non destructive. Références : [ADRs v0.1](../decisions/ADR-HISTORIQUE-v0.1.md).
