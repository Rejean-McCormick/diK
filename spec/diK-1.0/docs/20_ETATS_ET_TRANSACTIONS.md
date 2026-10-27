# 20 — Machines d'états, transactions et opérations idempotentes

## Décision de correspondance

`proposed -> in_review -> accepted | rejected`; `accepted/rejected -> superseded` seulement avec nouvelle décision référencée. `accepted` exige reviewer + méthode + preuve KS + unicité des `exactMatch`. Les décisions rejetées restent auditées.

## Import

`planned -> downloading? -> parsing -> staging -> validating -> ready -> published` ; de n'importe quel état prépublication : `failed|cancelled`, avec rollback du staging et reprise conditionnelle. Un manifest publié ne revient pas à editing : publier une révision supérieure. État `published` = tous shards/hashes accessibles et le pointeur atomique actif.

## Migration

`inventory -> proposed -> reviewed -> approved_for_submission -> producer_verified -> new_revision_published`. Aucun saut de `proposed` vers publication ; `approved` par une IA sans rôle vérifié invalide. Une modification de la source ou du plan retire l'autorisation précédente.

## Opération sûre

Chaque commande mutante stocke `idempotency_key`, hash entrée, version outils, statut, résultat/digest et journal d'étapes. En cas d'exécution répétée : même clé+même hash => replay du résultat ; clé égale/hash différent => erreur ; tentative concurrente => une seule publication, les autres détectent conflit. Stockage transactionnel local et atomic rename à l'étape d'activation.

## Exception/corruption

Si un artefact publié est corrompu, ne jamais corriger silencieusement ses octets. Marquer `quarantined`, conserver preuve, revenir au dernier snapshot vérifié si configuré et journaliser l'intervention. Ne pas supprimer des preuves historiques pour « réparer » des chiffres de couverture.

## Tests d'états

Transitions interdites, crash à chaque étape, double publication, révision périmée, nouvel ETag externe entre checkpoint/reprise, utilisateur non autorisé et plan changé après approbation doivent tous produire un échec propre et reproductible.
