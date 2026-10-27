# Jeux d'exemples et limites

## Exemples officiels non altérés

`framework-v11-unaltered/` recopie uniquement certains fichiers de test fournis avec **Framework 11.0.0-draft.3** : graphe, registre, crosswalk, rapport de couverture et plan de migration. Ces fichiers prouvent le **contrat historique de la fixture**, pas la validité de tous les cas de production. Les exemples Wikidata identifient notamment Augustin d'Hippone `Q8018` ; les autres `KQ/KP` des fixtures ne sont pas des IDs de production.

## Exemples applicatifs candidats

`proposed/` contient cinq payloads construits pour les **schémas diK candidats**, avec SHA de démonstration (`aaaa…`, `bbbb…`, `cccc…`). **Ne pas utiliser leurs empreintes comme checksums de fichiers réels**, ni leurs décisions accepted comme une vraie revue. Les exemples démontrent seulement forme et contraintes du schéma.

## Trois scénarios contractuels incontournables

1. **Wikidata ajoute un nouveau Q** : ajouter `candidate` puis `accepted exact` seulement après revue et KS ; `KQ` préexistant inchangé ; projections historiques inchangées.
2. **Projection diK `clean`** : lecteur voit texte localisé ; export JSON garde le canon, `clean.md` seul n'est pas une source de restauration ; statut missing explicit.
3. **Ancien Kristal avec « grâce »** : identifier rôle JSON Pointer, proposer éventuellement plusieurs KQ distincts, garder citation/littéral inchangés, émettre plan non exécutable ; producteur autorisé génère nouvelle révision uniquement après approbation.

La validation de schéma positive et négative est effectuée par `tools/validate_documentation.py`, pas par un faux serveur diK 1.0.
