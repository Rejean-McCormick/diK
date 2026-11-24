# ADR-DIK-LEX-6 — Lecteurs Wikidata par schéma, reprise et absence d'activation implicite

- Date : 2026-11-23
- Statut : **implémenté pour le diagnostic V5.3 (alpha.11) ; habilitation/publication non ratifiées**
- Contextes : [53 — diagnostic](../docs/53_DIAGNOSTIC_FACTUEL_V5_2_VERS_V5_3.md), [54 — architecture](../docs/54_ARCHITECTURE_LECTURE_WIKIDATA_V5_3.md), [55 — schémas](../docs/55_CONTRATS_SCHEMAS_JSONL_V5_3.md), [56 — reprise](../docs/56_STREAMING_REPRISE_SECURITE_V5_3.md).

## Contexte

V5.2 a découvert 40 JSONL thématiques, inspecté 37 et écarté trois copies identiques ; deux sources ont été tronquées à 150 000 lignes chacune. Le lecteur a reconnu zéro Q/P et classé 35 sources `no_accepted_qp_overlap`. Comme les **vrais schémas des JSONL ne figurent pas dans le bilan**, cette classification ne prouve pas l'absence d'identifiants ou de recoupements.

## Décision proposée

1. **Profil d'abord** : aucune conclusion d'absence sans schéma validé et extraction d'identifiants réussie.
2. **Adaptateur typé** : parser les fichiers selon leurs champs et leurs rôles réels, observés sur le contenu ; ne pas réutiliser le lecteur `QID → locales` pour les assertions sans preuve.
3. **Parcours complet ou partiel explicite** : lecture streaming, checkpoint versionné, vérification d'empreinte et reprise déterministe ; EOF nécessaire mais non suffisant à une conclusion d'absence.
4. **Jointure de confiance** : seuls les crosswalks officiels v11 `exactMatch accepted` avec pièces KS établissent `(namespace,KQ/KP) ↔ Q/P` ; aucun lien par graphie, propriété d'assertion ou suffixe d'identifiant.
5. **Observation ≠ habilitation** : source intacte, Q/P recoupé et libellé trouvé ne prouvent ni licence ni droit de publication. Aucune activation dans le lot V5.3.
6. **Périmètre stable** : 126 Kristals officiels, 14 locales exactes ; les 69 non évaluables et le raccordement GF/L/S/F sont des chantiers séparés.

## Conséquences attendues

- Rapports plus honnêtes : `schema_unknown`, `no_qp_extracted`, `partial_budget`, `complete_no_accepted_qp_overlap` distingués.
- Des Q/P observés peuvent augmenter sans que les **formes résolues** augmentent.
- Pas de modification des dictionnaires, Kristals ou catalogues publiés.
- Tests d'adaptateur basés sur des **enregistrements réels** et tests de reprise/empreintes obligatoires.
- L'adoption formelle d'une politique d'activation et de redistribution nécessite une autre décision.

## Alternatives rejetées (à ce stade)

- Deviner le chemin QID par recherche récursive de textes ressemblant à `Q123` : augmente les faux liens.
- Forcer tous les JSONL dans le modèle `{qid,labels}` : a déjà donné des faux « zéro ».
- Enlever simplement la limite 150 000 sans checkpoint ni bornes mémoire : améliore l'exhaustivité au prix de risques opérationnels.
- Déclarer « mot manquant » pour toute source dont l'inspection est incomplète : confond absence et indisponibilité.
- Activer une forme directement à partir d'un mot commun : incompatible avec le canon KQ/KP.

## Condition de ratification

Approbation du contrat et preuves de tests sur les schémas réels des 40 sources, y compris deux grands fichiers, sans activation automatique. Jusqu'à cette ratification, ce texte reste une **proposition documentaire**.


## État après implémentation alpha.11

Lecteurs, profilage, reprise, rapports et tests de non-activation réalisés. La ratification de la politique d’habilitation et la certification des schémas inconnus des 40 fichiers réels restent **hors du lot**. Voir [chapitre 61](../docs/61_IMPLEMENTATION_EFFECTIVE_V5_3.md).
