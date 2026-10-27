# 11 — Tests et critères d'acceptation

## Tests critiques P0

- [ ] `KQ1001` du namespace A n'est jamais confondu avec `KQ1001` du namespace B.
- [ ] `KQ1001` ≠ `wikidata:Q1001` sans correspondance exacte acceptée.
- [ ] KQ↔Q et KP↔P : les correspondances inversées sont rejetées.
- [ ] Un même mot français apparaît dans deux KQ : recherche inverse offre deux candidats et ne fusionne rien.
- [ ] `closeMatch` ne compte pas comme `exactMatch` et ne permet pas l'import lexical vérifié.
- [ ] Tout import conserve snapshot, hash, provenance et licence, sans effacer la curation locale.
- [ ] Deux libellés contradictoires de **priorité égale** donnent `conflicted`, pas un résultat arbitraire.
- [ ] Repli `fr-CA → fr` compte uniquement dans `fallback`, jamais `direct`.
- [ ] Déclarer 301 langues sans données n'invente aucune entrée et ne remplit aucun score fictif.
- [ ] Une langue sélectionnée sans label sur un graphe non vide affiche 0 %, pas « couvert ».
- [ ] Les KP utilisés dans les qualifiers sont audités en plus des KP sujets de prédicats.
- [ ] Un graphe ancien comportant des identités textuelles non résolues n'affiche pas 100 % de couverture.
- [ ] Le texte d'une citation reste strictement inchangé pendant les suggestions de migration.
- [ ] Aucun plan `pending`/`rejected`, ou dont le hash source a changé, n'est appliqué.
- [ ] Aucune commande diK n'écrase un ancien Kristal ou son engagement.
- [ ] Toutes les couches et rapports produits sont reconstruisibles avec les mêmes fichiers et digests.

## Tests P1 (scalabilité et fonctionnement)

- [ ] Import streaming d'un dump volumineux sans charger tout le fichier en RAM ; reprise après interruption.
- [ ] Comparaison de deux snapshots Wikidata, traitement des Q/P créés, redirigés et supprimés.
- [ ] Unicode combinant / variations d'écriture / RTL : texte préservé et comparaison non destructive.
- [ ] Tags de langue invalides rejetés par registre IANA/CLDR, pas seulement une expression régulière.
- [ ] DiK sait produire une matrice multi-Kristals avec périmètres et namespaces visibles.
- [ ] Résolutions et approbations reproductibles par snapshot ; audit détaillé.
- [ ] Répertoire importé malveillant / chemin de traversée rejeté.
- [ ] Aucune sortie réseau implicite lors du traitement de corpus privé.

## Scénarios d'acceptation métier

**A. Couverture d'un Kristal canonique.** Sur 2 KQ, 1 KP et les langues `fr`, `en`, `fr-CA` du fixture Framework, le rapport reproduit les comptes présents dans `dik-coverage.example.json`.

**B. Arrivée d'un futur Q.** Le KQ local reste stable et un nouveau `accepted exactMatch` versionné apparaît après revue ; tous les anciens graphes restent validables.

**C. Désambiguïsation « grâce ».** L'application montre au moins deux sens si la source les permet ; aucune sélection automatique n'est réputée autorisée.

**D. Préservation de l'historique.** Une migration approuvée crée un nouvel artefact et une charte de conversion, sans modifier les anciens fichiers ni leurs empreintes.

## Définition des jalons

**diK 0.1 fonctionnel :** CLI locale, projet unique, import échantillon/local, audit catalogue, rapports KQ/KP, plans non exécutables ; tests P0 pertinents verts.

**diK 0.2 fonctionnel :** conciliation et revue, priorités et corrections curatées, gestion multiréférentielle.

**diK 1.0 :** import massif robuste, 300+ langues mesurées, politiques de sécurité, UI stable, diagnostics/audit complets, intégration Authoring Kit **conditionnée à la disponibilité de son contrat d'exécution**.

Ces versions sont des **jalons proposés**, non des livraisons déjà réalisées.
