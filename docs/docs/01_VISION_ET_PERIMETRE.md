# 01 — Vision, objectifs et frontières

## Pourquoi diK

Les Kristals historiques peuvent contenir des identités locales sous forme de mots, de slug ou d'URN. Les nouvelles versions disposent de `KQ/KP/KA/KS`, de dictionnaires séparés et de correspondances externes, mais la mise en conformité doit être **gérée à l'échelle de nombreux projets et langues**, avec contrôle humain.

## Ce que diK doit rendre possible

1. **Relier plusieurs dictionnaires** français, anglais et spécialisés sans fusionner des sens différents.
2. **Accueillir 300 langues ou plus**, avec couverture partielle explicite, sans copier 300 fois le graphe.
3. **Importer une copie locale de Wikidata**, télécharger volontairement des mises à jour, conserver chaque snapshot et protéger les corrections internes.
4. **Connaître la couverture exacte** des KQ et KP réellement employés par chaque Kristal dans chaque langue déclarée.
5. **Traduire au rendu** sans redéfinir les concepts ni écrire le nom traduit dans les structures canoniques.
6. **Normaliser les anciens graphes** par suggestions, revue, plan de conversion et révision nouvelle, sans toucher à l'ancien canon.
7. **Produire des rapports reproductibles** pour CI, audit, publication, production et comparaisons dans le temps.

## Ce que diK n'est pas

- Ni le registre souverain des identités de Kristal ; le propriétaire des `KQ/KP` et leurs allocations restent sous les règles du Framework et des producteurs autorisés.
- Ni un clone de Wikidata ou une forge de faux `Q…` ; la correspondance avec Wikidata est externe, typée et versionnée.
- Ni un moteur de traduction automatique certifiant la vérité de ses sorties. Des candidats peuvent être générés par IA, mais ne deviennent pas des équivalences validées sans revue.
- Ni un destructeur de graphes anciens : aucune réécriture in situ des artefacts engagés ou signés.
- Ni un dictionnaire de langue généraliste complet : les libellés Q/P de Wikidata décrivent des **entités et propriétés**, non toutes les flexions et acceptions d'une langue.

## Vocabulaire produit

**Identifiant sémantique :** expression compréhensible par l'utilisateur. **Identifiant de référent sémantique (IRS) :** terme précis pour les entités/concepts du type `KQ`. **Identifiant de propriété :** `KP`. L'un et l'autre sont des identifiants opaques *dans un namespace*. `QID` et `PID` sont des identifiants **externes Wikidata**. Une `IRI` peut adresser une ressource, sans être le sens intrinsèque du référent.

## Principes de décision

- Distinguer **identité**, **définition**, **libellé**, **alias**, **équivalence** et **source**.
- Toute absence reste une absence : pas de traductions inventées ni de traduction régionale implicite.
- Un mot ambigu donne plusieurs candidats, jamais une fusion automatique.
- Une hausse de couverture lexicale n'est pas automatiquement une hausse de qualité sémantique.
- Toute mesure et décision est attribuable à un état figé du graphe, des dictionnaires et des correspondances.
