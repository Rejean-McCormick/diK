# diK — Audit intelligent local des Kristals × 14 langues (V2)

## Lancement

Dans le dépôt diK déjà installé : `LANCER_SCAN_KRISTALS_14_LANGUES.cmd`, ou avec Python 3.11+

```powershell
Set-Location 'C:\mycode\diK\diK'
$env:PYTHONPATH = (Join-Path (Get-Location) 'src')
py -3 -m dik coverage kristals14 --root 'C:\mycode' --dik-root 'C:\mycode\diK\diK'
```

La commande garde les sources **en lecture seule**, sans réseau, Git, Render ou traduction automatique.
Chaque exécution est publiée dans un nouveau dossier sous
`C:\mycode\diK\diK\reports\scans_14_langues\SCAN_...`.

## Périmètre et distinction des copies

Le scanner découvre les projets Kristals, prend une révision v11 complète par projet et
vérifie les couches du catalogue sélectionné avec le Framework (schéma, namespace,
empreintes SHA-256, intégrité des couches, conflits, alignements externes autorisés).

Une **copie exacte** doit présenter les **quatre mêmes fichiers v11** (graphe, registre,
crosswalk, catalogue, SHA-256) et toutes ses couches doivent aussi correspondre à leurs
empreintes attendues. Les copies sont conservées dans l'inventaire, mais ne gonflent plus
les totaux des libellés et identités. Le choix du représentant favorise heuristiquement
les dossiers habituels par rapport aux chemins staging / archives : ce n'est **pas**
une certification de la branche active sur disque.

Un manifeste diK invalide ne bloque plus l'utilisation d'une révision v11 complète de
repli lorsqu'elle existe dans le **même** Kristal. La source invalide reste signalée.

## Recherche de dictionnaires déjà présents

Le scanner inventorie les autres `dictionaries/catalog.json` dans le dossier du Kristal et,
pour les ensembles identiques, dans leurs copies. Un catalogue alternatif est **compatible
audité** seulement si le namespace correspond, si le registre et le crosswalk sont
**byte-identiques** à ceux de la révision choisie et si l'audit Framework de ses couches
réussit. Sinon il apparaît comme *rattachement non prouvé*, *namespace différent* ou
*audit impossible*. Aucun dictionnaire alternatif n'est fusionné, déclaré canonique,
ni appliqué automatiquement.

Les dictionnaires sans catalogue compatible, les autres formats de documents et les mots
libres des dépôts ne sont pas certifiés ou interprétés comme traductions KQ/KP.

## Fichiers de sortie

| Fichier | Description |
|---|---|
| `rapport.json` | Totaux calculés sur ensembles distincts, copies, candidats, limites et états |
| `scan.log` | Journal local de chaque Kristal |
| `kristals_14_langues.csv` | Inventaire exhaustif, états `evalue`, `copie_exacte` ou `non_evaluable`, représentant et rôle probable du dossier |
| `copies_exactes_14_langues.csv` | Copies et représentant retenu |
| `couverture_kristals_langues.csv` | 14 lignes par Kristal ; copies et non évaluables exclus des taux |
| `matrice_14_langues.csv` | Chaque KQ/KP × locale pour les **ensembles uniques évalués** |
| `lacunes_14_langues.csv` | Toutes les cellules sans traduction directe, y compris replis et langues non configurées |
| `mots_a_completer_14_langues.csv` | Cellules `manquant` dans un **catalogue configuré et audité**, sans candidat alternatif vérifié |
| `catalogues_candidats_14_langues.csv` | Inventaire des catalogues alternatifs repérés et nature des preuves |
| `traductions_a_recuperer_14_langues.csv` | Propositions issues de couches alternatives compatibles auditées, **à valider avant intégration** |
| `catalogues_14_langues.csv` | Couches effectivement auditées utilisées pour les langues cibles |
| `alertes_14_langues.csv` | Échecs v11, révisions invalides et avertissements |

Les CSV sont en UTF-8 BOM avec séparateur `;` (Excel).

## Les quatre états des cellules

- `direct` : libellé trouvé dans la couche vérifiée de la langue demandée.
- `repli` : libellé trouvé dans une langue de repli explicitement configurée.
- `manquant` : la langue **est configurée**, mais le KQ/KP n'a aucun libellé dans
  les couches du catalogue sélectionné audité. Cela ne prouve pas son absence du disque entier.
- `langue_non_configuree` : aucune entrée pour la langue dans ce catalogue ; ce n'est
  **pas** une traduction prouvée manquante.

Un Kristal `non_evaluable` n'a pas de vérifications comptées. Une `copie_exacte` ne
rajoute pas de cellules ni de taux, même si son contenu est indiqué dans son inventaire.

**Limite :** la V2 mesure les libellés liés aux identifiants sémantiques KQ/KP, pas la
qualité linguistique ni l'exhaustivité de tous les mots possibles. Les chiffres V2 ne
sont pas directement comparables à ceux de la V1, dont les copies étaient additionnées.
