# Instructions impératives pour les agents IA — diK

La source normative est `spec/diK-1.0/AGENTS.md`, puis `SPEC_LOCK.md`.

1. Le Framework v11 définit les KQ/KP/KA/KS. Aucun mot, URI historique ou Q Wikidata ne devient un identifiant canonique Kristal.
2. Aucun mapping `exactMatch` n'est accordé sur similarité de mots ou score de modèle. Revue et preuves KS nécessaires.
3. Le graphe historique, les dictionnaires importés et les engagements restent inchangés. Émettre des révisions isolées.
4. `clean.md` n'est pas réversible. Seule une enveloppe vérifiée contenant `canonical_graph` permet de restaurer.
5. Ne jamais prétendre que des tests/benchmarks/validations non exécutés sont réussis.
6. Ne pas modifier les contrats Framework existants ni réécrire les schémas vendored pour contourner un test.
7. Les nouveaux schémas diK 1.0 sont **candidats**, pas normatifs Framework.
8. `diK 1.0.0-alpha.6` est une implémentation partielle, pas une certification produit v1.0.
9. Tout nouveau changement requiert tests positifs/négatifs et mise à jour explicite du rapport de qualification.

## Contrat obligatoire de l’interface locale (alpha.2)

- Navigation par **intentions** (UX-01/UX-05/UX-06/UX-07) : un espace pour concepts et corrections, un pour complétude, un pour lecture. Les diagnostics restent secondaires (UX-09). Ne pas ajouter une page par commande CLI.
- Afficher les statuts **réels** : candidat lexical ≠ correspondance approuvée ; correction locale ≠ approbation cryptographique ; traduction repliée ≠ traduction directe.
- Toute édition Web doit être désactivée par défaut. Si explicitement activée, elle publie uniquement un **nouveau catalogue candidat** en dehors de la racine canonique, avec jeton CSRF, contrôle d’Origin/Host et confirmation. Jamais de mutation du graphe ni du crosswalk.
- La vue humaine épurée peut cacher les identifiants visuellement, mais l’export conserve toujours un **graphe canonique complet**. Restaurer seulement l’enveloppe vérifiée.
- Ne jamais « simplifier » les protections du serveur local ou déplacer des approbations d'identité vers l’UI sans modèle d’authentification ratifié.
- Lire `docs/docs/19_ATELIER_WEB_v1-alpha2.md` avant toute refonte d’interface; étendre les tests HTTP positifs et négatifs.

## Contrat supplémentaire alpha.3 — conciliation

- Les files `competing_preferred` et `shared_term` sont des **observations**, pas des décisions sémantiques. Interdiction de transformer les signaux lexicaux en `exactMatch` ou de fusionner des KQ/KP.
- Les différences entre couches de priorité distincte ne doivent pas être silencieusement supprimées : afficher les sources et la décision d'affichage séparément.
- Les index SQLite sont reconstruisibles : lorsqu'un index précédent ne comprend pas `dik-conciliation/1`, demander sa reconstruction, sans éditer ou migrer silencieusement les artefacts historiques.
- Aucun changement d'état par GET, rapport de conflits ou fiche de KQ. La correction opt-in crée seulement un nouveau catalogue candidat.
- Consulter `docs/docs/20_CONCILIATION_LEXICALE_v1-alpha3.md` avant toute modification de ce moteur ou de son interface.


## Contrat supplémentaire alpha.4 — synchronisation Wikidata

- Aucune source réseau n'est consultée implicitement. Seule une commande d'acquisition explicite peut contacter une URL Wikidata officielle HTTPS ; redirects non autorisés et URL tierces doivent être bloqués.
- Un hash SHA-256 calculé localement ne prouve pas une authentification Wikidata. Pour `sync import-mirror`, l'opérateur fournit indépendamment l'empreinte approuvée ; refuser les miroirs non vérifiés.
- La reprise HTTP vérifie `Range`, `If-Range`, validator et longueur ; jamais de concaténation aveugle. L'import d'un dump compressé ne prétend PAS reprendre arbitrairement à une position décompressée.
- `sync diff` compare des observations lexicales, ne transforme aucun événement en `exactMatch`, et n'écrase ni anciens catalogues ni corrections curatées.
- Consulter `docs/docs/21_MIROIR_WIKIDATA_REPRENABLE_v1-alpha4.md` avant de modifier import, miroir ou comparateur.


## Contrat supplémentaire alpha.5 — identités externes en mouvement

- `sync evolution` consomme des observations **normalisées**. Ne pas prétendre que le JSONL candidat est un format natif ou authentifié de dump Wikidata.
- Une redirection ou une fusion de Q/P n’autorise jamais une fusion de KQ/KP. Toute révision requiert une preuve externe indépendante et une décision humaine.
- Rejeter les chaînes cycliques, les types Q/P mélangés, les événements dupliqués et les sorties qui écraseraient les sources.
- Un split candidat n’est ni une vérité ni un nouveau KQ : garder les candidats et les références pour revue.
- Lire `docs/docs/22_EVOLUTIONS_WIKIDATA_v1-alpha5.md` avant d'étendre les imports, les alignements ou le graphe d'événements.


## Contrat alpha.6 — preuves issues de l’API Wikidata

- Seules les réponses officielles `action=query&redirects=1` peuvent être normalisées par `sync extract-redirects` : **aucune interprétation des absences comme suppression, scission ou fusion**.
- `sync probe-redirects` est manuel, ciblé sur les correspondances exactes déjà acceptées et strictement borné ; aucun réseau pendant lecture, projection ou vérification du canon.
- Conserver le fichier des réponses brutes et son SHA-256 ; le hash local ne prouve pas seul l’authenticité Wikidata. Une redirection ne change jamais un KQ/KP.
- Tout ajout d'un nouveau format amont nécessite validation explicite, jeux de tests adversariaux et documentation de la couverture réelle du format.
- Consulter `docs/docs/23_EXTRACTION_REDIRECTIONS_MEDIAWIKI_v1-alpha6.md` avant modification.

## Import alpha.7 — impératifs anti-drift

- Ne jamais interpréter un mot comme un KQ/KP. Importer uniquement les correspondances exactes approuvées.
- Conserver les imports historiques et les contrats Framework v11 draft.3 inchangés.
- Ne jamais transformer un hash local en preuve d'origine externe : `upstream_verified` dépend d'une empreinte fournie indépendamment.
- Une reprise gzip/bzip2 implique une relecture jusqu'au checkpoint : ne pas prétendre faire un seek aléatoire rapide.
- Ne pas annoncer une qualification réelle sur Wikidata massif à partir des tests synthétiques.
- Toute évolution de `import-large` doit avoir des tests positifs et négatifs sur les interruptions, les duplications et l'intégrité des publications.
