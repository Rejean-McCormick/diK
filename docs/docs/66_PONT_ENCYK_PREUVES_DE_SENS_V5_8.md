# 66 — V5.8 : diK ↔ EncyK, preuves de sens fédérées pour 14 langues

## Objectif

La V5.7 a construit les 14 dictionnaires candidats depuis l'index lexical local
`D:\EncyKlopedia\30_working\lexical\harvester\index-v1\lexical.sqlite3`.
Cette V5.8 rend **consultables depuis diK** les dossiers de preuves de sens déjà produits
par EncyK : `dik-reconciliation-v1` (v0.5) et `dik-enrichment-v1` (v0.6), en
**lecture seule** et sans recopier leurs bases SQLite volumineuses.

Ce raccordement est un **pont de consultation et de revue**, et non une
publication, une validation de sens ni une extraction exhaustive de dictionnaires.
Le projet DIK-LEX-1 conserve le rôle de gestionnaire de dictionnaires.

## Trois identités qui restent distinctes

1. **Graphie / lemma_key** : la clé NFKC/casefold d'EncyK regroupe des homographes.
   Elle peut masquer des homonymies, catégories grammaticales et sens différents.
2. **Candidat v0.5** : `lexcand-` suivi du SHA-256 JSON compact de
   `[language, lemma_key]`. Le `candidate_id` **n'est pas** un KQ/KP.
3. **Preuve v0.6** : `(source_id, source_line, candidate_id, language)`.
   Elle peut correspondre à la même observation V5.7 ou à une autre source
   portant le même homographe. Le code le signale explicitement.

Les identifiants Wikidata `L…-S…` éventuellement présents restent **externes**,
jamais convertis en Q/P ou en identité KQ/KP sans décision documentée.

## Contrôles du pont

- Vérification des profils exacts EncyK `candidate-v0.5` et `candidate-v0.6`,
  des manifestes et handoffs `may_be_published=false`, des états complets,
  des empreintes communes d'index, et des métadonnées des bases SQLite.
- Reproduction de `quality_audit.db_fingerprint` à partir des **métadonnées** de
  `source_files` et `language_stats`, sans balayage massif de `entries`.
- Vérification des colonnes requises, de l'index `(language,candidate_id)`
  pour les preuves, des compteurs par langue et de la revue v0.6.
- Les 14 codes exacts `en fr es de nl sv da no nn fi et af it pt` sont isolés ;
  aucun alias `nb` → `no` ou `nn` n'est créé.
- Sources EncyK ouvertes SQLite `mode=ro` + `query_only=ON` ; pas d'option
  `immutable=1` car un WAL peut contenir des écritures non checkpointées.
  Aucune modification, VACUUM, checkpoint, copie ou téléchargement d'EncyK.
- Les **14 SQLite V5.7 restent inchangés**. Seuls de petits fichiers de liaison
  par langue sont créés dans `D:\diK\lexical\collection-v57\semantic-v58`.
  Prévalidation des 14 cibles, rejet des liens symboliques, refus de toute
  liaison existante modifiée et remplacement atomique de fichiers nouveaux.

## Commandes diK

```powershell
$env:PYTHONPATH = 'C:\mycode\diK\diK\src'
py -3 -m dik world local-semantic-plan14 --encyk-root 'D:\EncyKlopedia' --collection-dir 'D:\diK\lexical\collection-v57'
py -3 -m dik world local-semantic-bind14 --encyk-root 'D:\EncyKlopedia' --collection-dir 'D:\diK\lexical\collection-v57'
py -3 -m dik world local-semantic-lookup --encyk-root 'D:\EncyKlopedia' --collection-dir 'D:\diK\lexical\collection-v57' --language fr --term chat
py -3 -m dik world local-semantic-export14 --encyk-root 'D:\EncyKlopedia' --collection-dir 'D:\diK\lexical\collection-v57' --output-zip 'C:\mycode\diK\diK\reports\DIK_V5_8_BILAN_MANUEL.zip'
```

La consultation renvoie la graphie et sa catégorie grammaticale, les gloses
**candidates** limitées des enregistrements v0.6, les identifiants de sens `L…-S…`
observés et le booléen `anchor_matches_same_lexeme`. La valeur `false`
signifie : **homographe dans les sources, identité de sens non démontrée**.
Même quand la valeur est `true`, il s'agit d'une preuve liée à une ligne source,
**pas** d'une équivalence entre deux sens ou d'un mapping KQ/KP.

Les gloses peuvent être soumises aux droits des sources : les commandes de
consultation affichent les mots et preuves seulement **sur le poste local**.
Le ZIP de bilan est **expurgé** : seuls profils, compteurs par langue, états
et catégories de revue sont transmis. Aucun mot, glose, chemin Windows,
identifiant sensible, base massive ou texte de source n'est exporté.

## Ce que signifie « 14 dictionnaires complets »

Les 14 **collections de lemmes et formes** V5.7 sont déjà matérialisées, mais
aucune langue ne peut être déclarée exhaustivement couverte. Les preuves v0.6
ne portent que sur les **ancrages échantillonnés par EncyK v0.5** ; les entrées
mono-source et les sens non échantillonnés n'y figurent pas nécessairement.
La V5.8 n'invente donc pas les sens manquants, et n'augmente pas le compteur
canonique de résolution KQ/KP.

Le travail restant est l'import **complet des sens depuis les archives primaires**
locales, accompagné d'un audit des licences et des SHA officiels, puis la
réconciliation sémantique supervisée, la qualification des formes, des tests
sur le corpus Windows réel et la publication versionnée après autorisation.
La V5.8 prépare cette étape sans multiplier les archives ni les bases.

## Validation et reprise

`PYTHONPATH=src python -m pytest -q` valide les schémas synthétiques reproduits
à partir du code EncyK fourni, les empreintes, la consultation, le refus des
sources modifiées, la protection des fichiers locaux, les 14 langues et
l'absence de promotion des candidats. Les tests n'ont pas lu les bases de
plusieurs gigaoctets sur le Windows cible : l'exécution du lanceur produit
le bilan réel à renvoyer.
