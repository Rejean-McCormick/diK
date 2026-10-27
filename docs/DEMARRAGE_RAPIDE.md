# diK — Démarrage rapide pour l'équipe de développement

**Ce dépôt documentaire décrit un logiciel à construire. Les exemples exécutables ci-dessous appartiennent à Kristal Framework 11.0.0-draft.3.**

## Étape 1 — Identifier les dépendances

Se procurer le Framework v11 draft.3 contenant `schemas/v11`, `tools/v11` et `examples/v11`. Lire [l'architecture](docs/02_ARCHITECTURE.md), [les identités](docs/03_IDENTITES_ET_ALIGNEMENTS.md) et [les tests](docs/11_TESTS_ET_ACCEPTATION.md).

## Étape 2 — Lire un graphe déjà canonique

Charger `examples/framework-v11-draft3/semantic-graph.example.json` et `identity-registry.example.json`. Construire l'inventaire des référents `(namespace, KQ/KP)` en comptant chaque identité distincte. Le modèle de graphe autorise des valeurs `literal` : ne pas essayer de les traiter comme des KQ.

## Étape 3 — Lire le catalogue lexical

Ouvrir `examples/framework-v11-draft3/dictionaries/catalog.json`. Vérifier les digests des fichiers, respecter l'ordre déclaré des couches et les replis `fr-CA → fr`. Les dictionnaires sont des projections lexicales, non des clés du graphe.

## Étape 4 — Calculer la couverture

Depuis le dossier du Framework :

```bash
python tools/v11/dik_coverage.py \
  --graph examples/v11/semantic-graph.example.json \
  --registry examples/v11/identity-registry.example.json \
  --crosswalk examples/v11/external-crosswalk.example.json \
  --catalog examples/v11/dictionaries/catalog.json \
  --locales fr,en,fr-CA \
  --output /tmp/rapport-diK.json
```

Comparer le rapport au fichier `dik-coverage.example.json` fourni ici comme fixture figée. Un résultat d'égalité binaire n'est pas toujours garanti si les IDs de rapports/hashes changent entre sources ; comparer structure et mesures avec la même version de fixtures.

## Étape 5 — Explorer la conversion, sans appliquer

Lire `examples/framework-v11-draft3/dik-conversion-plan.example.json`. Les opérations y sont `pending`, donc **non approuvées**. Le rôle de diK est d'expliquer chaque proposition et de préparer une décision, non de réécrire automatiquement les anciens graphes.

## Première itération concrète à coder

- Lecteur du registre et du graphe v11, avec vérification des namespaces.
- Lecteur des catalogues et des couches lexicales, avec validation SHA-256.
- Calculateur de couverture KQ/KP par langue et export du rapport Framework.
- CLI `project inspect` et `coverage report` en mode local.
- Tests de sécurité d'identités et de non-régression avant toute fonction d'édition.

Cette première itération doit pouvoir fonctionner sans réseau, sans serveur et sans téléchargement Wikidata.
