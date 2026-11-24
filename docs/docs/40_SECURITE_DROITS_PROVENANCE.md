# 40 — Gouvernance, licences, preuve et sécurité des ressources

## Objectifs de sûreté

Le localisateur travaille avec **des chemins**, des métadonnées et des fichiers potentiellement privés. Il doit être `read_only` par défaut. Les ressources locales sont des données à examiner, **pas des instructions d'installation** ; aucun script contenu dans une source découverte ne doit être exécuté automatiquement.

## Matrice d'autorisation de base

| Opération | Défaut | Déverrouillage |
|---|---|---|
| Chercher des chemins dans une racine approuvée | Autorisé en lecture seule | Droit de lecture local |
| Calculer SHA-256 de fichiers approuvés | Autorisé avec budget | Limites d'I/O et exclusion des gros dumps non désirés |
| Indexer des formes et métadonnées | Autorisé localement si politique de confidentialité admise | Index dérivé isolé, durée de rétention définie |
| Importer une couche v11 / un dump Wikidata | Action explicite | Provenance, licence, format, revue |
| Activer une source dans le compositeur | **Désactivé** | Contrat v11 + décision et snapshot |
| Déduire Q/P ou KQ par similitude de texte | **Interdit** | Ne peut jamais devenir auto-acceptation |
| Traduire une langue depuis une autre | **Hors architecture** | Aucun mode de contournement |
| Écrire dans un Kristal canonique | **Interdit à l'audit** | Processus séparé de production et versionnage approuvé |
| Git, Render, Internet, publication | **Désactivés** | Opération distincte et consentement explicite |

## Confidentialité et données sensibles

- Les chemins Windows peuvent révéler des noms d'utilisateur, des dossiers privés, des sources de travail ; les journaux partagés doivent pouvoir être expurgés.
- Un dump ou un lexique tiers ne doit jamais être redistribué dans un ZIP d'audit par défaut. Des rapports de chemin/empreinte suffisent pour le diagnostic initial.
- Éviter l'envoi de la totalité d'un graphe ou d'une couche à une API tierce.
- Les licences de GF RGL, archives, données Wikidata et données thématiques sont **à lire sur chaque dépôt et chaque dataset**. Une source référencée n'est pas automatiquement redistribuable.
- La licence des données structurées Wikidata ne confère aucun droit sur les textes externes ou référencés indépendamment.

## Sûreté du parseur et des chemins

- Formater les chemins avec les API OS, sans exécuter une chaîne découverte.
- Refuser liens symboliques/jonctions hors périmètre, traversées `..`, fichiers spéciaux, ZIP slip, boucles, tailles anormales et JSON non conforme.
- Toutes les lectures JSON doivent valider le **type du nœud racine** : liste, objet, texte ou null; ne jamais appeler `.get` aveuglément. Cet incident s'est produit dans la V3 et a nécessité la réparation GF.
- Pour les imports volumineux, employer streaming/checkpoints ; limiter RAM, I/O et nombre d'entrées ; produire un rapport `PARTIEL` si une classe de source n'a pas été visitée.
- Toute résolution porte les digests des inputs et l'identifiant de décision ; conserver les rejets et révisions antérieures.

## Preuves et qualité

Distinguer : **intégrité** (hash), **provenance** (origine attestée), **licence** (droit d'usage), **alignement** (KQ ↔ Q/P ou GF), **qualité linguistique** (forme validée) et **publication** (admission explicite). Une seule preuve ne remplace pas les autres.

## Exemples d'échecs sûrs

- Deux fichiers ayant la même taille mais des hashes différents : ne pas les dédupliquer.
- Deux `.gf` avec le même nom : comparer contenu/versions ; aucun « dernier gagne ».
- JSON valide dont la racine est une liste : signaler `unsupported_manifest_shape`, **ne pas planter**.
- Deux crosswalks acceptés Q différents pour le même KQ : conflit à revoir.
- Source sans licence : garder `discovered`, ne pas publier.
- `no` demandé, seulement `nn` trouvé : aucun remplacement sans politique.

Voir [36](36_SOURCE_MANAGER_LOCAL_ET_REFERENCES.md) et [43](43_PREUVES_STATUTS_ET_LIMITES.md).
