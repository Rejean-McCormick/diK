# ADR-DIK-FEDERATION-05 — Observatoire sémantique V5.14 (candidat)

**Statut :** architecture candidate non normative. **Propriétaire de l'index :**
Kristal-Manager. **Propriétaires des identités :** Kristals locaux, conformes
aux contrats Framework effectivement adoptés. **Producteur de canon :** Kit.

## Décision

La fédération collecte des **occurrences**, jamais une identité sémantique
globale implicite: `(namespace_id, KQ/KP/KA/KS)` est la clé de portée, assortie
du Kristal, de la révision non sélectionnée et de la provenance SHA-256. Le mot
reste dans les dictionnaires à couches, avec langue et état de revue; le lien
vers `Q...`/`P...` Wikidata est un mapping externe séparé.

L'index privé est créé exclusivement à partir de fichiers déclarés dans les
`canon/state.index.json` des Kristals **locaux**, sans modifier ces fichiers,
les commits d'état, les révisions, le graphe, les dictionnaires ni le public.
Un statut `accepted` dans une source n'est pas une certification indépendante;
les collisions `(namespace_id,id)` entre propriétaires bloquent la promotion.

## Portes encore nécessaires

1. Revue des doublons et conflits de sens entre révisions; jamais de sélection
   automatique par chronologie ou nombre d'occurrences.
2. Validation Framework/TCK, syntaxique et logique, sur la révision exacte.
3. Revue humaine des alignements Wikidata et des preuves KS indépendantes.
4. Sélection canonique explicite par le propriétaire et, le cas échéant,
   qualification indépendante C1/C2, préparation de copie via Kit/Manager,
   autorisation de publication C3 et activation distincte.

Le répertoire public n'est jamais une source de correction. Cet ADR n'étend
aucune autorité à Manager et ne remplace pas la spécification diK/Framework.
