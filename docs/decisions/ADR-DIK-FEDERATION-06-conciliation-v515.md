# ADR-DIK-FEDERATION-06 — Conciliation sémantique candidate V5.15

**Statut :** proposition d'implémentation non normative. **Producteur :**
Kristal-Manager, à partir de la projection locale V5.14. **Autorité :**
Framework/Kit et propriétaires des Kristals; qualification et publication
restent indépendantes.

## Décision et anti-décisions

Comparer les identifiants `(namespace_id, KQ/KP/KA/KS)`, termes par langue,
statuts source et cibles externes **entre révisions non sélectionnées**.
L'analyse écrit un registre privé de dossiers en état `NOT_DECIDED`, épinglé
sur le SHA-256 de la base V5.14 et gardant les chemins et preuves originaux.

Ne jamais déduire de l'égalité textuelle une identité sémantique commune.
Deux `KQ1001` de namespaces distincts restent distincts. Un terme partagé
peut être polysémique. Un Q Wikidata n'est qu'une identité externe. Le type
de relation `exactMatch` observé avec statut `candidate` ou `accepted` est
une **affirmation du fichier source**; l'observatoire ne le qualifie pas.
Les cibles `rejected` sont exclues des conflits actifs de cibles.

Aucune commande V5.15 ne sélectionne de révision, n'écrit dans `canon/`, ne
modifie les catalogues diK, ne fusionne de concept, ne contacte Wikidata,
n'écrit dans `kristal-public`, ne publie, et n'active de RuntimeSet.

## Critères avant une future correction

1. Choix humain du propriétaire pour la révision exacte et justification
   des divergences de rôle, de terme et de cible.
2. Preuves et décisions KS pour les liens Wikidata, vérifiées indépendamment.
3. Validation Framework v11/TCK sur les octets déclarés.
4. Nouvelle révision locale enregistrée par Kit selon sa récupération
   transactionnelle; historique et labels anciens préservés.
5. Qualification distincte C1/C2 puis publication C3 autorisée séparément.

Les rapports V5.15 sont **des files de travail**, et ne constituent pas
une source d'autorité révisée pour diK ou les Kristals.
