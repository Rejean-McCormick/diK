# diK V5.10 — Index canonique multirévision des 126 Kristals

Statut : **overlay d'observation, non normatif, sans activation**.

## Pourquoi cet overlay

Le diagnostic Windows du 24 novembre 2026 a constaté : 126 index canoniques lisibles, 77 Kristals avec registre V11, 49 sans registre V11, 180 révisions V11, 7 artefacts canoniques manquants et 25 741 lignes `accepted + exactMatch` *cumulées par révision*. Ces 25 741 lignes ne sont pas un total distinct. Le snapshot fourni séparément contenait 12 919 liens distincts après dédoublonnage `(kristal, namespace, KQ/KP, Q/P)`, sous réserve de vérifier les données vivantes.

La V5.9 choisissait un format V11 parmi des chemins anticipés : elle ne pouvait lire que 57 Kristals, 21 026 identités KQ/KP et 1 776 liens exacts acceptés. Rien n'indique que les autres Kristals soient vides.

## Architecture

La commande existante `dik world federation-build` conserve les tables, la clé `(namespace_id, semantic_id)` et l'interface V5.9. Elle ajoute quatre tables locales indépendantes :

* `canonical_sources` : provenance index canonique, contrats natifs, erreurs d'artefacts ;
* `canonical_revisions` : **une ligne par révision V11** annoncée par `canon/state.index.json` ;
* `canonical_identity_evidence` : identités KQ/KP, noms et définitions tels que déclarés par révision ;
* `canonical_crosswalk_evidence` : correspondances externes, statut source, décision et références de preuves.

Le code ne parcourt que les chemins explicitement déclarés dans `canonical_artifacts`, ne suit aucun lien symbolique et ne modifie ni Kristal ni EncyK. Les sources inconnues ou à contrat natif sont comptées, **jamais traduites** en KQ/KP artificiels. Les graphes trop volumineux sont contrôlés sur leur présence uniquement ; le manifeste marque `large_graphs_metadata_only`.

## Choix des révisions — principe de non-régression

Le même Kristal peut déclarer plusieurs versions V11. L'index conserve **toutes** les versions sous leur chemin relatif, sans choisir une version active sur la base du nom, de la date ou du nombre de lignes. Leur état est `OBSERVED_UNSELECTED`. Les liens `accepted + exactMatch` de ces sources sont signalés `SOURCE_ACCEPTED_REVIEWED_REVISION_UNSELECTED`, et ne sont jamais ajoutés aux liens mondiaux acceptés du registre V5.9.

Aucune identité n'est renumérotée, fusionnée, supprimée ou publiée. Les anciens chiffres de V5.9 restent comparables ; les chiffres du supplément canonique sont explicitement séparés. La sélection autorisée d'une révision requiert une décision contractuelle et probatoire ultérieure.

## Commandes

```powershell
$env:PYTHONPATH = 'C:\mycode\diK\diK\src'
python -m dik world federation-build --official-root 'C:\mycode\Kristal\kristal-public\kristals' --output-dir 'C:\mycode\diK\diK\reports\federation-v510-mon-audit' --min-kristals 126
python -m dik world federation-audit --dir 'C:\mycode\diK\diK\reports\federation-v510-mon-audit'
python -m dik world federation-revision-query --dir 'C:\mycode\diK\diK\reports\federation-v510-mon-audit' --wikidata-id Q8018
python -m dik world federation-revision-query --dir 'C:\mycode\diK\diK\reports\federation-v510-mon-audit' --namespace '<namespace exact>' --id KQ1001
```

Une requête locale sans namespace est refusée. Le résultat `UNSELECTED_SOURCE_EVIDENCE_NOT_AUTHORIZED` n'est pas une autorisation de publication. Les noms et définitions restent dans la **base locale** ; le bilan ZIP expurgé ne contient que des statistiques et une empreinte SHA-256.

## Prochaines décisions nécessaires

1. Désigner contractuellement la version active ou l'algorithme admissible pour chaque ensemble multirévision (ne pas déduire de `-v11-2`).
2. Vérifier les 7 artefacts manquants sans reconstruire arbitrairement leur contenu.
3. Ajouter des lecteurs spécifiques pour les 49 Kristals sans registre V11.
4. Effectuer le croisement accepté Q/P ↔ dictionnaires de **13 langues** uniquement après sélection et qualification.
5. Vérifier les droits et distinguer Wikidata Q/P de Wikidata lexèmes L/S/F.

## Limites

Ce correctif ne crée pas de nouveaux liens exacts approuvés ; il ne publie aucun dictionnaire et ne convertit pas les 49 contrats non V11. Il ajoute un inventaire analytique traçable. Les consommateurs EncyK, SemantiK, Runtime et Spek continuent à utiliser le contrat V5.9 et n'ont pas besoin d'être modifiés pour cette extension facultative.
