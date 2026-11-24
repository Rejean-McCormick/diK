## Dernière version : V5.7 / alpha.15 (23 novembre 2026)

- [x] DIK-LEX-1 : matérialisation réelle de 14 dictionnaires lexicaux SQLite candidats, import **complet de l’index EncyK** pour chaque code strict, source en lecture seule et sortie distincte sur D:.
- [x] Conservation des formes, catégories grammaticales, lignes originales et provenance ; reprise transactionnelle, verrou et contrôle de source stable.
- [x] Enquête d’éligibilité et des langues réellement présentes, statut `NO_DATA` explicite, refus des fichiers sources incomplets.
- [x] Bilan partageable expurgé (<1 Mio), sans lexèmes ni chemins locaux.
- [ ] Validation native Windows du corpus EncyK massif ; décompte réel des têtes lexicales, contrôles de l’espace disque.
- [ ] Import de **tous les sens/gloses** depuis archives primaires : EncyK `index-v1` contient des comptes, pas des définitions ; `dik-enrichment-v1` ne couvre qu’un échantillon.
- [ ] Vérification des licences et des empreintes officielles, qualification sémantique, raccordement KQ/KP et publication Framework v11.

Voir [chapitre 65](docs/docs/65_COLLECTION_LOCALE_14_LANGUES_ENCYK_V5_7.md). **Les chiffres 11 188 / 294 364 de couverture canonique restent inchangés.**

## État actuel : diK V5.4 / 1.0.0-alpha.12 (2026-11-23)

- **Implémenté** : adaptateurs de candidats d'identité locaux (`semantic_id`, `external_id`, `namespace`, `identity_status`, `reason`) et d'assertions Wikidata (`wikidata_subject`, `wikidata_property`, listes de candidats sémantiques et `evidence`) issus des profils de champs V5.3 sous Windows.
- **Implémenté** : rapprochement diagnostique des propositions à l'index `(namespace,KQ/KP)→Q/P` déjà accepté ; différences signalées, sans nouvelle approbation ni mot créé.
- **Implémenté** : rapports candidat et rôle non lexical, prise en charge de `empty_source`, export V5.4, reprises contrôlées par SHA et index accepté.
- **Non démontré** : les valeurs des 32 sources JSONL réelles n'ont pas été transmises ; les tests utilisent des valeurs de fixture pour les champs réellement observés. Quatre schémas GF-Wikidata restent inconnus, ainsi que l'activation des droits et les 69 Kristals hors v11.
- **Non modifié** : le dénominateur 57 Kristals évaluables × 14 locales, les ressources sources et les liens canoniques. Voir [62](docs/docs/62_CONNECTEURS_LOCAUX_IDENTITES_ASSERTIONS_V5_4.md).

# diK — État de mise en œuvre (alpha.8, 22 novembre 2026)

**Révision de distribution V4.1 (23 novembre 2026) :** correction du lanceur PS7 et de la vérification des références périmées. Voir [47](docs/docs/47_REVUE_PACK_V4_1.md).

**Le détail historique alpha.6 et ses limites sont conservés ci-dessous.** Version expérimentale actuelle : `1.0.0-alpha.8`, pas une certification du moteur multilingue global.

## Alpha.8 : Source Manager local (effectivement livré)

- [x] `dik sources discover` : reconnaissance ciblée des ressources GF/Wikidata et catalogues v11 présents sur disque, sans réseau, sans modification ni duplication.
- [x] Registre local référentiel horodaté et contrôles `dik sources verify` des empreintes (ou état `found_unhashed` si budget dépassé).
- [x] `dik coverage resolve14 --resource-registry` : sélection des fichiers de catalogue via les pointeurs, suivie des validations Framework déjà existantes.
- [x] `--wikidata-source-id` : sélection **explicite** d'un dump Q/P candidat inventorié ; aucune conversion des JSONL thématiques.
- [x] Détection des deux chemins de portefeuille officiel connus sous `sources_root`, sans prendre archives/copies pour des officiels.
- [ ] Approbation de provenance et licences, mapping GF↔KQ/KP avec preuves, flux L/S/F intégré, relocalisation automatique par digest et évaluabilité des 69 officiels sans ensemble v11.

