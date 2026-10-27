# 10 — Stockage, index et caches

## OPS-010 — Autorité

La source de vérité est le **catalogue de fichiers versionnés** et les documents Framework signés/empreintés selon leur profil. SQLite est un index dérivé **reconstructible**, pas un registre KQ autonome. L'instance peut être détruite puis reconstruite à partir d'un manifeste publié et de ses shards.

## OPS-011 — Structure proposée

```text
workspace/
  projects/           # références à graphes/catalogues, non copies massives obligatoires
  manifests/          # pointeurs de révisions publiées
  snapshots/          # objets immuables de dictionnaires/crosswalks/lexiques
  curated/            # nouvelles révisions revues
  staging/            # zone de travail non publiée, nettoyable
  indexes/            # sqlite/fts reconstructibles et cache
  jobs/               # checkpoints sans autorité sémantique
  audits/             # décisions et preuves/manifestes
```

Toutes les écritures sont contenues dans un `workspace_root` sûr ; pas de `../`, symlinks dangereux ou chemins absolus dans les manifestes importés.

## OPS-012 — Index logique (dérivé)

Tables proposées : `active_manifest`, `semantic_key(namespace,id,kind)`, `lexeme(namespace,id,locale,domain,layer,priority,term,aliases,status)`, `reverse_terms(locale,normalized_term,namespace,id,kind,context)`, `external_mapping(namespace,id,system,external_id,relation,status,decision)`, `snapshot(hash,source,version)`, `job_checkpoint`, `audit_decision`. Indexer `locale + normalized_term + kind` et `namespace+id+locale`, pas une table de 300 colonnes. FTS utile pour suggestions, sans rôle de preuve d'identité.

## OPS-013 — MVCC / cohérence

Le lecteur fixe une révision complète de manifeste au début ; les jobs peuvent préparer une autre révision sans changer les données vues. Un pointer swap atomique rend la nouvelle version visible après validation. Caches clés : `(manifest_digest, namespace, KQ/KP, locale, domain, resolution_profile)` ; invalider par changement de digest, pas via TTL qui pourrait masquer une publication.

## OPS-014 — Tâches et transactions

Une mise à jour publie son catalogue et ses shards ensemble, jamais un par un visibles. Crash avant commit : ancien pointeur inchangé. Crash après commit : manifeste vérifié, index peut être reconstruit. Aucun état `partial-success` silencieux à une API qui annonce réussite.

## OPS-015 — Efficacité

Chargement par lots/shards, streaming, réutilisation des parseurs/index, mémoire plafonnée, index réparables ; comparaison incrémentale des hashes de shards ; limiter l'audit complet quotidien en préférant audit incrémental + audit intégral périodique au lancement d'une release.
