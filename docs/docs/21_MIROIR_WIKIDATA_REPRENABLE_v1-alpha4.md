# diK alpha.4 — Miroir Wikidata et comparaison de snapshots

**Statut : implémentation alpha, contrats applicatifs candidats.** Ni l'identité sémantique ni les contrats du Framework v11.0.0-draft.3 ne sont modifiés.

## Règles impératives

1. `KQ/KP` sont les identités Kristal. `Q/P` restent externes. Un libellé téléchargé ne prouve jamais une équivalence ; seules les correspondances `accepted + exactMatch` validées par le Framework donnent accès à l'import vérifié.
2. Le téléchargement est une tâche explicite ; il n'y a **aucune connexion réseau** pendant `lookup`, la restauration de projection, la couverture ou le lancement de diK.
3. L'import du miroir exige une empreinte SHA-256 **approuvée indépendamment** du manifeste du téléchargement. La comparaison de cette empreinte avec les octets prouve leur conformité à la valeur approuvée, mais **pas** à elle seule l'origine du hachage ou l'authenticité du serveur.
4. Aucun dump, catalogue, dictionnaire corrigé, registre ou Kristal n'est modifié. Les imports et rapports créent des snapshots séparés. Pas d'adoption automatique.
5. Les vues et différences reflètent des **observations lexicales**. `label_changed`, `removed` et `external_id_changed` ne fusionnent aucun KQ.

## Télécharger (explicite)

```bash
# L'URL est un exemple officiel ; choisir un snapshot daté et épingler son SHA-256.
dik sync fetch \
  --url https://dumps.wikimedia.org/wikidatawiki/entities/latest-all.json.bz2 \
  --root /data/dik-mirrors \
  --snapshot wd-2026-10-16 \
  --sha256 VOTRE_EMPREINTE_AMONT_APPROUVEE
```

L'outil autorise uniquement HTTPS sur `dumps.wikimedia.org`, pour les répertoires Wikidata reconnus. Il enregistre un `.part`, un ETag fort ou `Last-Modified` disponible, et tente une reprise avec `Range` + `If-Range`. Une réponse partielle incohérente est refusée. Les téléchargements sans empreinte sont marqués `upstream_verified: false`, et restent impropres au parcours d'import vérifié.

- Les URL `latest-*` peuvent évoluer : le hash approuvé empêche de traiter silencieusement de nouveaux octets comme l'ancien snapshot.
- Si aucun validateur de ressource n'existe, **la reprise est refusée** ; l'opérateur doit recommencer une acquisition sûre.
- Les caches, backups et miroirs tiers ne sont pas automatiquement fiables ; la validation du SHA doit avoir une origine indépendante et approuvée.
- Le fichier complet peut être énorme. La commande possède une limite de taille configurable `--max-bytes` et un délai réseau `--timeout`. Aucun dump officiel massif n'a été téléchargé ni benchmarké dans les tests alpha.4.
- En cas de crash, le fichier `.part` et `transfer.json` restent disponibles. Un verrou `.lock-<snapshot>` protège la concurrence ; un verrou laissé par un crash exige un examen humain avant retrait. Aucune suppression automatique d'un verrou ancien.

## Importer un miroir vérifié

```bash
dik sync import-mirror \
  --manifest /data/dik-mirrors/wd-2026-10-16/mirror.json \
  --sha256 VOTRE_EMPREINTE_AMONT_APPROUVEE \
  --crosswalk /data/project/external-crosswalk.json \
  --registry /data/project/identity-registry.json \
  --namespace mon-namespace \
  --locales fr,en,fr-CA \
  --root /data/dik-imports
```

Cette commande vérifie l'empreinte à nouveau, puis utilise `sync import-local` existant : sortie immuable, clé idempotente et audit Framework. Les dictionnaires humains ne sont pas touchés. Les fichiers de transfert ne sont pas placés dans les graphes canoniques.

Le chemin `sync import-local` permet toujours d'utiliser sa propre copie de Wikidata hors ligne sans téléchargement par diK. La garantie de hachage du **nouveau parcours `import-mirror`** ne s'étend pas implicitement à tous les imports locaux historiques.

## Comparer les observations Wikidata entre deux snapshots

```bash
dik sync diff \
  --before /data/dik-imports/ancien/catalog.json \
  --after /data/dik-imports/nouveau/catalog.json \
  --crosswalk /data/project/external-crosswalk.json \
  --registry /data/project/identity-registry.json \
  --sample-limit 25 \
  --events /data/rapports/wikidata-diff.jsonl
```

La comparaison vérifie les catalogues et leurs couches contre le Framework, utilise un **merge en flux** des fichiers JSONL triés par identifiant, compte tous les changements et conserve au plus 25 exemples en mémoire. Avec `--events`, elle publie un journal JSONL complet de façon exclusive et atomique, sans le mélanger avec les catalogues.

Types : `added`, `removed`, `label_changed`, `aliases_changed`, `description_changed`, `multiple_fields_changed`, `external_id_changed` et, sur demande, `revision_only` (`--revision-only`). Tous les changements lexicaux sont marqués à revoir ; `revision_only` n'implique pas d'approbation.

### Cas non couverts en alpha.4

- Téléchargement de l'export incrémental : son format n'est **pas** automatiquement traité comme un dump d'entités complet ; seul un JSON d'entités valide passe l'import existant.
- Gestion sémantique des redirections, fusions et scissions Wikidata : elles demandent un adaptateur explicite, un statut `superseded` ou une décision documentée ; aucun KQ n'est fusionné automatiquement.
- Reprise au milieu d'un import `.bz2` monolithique : la reprise HTTP porte sur les octets transférés, **pas** sur l'analyse sémantique en cours.
- Auto-synchronisation planifiée, signature d'origine de la liste de checksums, benchmark massif 300 langues, quota global d'espace disque et implémentation multi-hôtes.
- Adoption automatique du nouveau lexique dans un Kristal actif : volontairement interdite.

## Tests alpha.4

Tests sans réseau externe : transfert simulé interrompu puis repris avec `Content-Range`, rejet de changements d'ETag, réponse 200 au lieu de 206, faibles validateurs, checksum incorrect, quota, exclusion des hôtes inattendus, verrou concurrent, récupération du staging, import vérifié et idempotent, comparaison de libellés/alias/retraits/révisions, et compatibilité des 64 tests antérieurs.

### Limite mémoire à mesurer

La comparaison des fichiers JSONL proprement dite conserve un nombre borné d'exemples, mais l'**audit Framework préalable** vérifie les identifiants et les priorités et utilise des structures mémoire proportionnelles au nombre d'entrées. Une empreinte contrôlée et un tri par identifiant ne sont donc pas encore une preuve de mémoire constante pour un catalogue Wikidata massif. Le TCK de charge et la future indexation de validation doivent quantifier cette limite avant la version stable.
