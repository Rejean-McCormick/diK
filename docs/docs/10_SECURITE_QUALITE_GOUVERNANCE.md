# 10 — Sécurité, qualité et gouvernance

## Principes de sécurité

- **Local-first** : aucun corpus privé, mot historique, nom de projet ou document ne part en requête Web implicitement.
- **Révision obligatoire** des correspondances exactes nouvelles fondées sur l'interprétation du sens, avec preuve `KS` dans le modèle Framework.
- **Identité de namespace** partout ; jamais de `KQ1001` utilisé sans contexte de namespace dans le stockage ou les caches.
- **Sources et sorties immuables** : snapshot importé jamais édité en place ; checksums et journaux.
- **Migration non destructive** : l'original, les commitments v9 et les citations littérales restent intacts.
- **Index régénérables** : supprimer les caches ne supprime aucun dictionnaire canonique.

## Menaces et protections à prévoir

| Risque | Contrôle |
|---|---|
| Collision entre namespaces | Identité composée `(namespace, semantic_id)` dans les tables, exports et index |
| Faux exactMatch par homonymie | Contexte, type, preuves, revue indépendante du libellé |
| Import corrompu/malveillant | Contrôle d'empreinte, limites de taille, parse streaming, validation, quarantaine |
| Traversée de chemin via catalogue | Résolution de chemins sous répertoire autorisé, refus `..` et symlinks hors racine |
| Conditions de réutilisation d'un dictionnaire | Métadonnées obligatoires, refus de publication non conforme |
| Erreur humaine de réviseur | Historique append-only, refus/annulation par nouvelle décision, audit |
| Traduction générée inventée | Jamais comptée validée sans revue et provenance explicite |
| Export de termes privés vers Wikidata/API | Réseau désactivé par défaut, consentement explicite, journal d'accès |
| Mise à jour interrompue | Staging + validation + commit atomique du nouveau catalogue |
| Anciens artefacts modifiés | Digests source avant/après et stockage immutable des originaux |

## Qualité d'alignement

Une décision `accepted exactMatch` signifie « validée selon notre procédure », non « vérité garantie ». Documenter les critères de revue, la preuve, les objections et le domaine. Une source externe réputée n'exonère pas d'une vérification de sens, surtout pour les concepts théologiques, historiques, locaux ou spécialisés.

## Permissions proposées

**Lecteur** : recherche et rapports ; **Éditeur lexical** : propositions de termes/alias ; **Réviseur** : accepte/refuse alignements et termes ; **Administrateur** : sources, catalogues, namespace et droits ; **Producteur** (service Authoring Kit) : unique acteur habilité à écrire une nouvelle révision de Kristal. Ce modèle RBAC est **prévu**, pas encore codé.

## Traçabilité

Pour chaque décision : identifiant, entrée/sortie, hash des snapshots consultés, namespace, auteur/réviseur, date, justification, preuves, statut et liens aux décisions supersédées. Le journal permet la **reconstitution** des vues, pas l'effacement silencieux des choix passés.