Voir [44 — Implémentation](docs/docs/44_SOURCE_MANAGER_V4_IMPLEMENTATION.md), [45 — Commandes PS7](docs/docs/45_COMMANDES_V4_WINDOWS.md) et [46 — Validation](docs/docs/46_VALIDATION_ET_LIMITES_V4.md).

---

## Archives de l'état alpha.6 (16 octobre 2026)

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

**Version de ce chapitre historique : alpha.6.** Ne pas baptiser `1.0.0` stable avant levée et preuve des critères ci-dessus.

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

## DIK-LEX-1 (2026-11-04, proposition additive, non ratifiée)

- [x] Inventaire descriptif *discovery_only*, schéma applicatif candidat et contrôles Python hors ligne.
- [x] Seed de 2 flux Wikidata + 1 source Wiktionary candidate, et 7 tags de locales, sans supposer des traductions présentes.
- [x] Tests positifs et négatifs (10 tests), sans toucher aux contrats vendoriés Framework.
- [ ] Ratification humaine de l'ADR; registre mondial IANA BCP 47 versionné; évaluation de licences externes et mesures réelles de couverture.
- [ ] Adaptateurs Wikidata L/S/F et GF, qualification complète DIK-LEX-1 et tests inter-dépôts.

**Cet ajout ne certifie ni un dictionnaire mondial ni une version diK stable.**

## DIK-LEX-1 — index ISO 639-3 de découverte (étape 2, proposition)

- [x] Snapshot local de **7 910 codes candidats** produit par `pycountry 24.6.1`; SHA du fichier et du dataset source consignés.
- [x] Schéma, lecture indépendante de `pycountry`, déterminisme, intégrité, tests négatifs.
- [ ] Autorité IANA versionnée et validation complète BCP 47; mapping alias/langue/script/région CLDR.
- [ ] Révision de licence et gouvernance pour redistribution du référentiel linguistique.
- [ ] Dictionnaires multilingues réellement importés, approuvés ou publiés : **aucun dans cet ajout**.

**Attention : 7 910 codes candidats ≠ 7 910 langues vivantes ≠ 7 910 dictionnaires.**


## DIK-LEX-1 v0.3 — overlay cumulatif mondial candidat (2026-11-04)

- [x] v0.1/v0.2 maintenues : 7 910 codes candidats ISO 639-3 de `pycountry 24.6.1`, manifestes, inventaire source et contrôles.
- [x] Création d'un catalogue **clairsemé** de 7 910 *emplacements non peuplés*, SHA + audit, sans création de 7 910 dictionnaires factices.
- [x] Catalogue de 25 ressources mondiales **à examiner** : 0 licence approuvée, 0 import certifié.
- [x] Parser IANA TXT local + vérificateur conservateur de tags BCP 47, support du statut déprécié, scripts/régions/variantes, téléchargement HTTPS **opt-in** vers hôte IANA verrouillé.
- [x] Réconciliation ISO→IANA dans une sortie immuable auditée, sans créer de KQ/KP, d'`exactMatch` ni de dictionnaire publié.
- [x] Import local streaming de lexèmes Wikidata L/S/F à vocation d'observation, avec SHA, limites de ressources, détection de doublons et compteurs de locales; aucune correction curated automatique.
- [x] Relais lexical **candidat** vers GF, Q grammaticaux explicitement non mappés.
- [ ] Qualification réseau réelle de l'acquisition IANA; registres courants authentifiés et alias CLDR complets.
- [ ] Tests sur dumps lexèmes industriels, compatibilité exacte avec de vraies grammaires GF, licences/qualité des 25 sources, support des claims Wikidata complets.
- [ ] Certification DIK-LEX-1 par les autres dépôts; ratification de l'ADR.

Voir `DIK-LEX-1-README-OVERLAY.md` et `docs/docs/27_*.md`, `28_*.md`, `29_*.md`. Ceci n'est **pas** une release diK 1.0 stable.


