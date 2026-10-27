# diK — Interface, écrans et parcours (spécification 0.1.0)

## 1. Tableau de bord

L'application affiche les projets connectés, leurs namespaces, leurs catalogues et la couverture par langue **pour les identifiants réellement utilisés**. Chaque pourcentage porte une mention `KQ` ou `KP`, la version du graphe et celle du catalogue. Ne jamais afficher un score 100 % si l'inventaire comporte des mots non résolus.

Cartes de synthèse : nombre de Kristals inspectés, KQ/KP distincts, langues déclarées/présentes, répartition des traductions directes / fallbacks / manques / conflits, candidats d'identité en attente, sources expirées ou fichiers à empreinte invalide.

## 2. Matrice de complétude

Axes : Kristals (ou domaines) × langues. Cellules : pourcentage de couverture directe, couverture utilisable en repli et volume de manques. Filtrage par KQ/KP, domaine, fréquence d'utilisation et source. Cliquer une cellule affiche la liste exacte des identifiants sans libellé, leurs sources disponibles et l'historique de leur statut. Export JSON de référence `kristal_dik_coverage_report` et, plus tard, CSV détaillé et JSONL vérifié.

Une langue sans entrée doit rester visible à 0 %, pas disparaître du tableau. Une traduction `fr-CA` obtenue par `fr` est affichée comme **fallback**, jamais comme libellé direct.

## 3. Atelier de conciliation

Pour un KQ/KP sélectionné, afficher côte à côte les libellés français, anglais et autres langues issus de : Wikidata, dictionnaires externes acceptés, corrections Kristal. Montrer les décisions `exactMatch` et `closeMatch` séparément, les licences, la source/version et les preuves. Proposer « préférer ce libellé », « conserver les deux comme alias », « marquer douteux », « demander revue », « refuser la correspondance » ; l'édition écrit une **nouvelle couche versionnée**, sans toucher au snapshot importé.

Conflits de même priorité : état bloquant à résoudre, jamais choix arbitraire. Un même mot peut valablement pointer vers plusieurs KQ : ne pas imposer l'unicité inverse.

## 4. Sources de dictionnaires

Écran sources : créer source `Wikidata locale`, `dictionnaire externe`, `curation locale`, pointer vers fichier/dossier, afficher source/version/date/empreinte/licence/conditions d'usage, lancer un **dry-run** d'import et une comparaison de snapshots. Les nouvelles correspondances d'identité sont proposées en attente, jamais automatiquement validées sur similarité lexicale.

### Import Wikidata

- Source recommandée : copie locale déjà possédée par l'opérateur.
- Source distante facultative : [Wikidata JSON entity dumps](https://www.wikidata.org/wiki/Wikidata:Database_download), téléchargés sur choix explicite, avec hash, reprise, quotas et surveillance de l'espace disque.
- Les libellés/alias/descriptions de Q/P sont *des termes de concepts*, pas un dictionnaire linguistique exhaustif. Les lexèmes de Wikidata (`L`, sens et formes) utilisent un **autre modèle** : [documentation](https://www.wikidata.org/wiki/Wikidata:Lexicographical_data/Documentation). Leur ingestion nécessitera un contrat spécialisé, elle ne doit pas être mélangée par erreur aux Q/P.
- L'importation du Framework v11 est **déjà possible hors-ligne** sur un dump local et un crosswalk `exactMatch` accepté ; l'interface de téléchargement et la synchronisation massive restent à construire dans diK.

## 5. Atelier de migration des Kristals anciens

Vue source à gauche : champs historiques et contexte de graphe. À droite : KQ/KP proposés, éventuel Q Wikidata lié, type attendu, preuve, statut de décision. Outils : « sélectionner un candidat », « aucun candidat adéquat », « créer une demande de KQ/KP », « approuver/refuser », « exporter le plan ». L'application ne remplace **jamais** du texte documentaire non identifié comme champ d'identité.

Bouton « exécuter la migration » **non prévu pour la v0.1.0** : l'exécution demande une intégration Authoring Kit capable de préserver et vérifier les engagements. L'interface peut seulement exporter un plan non exécutable et visualiser les avertissements.

## 6. Paramètres et gouvernance

Éléments essentiels : namespace actif, langues/variantes BCP 47, fallbacks explicites, ordre de priorité, politique d'approbation, chemins locaux, sécurité réseau désactivée par défaut, licences et conservation des traces. Aucune remontée automatique des mots d'un corpus privé vers les services externes.

## 7. États et erreurs utilisateur

- `validé` : fichier et sémantique approuvés
- `en attente` : suggestion non examinée
- `ambigu` : plusieurs identités candidates ; revue obligatoire
- `absent` : dictionnaire ne propose rien
- `conflit` : plusieurs libellés contradictoires au même niveau
- `périmètre incomplet` : ancien Kristal à mots non normalisés, couverture canonique impossible à certifier
- `empreinte invalide` : source modifiée ou corrompue ; audit bloqué

Toutes les actions sensibles possèdent un écran de prévisualisation et un journal permettant de retrouver *qui* a approuvé *quoi*, *sur quelle version*, *avec quelles preuves*.
