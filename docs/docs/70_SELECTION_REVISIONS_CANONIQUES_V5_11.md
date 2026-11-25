# diK V5.11 — Sélection prudente des révisions canoniques pour une vue dérivée

**État : implémenté dans diK en lecture seule. NON NORMATIF.**

## Ce que les sources réelles prouvent

Le snapshot officiel `znapshot_kristal-public_11240810.zip` contient 126 fichiers `canon/state.index.json`, dont 77 Kristals déclarant 180 révisions V11. Tous déclarent les artefacts `canonical_artifacts` mais **aucun champ explicite ne désigne une révision V11 active**. Plusieurs révisions peuvent appartenir simultanément au canon du Kristal. Il serait erroné d'élire « le nom le plus récent », le plus grand registre ou le plus grand QID.

V5.10 conservait 25 741 correspondances exactes `accepted` *par révision* (12 919 distinctes entre révisions) comme **preuves sources uniquement**. Les 1 776 liens admis par le lecteur historique V5.9 demeurent une couche séparée. Ni l'une ni l'autre des statistiques n'autorise une publication supplémentaire.

### Constats sur le snapshot du 24 novembre

- 5 Kristals ont une seule révision V11 ;
- 71 Kristals ont plusieurs révisions différant au moins par des identités et/ou mappings observés ;
- 1 Kristal possède deux révisions aux identités/mappings identiques dans le contrôle de surface effectué ;
- 49 Kristals ne déclarent aucune révision V11.

Le moteur V5.11 conserve les **72 Kristals multirévisions sans choix automatique**. Dans l'échantillon où 7 graphes dépassent 8 Mio, quatre Kristals sont marqués `MULTIPLE_INCOMPLETE_UNSELECTED` : la lecture du graphe n'a pas validé l'entièreté des artefacts. Le résultat d'une installation vivante devra être vérifié séparément.

## Contrats et invariants

1. Les identités canoniques restent `(namespace_id, KQ/KP)` dans le Framework. diK n'écrit ni dans `kristals` ni dans leurs index.
2. Seuls les chemins répertoriés dans `canon/state.index.json` entrent dans la sélection. Les noms, dates et quantités ne désignent pas une autorité.
3. Pour une révision unique **lisible et inspectée**, diK autorise la consultation dans une **vue dérivée** : `SINGLE_DECLARED_DERIVED_VIEW`. Ce n'est **pas** une sélection normative de l'autorité Framework.
4. Plusieurs révisions nécessitent une décision de revue explicite, liée aux empreintes SHA-256 exactes de l'index, du registre, du crosswalk, **du graphe inspecté** et du catalogue (profil `dik.canonical-selection-decisions/0.2`). Une telle décision ne crée que `OPERATOR_PINNED_DERIVED_VIEW` ; son rédacteur n'acquiert pas le pouvoir de modifier le canon ni d'approuver de nouveaux liens.
5. Les graphes > 8 Mio ne sont pas intégralement inspectés dans ce profil léger. Une révision dont le graphe est non inspecté ne peut pas être sélectionnée : réévaluer le contrôle requis dans une nouvelle version.
6. Un même KQ/KP rattaché à plusieurs Q/P exacts `accepted` à l'intérieur d'une même révision bloque la sélection de cette révision.
7. Les liens `accepted`, les décisions de revue et les références KS restent **déclarations des sources**. Les données lexicales, les attestations Wikidata L/S/F et la qualification de licence demeurent indépendantes.
8. La recherche locale exige toujours namespace + KQ/KP ; la recherche Q/P retourne des références croisées mais ne fusionne jamais les identités.
9. `framework_authority_confirmed = 0`, `new_global_approvals = 0`, `published_dictionaries = 0` dans tous les rapports V5.11 ; les calculs historiques V5.9 sont inchangés.
10. Les 13 langues cibles sont `en fr es de nl sv da nn fi et af it pt`. La base historique `no` est préservée mais n'est plus une langue cible.

## Tables locales ajoutées au SQLite fédéré

