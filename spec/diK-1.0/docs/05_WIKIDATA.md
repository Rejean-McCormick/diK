# 05 — Copie Wikidata, import, synchronisation et reprise

## IMP-001 — Source externe et miroir

Le dump Wikidata est une **entrée non fiable** et non une autorité locale de KQ. Son format Q/P, ses alias, ses révisions, ses descriptions, redirections sont adaptés dans une couche anti-corruption. Le miroir local de l'utilisateur est supporté sans accès Internet. Un téléchargement depuis une source officielle est une opération **explicite** distincte du rendu/lookup.

## IMP-002 — Pipeline robuste

1. L'opérateur fournit URL ou chemin local, mode (`full`/`delta` si source fiable disponible), révision/date, langues ciblées, limites de ressources et destination.
2. Vérifier signature/checksum de l'amont *si disponible* ; toujours calculer empreinte locale ; ne jamais décompresser sans quotas ni écrire à une destination arbitraire contrôlée par le dump.
3. Parser **en flux**, supporter `.json`, `.jsonl`, `.gz`, `.bz2` compatibles ; préciser le format réellement accepté ; ne pas matérialiser des milliards de records en RAM.
4. Joindre uniquement `accepted + exactMatch` actif pour le namespace choisi ; `candidate`, `rejected`, `relatedMatch` sont exclus des imports vérifiés.
5. Générer shards immuables par locale/plage, provenance, hashes et statistiques; séparer erreurs isolées et erreurs bloquantes selon politique configurée et observable.
6. Comparer contre l'ancien snapshot : ajout/suppression/label/alias/redirect/merge/split, classer les changements et ouvrir une tâche de revue si le sens pourrait changer.
7. Vérifier puis publier atomiquement le nouveau catalogue ; conserver l'ancien ; ne jamais modifier `curated` ni réallouer des KQ.

## IMP-003 — Reprise/idempotence

Clé de tâche = hash canonique `(source snapshot, namespace, crosswalk revision, selected locales, transform version, settings)`. Même clé/mêmes octets -> résultat identique sans duplication ; même clé/octets différents -> conflit bloquant. Checkpoints portent compteur d'objets, shard terminé, empreintes ; reprise uniquement si source identique, transformation identique et point de reprise validé. Compresser et reprendre par blocs/fragments vérifiables, sans promettre seek arbitraire dans un `bz2` monolithique.

## IMP-004 — Téléchargements

HTTP(S) seulement si activé ; délais et budget total, retry avec backoff+jitter seulement sur erreurs transitoires, limite de débit, stockage temporaire de téléchargement, métadonnées ETag/Last-Modified *si la source les fournit*, checksum post-téléchargement, publication après validation. Aucun appel réseau dans `projection restore`, `coverage`, `lookup` ni au démarrage de diK.

## IMP-005 — Wikibase lexèmes

Les lexèmes Wikidata `L…` (formes/sens) sont différents des items `Q…` et propriétés `P…`. L'import 1.0 des labels Q/P **ne les traite pas** comme des KQ. Un connecteur L séparé demanderait des contrats explicitement typés et des tests distincts.

## Critères bloquants

- IMP-T1 interruption à 50% => aucun nouveau catalogue visible ; reprise identique.
- IMP-T2 nouveau snapshot Wikidata avec label changé => ancienne couche disponible, correction curatée intacte.
- IMP-T3 Q nouveau aligné uniquement `candidate` => aucune importation vérifiée.
- IMP-T4 dump contenant champs/path malveillants => aucun traversal ni exécution.
- IMP-T5 même import relancé => aucune duplication.
- IMP-T6 suppression ou redirection externe => événement de rapprochement, pas fusion de KQ.
