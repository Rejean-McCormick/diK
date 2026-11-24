# diK — Guide maître : identités, sources locales, 14 langues

**Historique consolidé du pack V4.1 (23 novembre 2026) :** le registre de références locales et la résolution via catalogues v11 audités sont implémentés. Les chapitres **44–47** décrivent le code et sa revue actuelle ; les chapitres 34–43 conservent aussi les étapes historiques et la cible non encore réalisée.

> **État actualisé au 23 novembre 2026 :** les chapitres 53–60 retracent la spécification ; V5.3 est implémentée au chapitre 61 et V5.4 au [chapitre 62](docs/62_CONNECTEURS_LOCAUX_IDENTITES_ASSERTIONS_V5_4.md). Les paragraphes historiques ci-dessous conservent leur date.
>
> **Principe** : diK ne traduit jamais une langue dans une autre. Il recherche une forme linguistique pour la clé canonique `(namespace_id, KQ/KP, locale)` en utilisant des catalogues autorisés, des références externes revues et des ressources grammaticales qualifiées. La langue de départ n'existe pas dans ce contrat.

## Lire ce guide en premier

1. [34 — Identité → forme, sans traduction](docs/34_IDENTITE_VERS_FORME_SANS_TRADUCTION.md) : contrat fonctionnel et états de preuve.
2. [35 — Localiser avant de connecter](docs/35_CARTE_DES_RESSOURCES_LOCALES.md) : chemins réels *déclarés* par Spek et les index transmis, avec niveau de confiance.
3. [36 — Registre des sources](docs/36_SOURCE_MANAGER_LOCAL_ET_REFERENCES.md) : découverte non destructive, manifests, SHA, formats, sécurité.
4. [37 — Adaptateurs Wikidata et GF](docs/37_CONNECTEURS_WIKIDATA_GF.md) : pourquoi Q/P, L/S/F et fonctions GF ne sont pas interchangeables.
5. [38 — Portefeuille 126 × 14](docs/38_AUDIT_126_KRISTALS_14_LANGUES.md) : sélection canonique, métriques exactes et résultats observés.
6. [39 — Interop Spek/Konstellation](docs/39_INTEROPERABILITE_SPEK_KONSTELLATION.md) : frontières et contrats de lecture.
7. [40 — Sécurité & gouvernance](docs/40_SECURITE_DROITS_PROVENANCE.md) : licence, localité, absence de mutations.
8. [41 — Plan d'implémentation vérifiable](docs/41_FEUILLE_DE_ROUTE_LOCALISATION_ET_TESTS.md) : travaux non implémentés et critères d'acceptation.
9. [42 — Exploitation Windows PS7](docs/42_EXPLOITATION_WINDOWS_PS7.md) : procédures et journalisation.
10. [43 — Preuves et interprétation](docs/43_PREUVES_STATUTS_ET_LIMITES.md) : observations / candidats / acceptés / refusés.
11. [ADR DIK-LEX-2](decisions/ADR-DIK-LEX-2-localiser-et-referencer.md) : décision documentaire proposée (pas une approbation canonique).
12. [Modèles de manifestes non normatifs](examples/resource-locator/README.md) : exemples *non activés* destinés aux futurs adaptateurs.

### Ce qui existe dans le code observé

- diK (snapshot du 21 novembre) : couches v11, audit, moteur de sélection, imports Wikidata locaux, observations lexicales Wikidata L/S/F, handoff GF **candidat**.
- diK V3 livré ensuite : `dik coverage resolve14` sélectionne les sous-dossiers officiels avec `kristal.discovery.json`, puis audite les couches v11 sélectionnées et certains catalogues raccordables. Le rapport d'exécution du **23 novembre 2026 UTC** (22 novembre en heure de Toronto) indique `etat=PARTIEL`, pas une couverture totale.
- Les fichiers GF repérés dans les *index seulement* ne sont **pas** automatiquement des entrées diK utilisables. Aucun mapping `(namespace,KQ/KP) -> fonction GF` n'est présumé.

### Ce qui ne marche PAS encore automatiquement (état V4.1)

Le Source Manager **découvre déjà les racines ciblées et enregistre les références** ; en revanche, la découverte de toutes les racines inconnues, l'admission des ressources GF en lexique KQ/KP, le chargement sans sélection explicite d'un dump Wikidata Q/P global, la résolution prouvée des 126 Kristals et la qualification linguistique globale restent non terminés. Une ressource repérée ne vaut pas correspondance sémantique acceptée.

### Autorité, priorité, et compatibilité documentaire

Les schémas et validateurs du Kristal Framework ont priorité sur les exemples diK. Les documents `docs/docs/01..31` et `docs/README.md` contiennent des éléments historiques, dont certains décrivent un produit futur ; cette mise à jour les complète sans réécrire rétroactivement le passé. Les chapitres 32–33 décrivent des scanners V2/V3 ; 34–43 fixent les limites et le programme **sans présumer que la connexion est achevée**. En cas de conflit, confronter le code installé, les manifestes du Framework et les preuves du scan.

**Périmètre du pack V4.1 actuel** : mise à jour versionnée du **code diK et de la documentation**, sans modification des Kristals, des dictionnaires, des dépôts GF, de Git ou de Render. L'installateur n'applique que les fichiers de son manifeste et conserve les autres fichiers du dépôt local.

## Rectificatif d'implémentation V4 (alpha.8)

La livraison documentaire DIK-DOCS-LOCAL-1 décrivait une **cible**. Depuis ce correctif moteur, la découverte ciblée et la persistance d'un registre de références sont **implémentées**, tandis que l'activation de ressources GF et le mapping GF↔KQ restent **non implémentés**. Voir [44](docs/44_SOURCE_MANAGER_V4_IMPLEMENTATION.md), [45](docs/45_COMMANDES_V4_WINDOWS.md), [46](docs/46_VALIDATION_ET_LIMITES_V4.md) et [ADR-DIK-LEX-3](decisions/ADR-DIK-LEX-3-local-source-registry-v4.md). Les chapitres précédents conservent leur contexte historique.

**Revue de la distribution :** [47 — Paquet V4.1 audité, corrections et limites](docs/47_REVUE_PACK_V4_1.md).


## Mise à jour V5 — qualifier avant de pointer

Le registre local des sources est désormais analysable par `dik sources qualify`. Les observations QID explicitement liées par un `exactMatch accepted` peuvent être enregistrées avec `--observe-qid-lexicon`, mais restent **candidates** et n’augmentent pas la couverture. Voir [48](docs/48_QUALIFICATION_SOURCES_REELLES_V5.md), [49](docs/49_OBSERVATIONS_QID_ET_LIMITES_GF_V5.md) et [50](docs/50_FEUILLE_DE_ROUTE_DIAGNOSTIC_REGISTRE_V5.md).


## Contrat documentaire V5.3 — Lecture Wikidata par schéma, sans traduction (2026-11-23)

Le bilan **V5.2 exécuté sur Windows** confirme 126 Kristals officiels (57 évaluables, 69 non évaluables), 5 269 références locales et 40 sources Wikidata thématiques. Le lecteur V5.2 a examiné 37 sources, ignoré trois copies identiques, tronqué City/University à 150 000 lignes chacune et reconnu zéro Q/P. **Cela ne prouve pas une absence de Q/P dans ces fichiers : leur schéma réel n'a pas été établi à partir du bilan.**

Le nouveau système est **décrit mais non codé** dans [53 — état et limites](docs/53_DIAGNOSTIC_FACTUEL_V5_2_VERS_V5_3.md), [54 — architecture](docs/54_ARCHITECTURE_LECTURE_WIKIDATA_V5_3.md), [55 — adaptateurs](docs/55_CONTRATS_SCHEMAS_JSONL_V5_3.md), [56 — reprise](docs/56_STREAMING_REPRISE_SECURITE_V5_3.md), [57 — preuves](docs/57_PREUVES_KQ_QP_LSF_GF_V5_3.md), [58 — statuts/rapports](docs/58_STATUTS_ET_RAPPORTS_V5_3.md), [59 — plan de code](docs/59_PLAN_IMPLEMENTATION_TESTS_V5_3.md), [60 — frontières](docs/60_FRONTIERES_GF_ET_KRISTALS_NON_EVALUABLES.md) et [ADR 6 proposée](decisions/ADR-DIK-LEX-6-lecteurs-schemas-reprise-sans-activation.md).

Cette étape **ne change ni le code V5.2, ni ses CLI, ni les dictionnaires**. Les futurs champs/sorties/états sont des contrats de conception. Le prochain développement devra d'abord tester les vrais enregistrements locaux, puis rendre explicites les scans complets/partiels, sans jamais créer d'identité par ressemblance des mots.


## Implémentation V5.3 (alpha.11)

La documentation de conception 53–60 est maintenant accompagnée du [chapitre 61 — état réellement livré](docs/61_IMPLEMENTATION_EFFECTIVE_V5_3.md). Les schémas non reconnus des JSONL réels restent explicitement à qualifier ; aucun droit ni rapprochement sémantique n’est inventé.


## Implémentation V5.4 (alpha.12)

Les adaptateurs d’**identités candidates** et d’**assertions Wikidata** répondent aux champs réellement relevés dans le bilan V5.3 ; les valeurs des sources n’étant pas disponibles ici, ils sont testés sur des fixtures synthétiques, puis destinés à une validation Windows. Aucune source n’est autorisée automatiquement. Voir [62 — connecteurs locaux](docs/62_CONNECTEURS_LOCAUX_IDENTITES_ASSERTIONS_V5_4.md).


## Implémentation V5.5 (alpha.13) — GF-Wikidata : vrais tableaux JSON

Les quatre fichiers `City`, `University`, `Country` et `Part_of world` fournis sont des **tableaux JSON multiligne malgré leur extension `.jsonl`**. Le lecteur V5.5 les traite objet par objet, avec checkpoints et identifiants `url` vérifiés. Il produit uniquement des rapprochements **candidats** vers les Q/P déjà acceptés, dans les locales explicites `en` et `sv` pour ce lot. Voir [63 — formats réels et validation](docs/63_ADAPTATEUR_GF_WIKIDATA_TABLEAUX_JSON_V5_5.md).


## V5.6 — Gestionnaire local ET en ligne

Le Source Manager interroge désormais, sur consentement explicite, l'API officielle Wikidata en ciblant les Q/P **déjà acceptés et vérifiés**. Les données récupérées sont conservées sous `diK/reports/sources/online`, empreintées et rapprochées seulement par identité : aucune traduction ni repli de langue. Elles restent des **observations candidates** séparées des formes publiées. Kaikki/Wiktionary et GF-RGL en ligne sont catalogués avec leurs droits respectifs mais ne sont pas importés en V5.6. Voir [64](docs/64_SOURCE_MANAGER_EN_LIGNE_CIBLE_WIKIDATA_V5_6.md) et les commandes dans ce chapitre.


## V5.7 — Du catalogue mondial aux 14 dictionnaires réellement matérialisés

La commande `dik world local-build14` importe l’intégralité des observations
éligibles indexées par EncyK et crée 14 SQLite indépendants sur D:, avec source
EncyK en lecture seule et aucune consultation Internet. Le catalogue
mondial DIK-LEX-1 reste le cadre architectural ; l’import ne crée aucun KQ/KP.
Voir [65](docs/65_COLLECTION_LOCALE_14_LANGUES_ENCYK_V5_7.md).

## Pont EncyK V5.8

Pour les dictionnaires candidats construits en V5.7, utiliser désormais
`dik world local-semantic-plan14`, puis `local-semantic-bind14` et
`local-semantic-lookup`. Les bases EncyK restent intactes. La liaison v0.5/v0.6
par clé homographe n'est jamais une équivalence KQ/KP.
Voir le chapitre `docs/docs/66_PONT_ENCYK_PREUVES_DE_SENS_V5_8.md`.
