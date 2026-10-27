# 21 — Taxonomie d'erreurs, audit et observabilité

## Codes d'erreur stables (cibles)

- `DIK_ID_INVALID` : type ou namespace d'ID invalide.
- `DIK_CONTRACT_MISMATCH` : schéma Framework ou profil de projection incompatible.
- `DIK_LEX_MISSING`, `DIK_LEX_CONFLICT`, `DIK_LOCALE_UNKNOWN`, `DIK_FALLBACK_CYCLE`.
- `DIK_XW_NOT_APPROVED`, `DIK_XW_CONFLICT`, `DIK_EVIDENCE_MISSING`.
- `DIK_PROJECTION_NOT_REVERSIBLE`, `DIK_PROJECTION_TAMPERED`, `DIK_ORIGIN_NOT_AUTHENTICATED`.
- `DIK_MIG_ROLE_UNKNOWN`, `DIK_MIG_SOURCE_CHANGED`, `DIK_MIG_APPROVAL_REQUIRED`.
- `DIK_SOURCE_UNAVAILABLE`, `DIK_IMPORT_INTERRUPTED`, `DIK_QUOTA_EXCEEDED`.
- `DIK_IDEMPOTENCY_CONFLICT`, `DIK_REVISION_CONFLICT`, `DIK_STORAGE_CORRUPT`.

Les messages humains peuvent être traduits sans changer le code machine. Les appels API doivent retourner le rôle du champ, chemin/pointeur pertinent et remédiation recommandée, sans exposer données secrètes ou dumps entiers dans les logs.

## Traçabilité minimum

`request_id/job_id`, command/version, namespace, hash manifeste, source snapshot, number examined/accepted/missing/conflicted, temps CPU/IO, cache hit, état des transitions et sortie SHA. **Ne pas logger automatiquement les contenus textuels complets**, ni les documents d'utilisateur ; exporter une preuve explicite à la demande.

## Audit de décisions

Journal append-only : qui/quoi/quand, rôle, source/avant/après, motif, preuves, hash de plan, version registre/crosswalk/catégorie lexicale, éventuelle supersession. Distinguer prévisualisation de publication. La présence d'un hash n'est pas une signature d'approbation.

## Observabilité sans serveur imposé

CLI affiche progression stable et sauvegarde logs structurés locaux ; interface suit les jobs et états partiels ; exporter métadonnées sans identités privées si l'utilisateur le veut. Aucune télémétrie réseau requise ou activée silencieusement.
