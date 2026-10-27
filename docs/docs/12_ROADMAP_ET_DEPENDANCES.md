# 12 — Roadmap et dépendances inter-dépôts

## Ordre de développement recommandé

| Lot | Livrable | Bloqueur / dépendance | Fin de lot vérifiable |
|---|---|---|---|
| A — Base | Repo diK, CLI minimale, lecture projets, validation v11, catalogue local et coverage | Framework v11 draft.3 | Rapport de couverture exact sur fixtures Framework |
| B — Imports | Import local Wikidata JSON/JSONL, staging et hash, dictionnaires tiers | Crosswalks v11 | Snapshot immuable, correction locale préservée |
| C — Conciliation | Index inverse, recherche candidats, revue exact/close, éditions curatoriales | Gouvernance des décisions | Aucun libellé seul n'autorise un exactMatch |
| D — Anciens Kristals | Inventaire schema-aware et plan approuvable | Contrat de source historique | Aucun remplacement dans une citation ni réécriture originale |
| E — Producteur | Application transactionnelle des plans | **Authoring Kit** mis à jour | Nouvelle révision conforme, ancienne intacte |
| F — Grande échelle | 300+ langues, téléchargements/reprise, diffs, index incrémentaux | Pipelines stabilisés | Tests de performance, reprise et intégrité |
| G — Distribution | Integration Pack, visualisation et exports | Contrats stabilisés | Échanges neutres par langue et namespace |

## Repos et snapshots déjà reçus

- `Kristal-Framework` — snapshot v10 puis **v11 draft.3** : schémas, profils, validateurs de référence. **Déjà traité localement**.
- `Kristal-Authoring-Kit` — snapshot 3.3.1 : futur producteur de graphes v11 et applicateur autorisé de migrations. **Prochain repo à réviser**.
- `Kristal-Integration-Pack` — snapshot 0.1.0-alpha.2 : lecture/publication et projections ; vérifier qu'aucun mot ne réapparaît comme clé de graphe.
- `A-Kristal-Catho` — archive de test : audit historique et migration pilote **après** stabilisation.
- `diK` — **nouveau repo**, cette documentation est son cahier des charges ; pas encore d'application dans cette livraison.

## Gestion des versions

Ne pas modifier silencieusement le Framework `11.0.0-draft.3` : si un nouveau champ normatif devient nécessaire (par ex. vue de portefeuille multi-Kristals, décision multi-réviseurs ou un type de rapport définitions/alias), ouvrir une révision de contrat. Les sorties de diK doivent déclarer leur version de format et la version exacte du Framework utilisé.

## Dépendances non négociables

- Authoring Kit doit reconnaître explicitement les rôles de champs des formats historiques et produire un nouveau canon sans perte.
- Integration Pack doit exporter les KQ/KP et données lexicales séparément.
- Les tests de diK et ceux du Framework doivent partager des **fixtures normatives** versionnées pour éviter le drift entre repos.
- Le pilote Catho doit avoir un inventaire avant/après avec seuil **zéro fusion silencieuse**.