- `canonical_revision_inputs` : SHA-256 des fichiers index, registre, crosswalk, graphe (si inspectable), catalogue, par révision. Les chemins restent locaux.
- `canonical_selection` : état de sélection par Kristal, éventuelle révision choisie pour la **vue dérivée**, référence de revue, motif, compteur de correspondances candidates, indicateurs d'autorité et d'admission toujours à zéro.

La sélection dérivée ne change pas les tables `identities`, `crosswalk`, `kristals` héritées de V5.9. Les tables multirévisions V5.10 demeurent consultables.

## Commandes

```powershell
$env:PYTHONPATH = 'C:\mycode\diK\diK\src'
$root = 'C:\mycode\Kristal\kristal-public\kristals'
$out = 'C:\mycode\diK\diK\reports\federation-v511-manuel'
python -m dik world federation-build --official-root $root --output-dir $out --min-kristals 126
python -m dik world federation-audit --dir $out
python -m dik world federation-selection-query --dir $out --wikidata-id Q8018
python -m dik world federation-selection-review --dir $out --output-file "$env:USERPROFILE\Downloads\DIK_SELECTION_A_REVOIR.json"
```

L'export **local** `DIK_SELECTION_A_REVOIR.json` contient les chemins relatifs des révisions, leurs nombres d'identités/mappings et leurs SHA. Ce document **n'est pas une approbation ni une décision**. Il n'est pas joint au ZIP expurgé de bilan.

### Décision de revue explicite (optionnelle, jamais automatique)

Après vérification par une autorité compétente, écrire un document JSON séparé :

```json
{
  "profile": "dik.canonical-selection-decisions/0.2",
  "scope": "derived_view_only",
  "decisions": [
    {
      "kristal": "nom-officiel",
      "revision_dir": "chemin-relatif-exact-provenant-de-la-file-de-revue",
      "state_index_sha256": "sha256-index-64-hex",
      "registry_sha256": "sha256-registre-64-hex",
      "crosswalk_sha256": "sha256-crosswalk-64-hex",
      "graph_sha256": "sha256-graphe-inspecte-64-hex",
      "catalog_sha256": "sha256-catalogue-64-hex",
      "review_decision_id": "decision-reelle-du-relecteur",
      "reviewer": "identite-du-relecteur",
      "rationale": "motif documente de selection pour consultation derivee"
    }
  ]
}
```

Les exemples `sha256-...` sont des espaces réservés, **pas des empreintes valides**. Aucun fichier de décision n'est généré ou rempli automatiquement. Reconstruire **dans un dossier neuf** avec `federation-build ... --selection-file chemin-vers-decisions.json` : tout changement d'un octet dans une source épinglée sera refusé. **Les anciens fichiers de décision `/0.1`, qui n'épinglaient pas les octets du graphe, sont refusés pour toute nouvelle construction** ; les anciens registres dérivés restent des archives consultables, sans promotion. Réexaminer les cinq SHA-256 et établir un nouveau fichier `/0.2` par revue explicite. L'activation éditoriale et l'autorité Framework nécessitent un contrat et un processus d'approbation distincts. Voir [ADR-DIK-FEDERATION-03](../decisions/ADR-DIK-FEDERATION-03-selection-graphe-epingle.md).

## Bilan expurgé

`manifest.json` et son ZIP contiennent uniquement des compteurs par état, le profil, la version des langues et l'empreinte du SQLite dérivé. Pas de mot, ni de gloses, ni de chemin Windows, ni de décisions nominatives. Le SQLite et la file de revue restent sur le poste.

## Limites restantes

- 49 Kristals sans V11 demandent des lecteurs natifs propres à leurs contrats (pas d'IDs devinés).
- Les révisions multiples ne contiennent pas de preuve de « version active » dans les index examinés : une autorité contractuelle doit la déclarer pour un choix normatif.
- 7 artefacts canoniques déclarés absents dans le diagnostic Windows précédent ; leur récupération n'est pas automatique.
- 7 graphes non inspectés dans le profil léger ; la preuve de présence n'est pas une inspection de leur contenu.
- Les 13 dictionnaires ne sont pas encore alignés et publiés, et les 12 919 correspondances sources ne sont pas admises en bloc.
