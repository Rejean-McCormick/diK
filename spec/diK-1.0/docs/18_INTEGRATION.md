# 18 — Compatibilité Framework, Authoring, Integration et Kristals existants

## Contrats connus (snapshots fournis)

- **Framework v11 draft.3** : source normative des schémas, outils v11 de référence, profils lecteurs, lexique, crosswalk, coverage et plans non exécutables.
- **Authoring Kit 4.0.0-draft.2** : producteur pouvant qualifier v11 (`qualify-v11`), gardien de révision et migration potentielle ; **ne pas supposer que la migration automatisée universelle est déjà implémentée**.
- **Integration Pack 0.2.0-alpha.1** : adaptateurs de lecture et projections ; devrait consommer les IDs KQ/KP sans en faire du texte canonique.
- **diK 0.3.0** : import local, audit, rapport, projection compacte/verbose/restore ; les workflows nouveaux de 1.0 restent à coder.
- **A-Kristal-Catho** : corpus pilote legacy ; ne pas modifier les originaux sans sauvegarde/version et plan approuvé.

## Test croisé obligatoire

1. Charger fixtures Framework v11 draft.3 avec diK et Authoring Kit ; produire coverage identique structurellement, même dénominateur KQ/KP.
2. Exporter une projection compacte avec diK ; vérifier via diK et le consommateur si ce dernier revendique la compatibilité ; restituer `G` et comparer à l'original.
3. Présenter la vue dans Integration Pack : labels uniquement dans zone de présentation, jamais dans les IDs.
4. Générer plan legacy diK; Authoring Kit **revérifie** source hash, rôle du champ, décisions et KS, puis produit une nouvelle révision ; l'ancien artefact reste identique.
5. Tester une version de schéma modifiée -> rejet du pin, pas fallback silencieux.

## Publicités de compatibilité interdites

Ne pas dire « Full v11 certified » si seule la validation JSON Schema marche. Ne pas assimiler complétude lexical et alignement Wikidata. Une migration testée sur trois mots n'est pas une qualification de Catho entier.

## Dépendances de publication

- diK peut être livré avec snapshot Framework draft.3 épinglé et indiquer sa compatibilité **limitée**.
- Pour marquer diK 1.0 stable, l'équipe décide si Framework doit être stable ou si un draft exact peut être cible ; si draft, mentionner ce risque explicitement.
- Toute modification normative hors diK doit être proposée au repo Framework, pas injectée silencieusement dans un adaptateur diK.