## Alpha.9 / V5 — Qualification sans activation (2026-11-23)

- [x] `sources qualify` : une ligne par référence du registre local, vérification SHA et statut/action, identification des copies, des artefacts `.pgf` de tests et des sources à inspecter.
- [x] `resolve14 --observe-qid-lexicon` : observation optionnelle des Q/P déjà acceptés avec `labels[locale]` explicites et SHA inchangé ; résultats candidats séparés, **non ajoutés à la couverture**.
- [x] Chapitres 48–50 et décision ADR-DIK-LEX-4.
- [ ] Qualification des licences et provenance externe, lecture/validation du vrai schéma du JSONL QID du Windows, GF↔KQ/P, Wikidata L/S/F complet, 69 officiels sans v11, tests PS7 natifs.


## V5.2 — État effectif (2026-11-23)

- [x] Inspection locale de `wikidata_thematic_candidate` sous contrôle SHA/taille/racine, avec déduplication, identification des schémas et des conflits, sans interpréter `statements` comme des libellés.
- [x] Observation de libellés Q/P explicites **seulement** si le Q/P est relié à une identité canonique KQ/KP par un crosswalk accepté et audité. CSV séparés, aucun changement des compteurs.
- [x] Qualification QID : codes strictement limités aux 14 locales officielles, statut `lexique_qid_schema_reconnu_non_habilite` distinct de `a_inspecter`.
- [ ] Contenu/schémas des 40 sources thématiques vérifié en conditions réelles sur Windows ; contrôle licences/provenance et activation ratifiée.
- [ ] Import global Wikidata Q/P/L/S/F, alignement GF ↔ KQ/KP et réparation prouvée des 69 Kristals non évaluables.


## Contrat documentaire pour V5.3 — 2026-11-23 (**non implémenté**)

Le dépôt exécuté localement reste au niveau du code V5.2. Le rapport `DIK_V5_2_BILAN_20261123T143508Z.zip` indique 40 sources thématiques (37 inspectées, 3 doublons identiques, 2 tronquées), **0 Q/P reconnu par le lecteur thématique**, 0 observation thématique publiée et 11 188/294 364 couples résolus. La future V5.3 doit d'abord valider le **schéma réel** des JSONL, puis lire de manière progressive et reprenable, avant de conclure à un recoupement ou à son absence. Lire le [chapitre 53](docs/docs/53_DIAGNOSTIC_FACTUEL_V5_2_VERS_V5_3.md) et le [plan 59](docs/docs/59_PLAN_IMPLEMENTATION_TESTS_V5_3.md). Les connecteurs GF/L/S/F et la prise en charge des 69 Kristals non évaluables restent distincts. Aucun changement du programme, des comptes de couverture ou des licences.


## V5.3 alpha.11 — implémenté (diagnostic uniquement)

Profilage de schémas, extraction d’identifiants par rôle, reprise SQLite SHA-256, statuts discriminants, rapports versionnés et CLI conservée. Les schémas réels encore inconnus, l’activation GF/L/S/F et la couverture des 69 Kristals hors v11 restent ouverts. Voir `docs/docs/61_IMPLEMENTATION_EFFECTIVE_V5_3.md`.


## V5.5 alpha.13 — Code livré : tableaux JSON GF-Wikidata

- [x] Adaptateur pour les 4 sources réelles : tableaux JSON malgré le suffixe `.jsonl` (`url`, `labels`, `descriptions`).
- [x] Lecteur streaming de 46 889 entités testées en local, reprise SQLite et SHA, profilage séparé conteneur / schéma.
- [x] `en` et `sv` uniquement pour ce lot parmi les 14 langues officielles ; autres langues sans repli ni traduction.
- [x] Rapprochement QID exact vers les correspondances KQ/KP acceptées ; sortie candidate seulement et aucune augmentation artificielle des totaux.
- [ ] Recoupement sur Windows avec les 1 776 liens acceptés ; validation des droits, publication de ressources, GF morphologique et 69 Kristals non évaluables.

