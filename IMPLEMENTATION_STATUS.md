# diK 1.0.0-alpha.6 — État de mise en œuvre (16 octobre 2026)

## Exécuté et vérifié dans cette livraison

- Capacités historiques v0.3 : projet v11, audit dictionnaires, import Wikidata local en flux, couverture, projections compact/verbose, restaurations sans recherche inverse.
- Nouveaux modules : index SQLite dérivé/reconstructible, recherche inverse exacte NFC, proposition de candidats sans approbation.
- Curation : publication de nouveaux catalogues avec couches revues, fichiers sources non réécrits.
- Gouvernance : journal de décisions append-only à hashes chaînés, contrôle du schéma candidat, intégrité et idempotence locale.
- Crosswalk : génération de **nouvelle** révision à partir des décisions attestées; vérification Framework, détection de collisions.
- Migration : plans non exécutables fondés sur des rôles JSON Pointer explicitement fournis ; vérification de source.
- Patch : validation d'intentions sans modification du canon.
- Portefeuille : rapports de complétude regroupés par namespace/catalog, sans fusion non fondée.
- Imports : réutilisation de snapshot identique via clé dérivée SHA-256, réparation du sidecar après crash de publication.
- Interface : atelier local guidé (concepts, couverture paginée, lecture et export réversible), API lecture seule; curation lexicale opt-in non destructive sur workspace distinct, protégée contre la CSRF.
- Compatibilité tests historiques v0.3.

## NON TERMINÉ / ne pas annoncer comme fonctionnalité de production

1. L’atelier graphique effectue une correction lexicale isolée, mais la **conciliation et l’approbation multi-acteur authentifiée** ne sont pas terminées. Les nouveaux catalogues ne sont pas adoptés automatiquement.
2. Authentification forte, signatures, audit cryptographiquement authentifié : les noms de réviseurs sont pour l'instant déclaratifs.
3. Acquisition HTTPS officielle maintenant disponible avec reprise Range + ETag/Last-Modified, quota et hash. **Non qualifiés** : signatures/authenticité de checksum, synchronisation automatisée des deltas, redirections, fusions/scissions et téléchargement réel massif.
4. Reprise au niveau des fragments vérifiables sur dumps massifs compressés. Un redémarrage d'import repart du début si non publié.
5. Moteur de désambiguïsation avancé avec typage contextuel, scores explicables et revue des alias homonymes. La recherche inverse est exacte NFC.
6. Intégration transactionnelle de *publication* de nouveaux Kristals par Authoring Kit, tests complets Authoring + Integration Pack en environnement cible.
7. TCK intégral : les 30 scénarios et 87 exigences positives/négatives n'ont pas tous été exécutés sur ce logiciel.
8. Benchmarks de masse, corpus réels, index millions d'entités, budgets P95 validés sur machine de référence, couverture 300 langues réelle.
9. Qualification stricte contre toutes les sources épinglées et ratification humaine des décisions produit en attente.
10. Installer/distribuer un service durci, multitenant, collaboration réseau ou récupération d'un journal interrompu après écriture partielle.

**Version réellement livrée : alpha.6.** Ne pas baptiser `1.0.0` stable avant levée et preuve des critères ci-dessus.

## Limites de l’interface alpha.2

Le rendu web n’est pas qualifié sur des volumes industriels; la couverture est paginée (25 langues/requête). Sans index fourni par la CLI, la recherche lexicale n’est pas disponible. Les modifications graphiques sont des propositions locales, sans authentification forte ni déploiement réseau.

## Ajouts alpha.3

- Conciliation en lecture seule (`competing_preferred`, `shared_term`) et provenances détaillées.
- File pré-calculée dans l'index, pagination, isolation namespace/langue/famille, affichage au niveau des concepts et API JSON.
- Les décisions acceptées et l'authentification des réviseurs **ne sont pas ajoutées** : les conflits restent à examiner, jamais automatiquement résolus.
- Les index SQLite créés avec alpha.2 restent valables pour la recherche inverse, mais **doivent être reconstruits** pour les nouvelles commandes de conciliation.


## Ajouts alpha.4

- Téléchargement explicite en streaming et publication immuable après contrôle de SHA-256 (si approuvé) ; transit `.part` et reprise HTTP gardée par validateurs.
- Conversion de transfert en import vérifié uniquement si un SHA-256 indépendant est fourni à `sync import-mirror`.
- Comparateur d'observations Wikidata `sync diff` avec audit Framework de chaque catalogue, échantillons bornés et flux JSONL complet optionnel.
- Tous les contrôles sont hors ligne dans les tests ; aucun test réel sur la taille complète Wikidata n'a été effectué.


## Ajouts alpha.5

- Analyse déterministe en lecture seule de redirections Q/P, retraits et scissions candidates à partir d'un JSONL normalisé avec provenance déclarée.
- Détection de cycles et conflits de cibles externes vers deux KQ/KP distincts.
- Rapport d'impact borné plus flux JSONL complet optionnel ; empreintes et conservation des entrées.
- Aucun traducteur automatique des formats de redirect officiels de Wikidata ni adoption de nouvelles correspondances.


## Ajouts alpha.6

- Adaptateur réel `query.redirects` de MediaWiki Action API : extraction JSON/JSONL, provenance liée à l’empreinte, sortie atomique, vérification d’intégrité optionnelle par hash approuvé.
- Consultation HTTPS ciblée de `www.wikidata.org/w/api.php` : seules les entrées approuvées Q/P sont interrogées ; quotas explicites, contrôle des redirects/URL, agent identifié, absence de requêtes implicites.
- Contrôle des erreurs/malformations, des sources non interrogées et des collisions de Q/P. Le résultat alimente `sync evolution` sans modifier les KQ, KP ou crosswalk.
- **Non inclus :** parseur général des `redirect.sql.gz`, flux RDF complet, ingestion directe des dumps incrémentaux, reprise de millions de redirections, test d’API Wikidata réel ou authentification multi-acteur.

## Alpha.7 (ajout)

- [x] Nouveau chemin d'import local avec SQLite, checkpoints transactionnels, JSON(L)/gzip/bzip2, et publication immuable.
- [x] Compatibilité des sorties avec les schémas Framework v11 et l'importeur historique sur fixtures.
- [x] Attestation de source distinguée d'un hash local ; aucun KQ créé ou fusionné.
- [ ] Validation de plusieurs centaines de Go de dump réel et des empreintes officielles.
- [ ] Indexation disque du registre/crosswalk lorsque des millions de correspondances sont approuvées.
- [ ] Traitement complet des deltas Wikidata et service de réconciliation industrialisé.
- [ ] Authentification, workflow d'approbation complet et publication contrôlée des migrations.
