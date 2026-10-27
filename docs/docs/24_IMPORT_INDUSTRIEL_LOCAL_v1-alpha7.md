# diK alpha.7 — Import industriel local (contrat candidat)

## Périmètre

Le nouveau chemin `dik sync import-large` traite les dumps JSON de Wikidata, y compris les tableaux JSON **avec un objet par ligne** (`.json`, `.json.gz`, `.json.bz2`) et les fichiers JSONL (`.jsonl`). Il réutilise exclusivement les correspondances `exactMatch` KQ↔Q ou KP↔P **acceptées** dans le registre du Framework v11 draft.3. Les KQ/KP, le registre, le crosswalk et le dump source ne sont jamais modifiés.

Il complète, mais **ne remplace pas**, `sync import-local` et `sync import-mirror`.

## Exécution

```bash
# En utilisant ta copie Wikidata locale :
dik sync import-large \
  --dump /miroirs/wikidata-20261016-all.json.bz2 \
  --crosswalk /projet/external-crosswalk.json \
  --registry /projet/identity-registry.json \
  --namespace mon.espace/kristal \
  --snapshot 2026-10-16 \
  --locales fr,en,fr-CA \
  --root /miroirs/imports-dik \
  --batch-lines 5000
```

Pour déclarer la source authentifiée, fournir `--approved-sha256 <empreinte obtenue indépendamment>` : la simple empreinte calculée par diK sur son propre fichier **n'atteste pas** l'origine Wikidata.

## Sécurité et déterminisme

- Chaque opération dépend des empreintes **source, crosswalk et registre**, du namespace, du snapshot, des langues (dans l'ordre choisi) et de la version de transformation.
- Aucune identité locale n'est attribuée ou fusionnée pendant l'import.
- Seuls les éléments Wikidata dotés d'une équivalence exacte déjà acceptée produisent des entrées.
- Les enregistrements sont validés avec le schéma lexical officiel Framework v11 draft.3, avant l'insertion SQLite.
- Le répertoire publié porte une clé de contenu et n'est jamais remplacé ; les couches ont des SHA-256 et un `catalog.json` validé.
- La publication via renommage de répertoire intervient **après** finalisation des sorties. Une reprise après une panne pendant cette phase reconstruit les fichiers depuis l'index SQLite scellé.
- Les identités, propriétés, libellés et correspondances restent trois notions séparées.

## Reprise d'import

Les écritures sont enregistrées dans `progress.sqlite` avec un checkpoint dans **la même transaction** que les enregistrements. Un groupe non validé est rejoué après interruption, sans créer de doublon. Par défaut, une transaction couvre jusqu'à 5 000 lignes du dump ; `--batch-lines` ajuste ce compromis entre I/O et reprise.

- **JSON/JSONL non comprimé** : reprise à l'offset octet conservé dans SQLite, après vérification SHA-256 du dump et des entrées.
- **gzip / bzip2** : la reprise n'effectue pas de seek arbitraire ; elle **re-décompresse depuis le début pour ignorer les lignes déjà validées**, puis poursuit. Ce comportement est correct mais peut être lent sur un dump énorme. Aucun prétendu seek rapide dans une archive compressée.
- Un import terminé de façon valide est retourné comme `already_published` après revérification des empreintes.
- Un dump tronqué, une ligne surdimensionnée ou une entrée dupliquée provoquent un **échec**, jamais une publication partielle.
- Après un arrêt *brutal* du processus, un fichier `.lock-large-*` peut subsister. Vérifier qu'aucun processus n'utilise ce snapshot avant de supprimer manuellement le verrou. **Ne jamais supprimer un verrou actif**.

## Coût mémoire et stockage

Les entités sont lues une ligne à la fois et seuls les KQ/KP déjà appariés sont indexés en SQLite. La mémoire n'est donc pas proportionnelle au nombre total d'entités du dump ; elle dépend néanmoins de la taille du registre/crosswalk et de la **plus grande ligne**, limitée par `--max-line-bytes` (128 Mio par défaut). Les index et les données de reprise consomment du disque. Le nombre de langues est libre en pratique, sous réserve de ressources et de tags valides.

**Attention :** une très grande liste de KQ approuvés reste encore chargée en mémoire ; ce module n'est donc **pas** une preuve de mémoire constante à l'échelle de tous les Wikidata Q. Il faudra indexer aussi le crosswalk sur disque si cet ensemble devient trop important.

## Vérifications et limites

- La conformité fonctionnelle est testée contre l'importeur v11 historique (mêmes catalogues et octets de couches sur les fixtures couvertes).
- Des tests injectent une interruption après checkpoint, valident la reprise sur JSON, JSONL, gzip, bzip2, 301 tags déclarés, un dump modifié, un doublon, une corruption publiée et un verrou.
- Benchmark synthétique : 50 000 entités, 4,3 Mo de JSONL, 1 seule correspondance acceptée et 2 langues : environ **1,80 s**, pic RSS **121 Mo** dans cet environnement de test. **Ce n'est pas** un benchmark d'un dump Wikidata complet.
- Pas de parsing natif des dumps incrémentaux (Add/Change), de redirections massives ou de fusion automatique de crosswalk.
- Pas de qualification sur le dump Wikidata réel de plusieurs dizaines de gigaoctets, ni d'authentification/autorisation multi-utilisateur.
- La normalisation complète des tags BCP47/IANA/CLDR n'est pas encore finalisée ; le Framework applique actuellement une validation syntaxique.
- Aucun résultat d'import ne doit devenir canonique dans un Kristal sans les contrôles du Framework et de l'Authoring Kit.

## Critères de passage à la version stable

1. Tests sur dump Wikidata réel et sur forte densité de correspondances acceptées ; pics mémoire, disque et temps mesurés.
2. Reprise après arrêt brutal, panne disque et coupure secteur sur les plateformes ciblées ; verrouillage portable et récupération opérationnelle qualifiés.
3. Validation indépendante du pipeline de gros imports et des dépendances Framework v11 stables.
4. Support complet des deltas/redirects et des migrations revues, sans changement silencieux de KQ.
5. Couverture des exigences TCK 1.0, intégration à l'Authoring Kit et gouvernance des approbations.
