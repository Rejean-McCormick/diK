# ADR-0003 — Profil local diK 1.0 (proposition normative du dossier)

**Statut : PROPOSED / candidate.2 ; ratification humaine requise avant gel final.**

## Contexte

Huit choix ouverts étaient laissés aux agents IA. Ils risquaient de produire des implémentations incompatibles, notamment un serveur imposé, un allocateur KQ incorporé à diK et un cache considéré comme canon.

## Profil proposé pour implémenter sans dérive

| Question | Comportement par défaut du profil local | Extension, jamais présumée |
|---|---|---|
| UI | UI web servie sur loopback avec session locale ou interface desktop ; **CLI obligatoire** même sans UI | serveur distant ou collaboration |
| Réseau | **hors ligne** et aucun appel automatique ; import depuis un miroir/fichier explicitement sélectionné | téléchargement HTTPS explicite/reprise |
| Acteurs | espace local mono-utilisateur avec journal des décisions | ACL multi-utilisateur et signatures |
| Authentification | aucune exposition hors loopback ; opérations locales limitées au propriétaire du workspace | jetons authentifiés, TLS, audit distant |
| Attribution KQ/KP | diK ne mint **jamais** ; le registre/producteur Framework reste seul autorisé | allocateur externe déclaré par interface |
| Migrations | plans proposés uniquement ; l'Authoring Kit/producteur applique après revalidation | aucun exécuteur implicite |
| Stockage | snapshots signalisés par SHA-256 et pointeur atomique ; SQLite dérivé | base distante synchronisée |
| Import Wikidata | miroir local versionné, snapshot explicite, extraction en flux | connecteur réseau activable séparément |
| Projections massives | profil compact diK v0.3 inchangé ; export séquentiel sans inventer nouveau wire format | profil shardé futur et versionné |
| Conservation | ne jamais supprimer automatiquement les artefacts engagés ni les décisions ; sauvegarde/restauration documentée | politique de purge validée par gouvernance |
| Signatures | SHA-256 pour intégrité, pas preuve d'auteur | signatures de publication si acteurs multiples |

## Impacts de compatibilité et sécurité

Pas de nouvelle identité canonique ni de modification des schémas Framework. Les endpoints réseau ne peuvent pas être exposés par défaut ; les droits d'import doivent être établis et le journal de décisions contrôlé. L'absence de signature doit être affichée comme limite en contexte multi-acteurs.

## Tests d'acceptation à implémenter

API bloquée hors loopback ; démarrage sans réseau ; diK refuse d'allouer un KQ ; crash prépublication et après publication ; reprise idempotente ; import de source inconnue mis en quarantaine ; restauration sans réécriture d'historique.