Voir [63](docs/docs/63_ADAPTATEUR_GF_WIKIDATA_TABLEAUX_JSON_V5_5.md).


## V5.6 alpha.14 — Gestionnaire des sources en ligne (réel, mais prudent)

- [x] Liste des fournisseurs en ligne avec URL, droits et degré d'implémentation (`sources online-catalog`).
- [x] Requêtes consenties vers Wikidata Action API pour les Q/P KS-acceptés, batchées, temporisées, sans fallback linguistique.
- [x] Cache des réponses par SHA-256, index et reprise incrémentale, refus des contenus modifiés, aucun remplacement des ressources canoniques.
- [x] Nouvelle observation en ligne candidate dans `resolve14`, compteur potentiel séparé, nouvel export V5.6 expurgé.
- [ ] Consultation HTTP réelle sur Windows et mesure du recoupement avec les liens acceptés.
- [ ] Connecteurs téléchargeables Kaikki/Wiktionary, GF morphologique, Wikidata L/S/F, admission formelle des labels, 69 Kristals non évaluables.

Voir [64](docs/docs/64_SOURCE_MANAGER_EN_LIGNE_CIBLE_WIKIDATA_V5_6.md). **La V5.6 ne fait pas passer les 11 188 résultats historiques à un nombre augmenté sans revue.**

## V5.8 — Fédérer les preuves de sens (candidats uniquement)

Le code `src/dik/semantic_evidence_bridge.py` relie les 14 dictionnaires
V5.7 à la réconciliation EncyK v0.5 et à l'enrichissement v0.6 sans changer
les bases lexicales ni les bases EncyK. Les commandes permettent le plan, la
liaison légère, la consultation de gloses/S externes et un rapport expurgé.
La v0.6 est échantillonnée et non exhaustive. La revue de sens, des SHA
source officiels et des droits reste à accomplir. Aucune correspondance
canonique ou publication, 0 licence approuvée par ce pont.

## V5.10 (2026-11-24) — Suivi des 126 Kristals

**Implémenté** : lecture de `canon/state.index.json` pour chaque Kristal officiel,
indexation des V11 par révision (registres, mots connus, correspondances
Wikidata et preuves déclarées), état des contrats non V11 et artefacts absents.
Extension additive du registre V5.9, profil externe inchangé, 13 langues cibles.

**Non implémenté** : décision contractuelle sur la révision V11 active,
conversion des formats natifs et validation indépendante des nouveaux liens
Wikidata. Les 1 776 liens V5.9 restent seuls admis dans la vue résolutive
jusqu'à examen. Aucune publication automatique.

## V5.11 (2026-11-24) — Statut implémenté, sélection non normative

- [x] Empreintes SHA-256 par index canonique, registry, crosswalk, catalogue et graphe inspectable.
- [x] États de sélection par Kristal : singleton consultable, plusieurs révisions divergentes, équivalentes au niveau des observations, non inspectées et absentes.
- [x] Décision manuelle optionnelle, attachée aux empreintes exactes, pour **vue dérivée uniquement** ; aucune promotion des `accepted` vers la couche globale de diK.
- [x] Recherche Q/P inverse et `(namespace,KQ/KP)` directe sur les révisions sélectionnées, avec refus de clé locale sans namespace.
- [x] Validation des décisions et SHA, tests d'intégration et contrôle du manifeste.
- [ ] Autorité canonique choisie contractuellement par les Kristals multirévisions. Leurs `state.index.json` examinés ne contiennent pas de champ actif déterminant.
- [ ] Qualification de preuves et admission des 12 919 liens source, 49 Kristals non V11, 7 artefacts absents et 7 graphes à inspection différée.
- [ ] Publication et activation des 13 dictionnaires linguistiques et consommateurs SemantiK/Spek.

**Important :** `SINGLE_DECLARED_DERIVED_VIEW` et `OPERATOR_PINNED_DERIVED_VIEW` ne sont ni des validations de sens, ni des autorités Framework, ni des autorisations de publication.
