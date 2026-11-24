# 57 — Identités, preuves et habilitation : KQ/KP, Wikidata Q/P, L/S/F et GF

> **Mise à jour du 23 novembre 2026 :** les composants dont les formats sont prouvés sont implémentés dans **alpha.11**. Lire le [chapitre 61 — état réellement livré](61_IMPLEMENTATION_EFFECTIVE_V5_3.md). Les parties visant des schémas locaux encore inconnus demeurent des spécifications, non des fonctionnalités certifiées.

**Contrat d'architecture proposé pour V5.3 ; non implémenté.** Complète [03 — identités](03_IDENTITES_ET_ALIGNEMENTS.md), [37 — connecteurs](37_CONNECTEURS_WIKIDATA_GF.md), [40 — gouvernance](40_SECURITE_DROITS_PROVENANCE.md) et [43 — statuts](43_PREUVES_STATUTS_ET_LIMITES.md).

## Une résolution est une jointure, pas une traduction

Demande : `(namespace_id, semantic_id, locale)` où `semantic_id` est un KQ ou KP valide. Correspondance **seulement** depuis le `external-crosswalk.json` de la révision officielle auditée, avec relation `exactMatch`, décision `accepted`, preuves KS vérifiées et catégorie compatible (`KQ↔Q`, `KP↔P`). La relation doit être non contradictoire **dans le namespace et la révision considérés**. Le Q/P donne accès aux champs explicites de la locale cible dans une source référencée ; aucune langue intermédiaire n'intervient.

## Échelle des permissions

| Étape | Exemple d'évidence | Peut compter comme résolu ? |
|---|---|---|
| Source trouvée | chemin + SHA local | **Non** |
| Schéma confirmé | profil vérifié, version d'adaptateur | **Non** |
| Q/P observé | champ et rôle documentés | **Non** |
| Q/P ↔ KQ/KP accepted | crosswalk, namespace, KS, non-contradiction | **Non**, pas encore de label |
| Label explicite pour `locale` | texte exact, origine, position | **Non**, forme **candidate** |
| Droits + provenance qualifiés | licence, attribution, date/versions, restrictions | **Non**, pas sans activation explicite |
| Activation par politique/réviseur | version d'une décision, couche et priorité | **Oui**, après contrôle et uniquement dans le périmètre autorisé |

Le moteur V5.2 n'active rien. La dernière ligne est une **cible** à implémenter séparément, pas une autorisation automatique accordée par ce document.

## Échecs fermés

- `candidate`, `closeMatch`, lien `deprecated` ou décisions non vérifiables : **aucune activation**.
- Deux Q/P distincts acceptés pour un même `(namespace, KQ/KP)` sans règle d'arbitrage documentée : **conflit**, pas choix arbitraire.
- Formes différentes pour le même Q/P + locale sous des sources distinctes : signaler l'écart ; garder provenance séparée ; ne pas écraser.
- Valeur `Q123` présente dans une assertion comme prédicat/objet : **pas** automatiquement label du sujet ni lien KQ/P.
- Ressemblance de graphie entre un label GF et Wikidata : **pas** d'alignement sémantique.
- `no`, `nb`, `nn` sont des codes distincts ; **aucun** repli implicite.
- Aucune preuve de droits : observation possible en lecture seule, **publication interdite**.

## Typage obligatoire des identifiants

| Espace | Signification | Règle V5.3 |
|---|---|---|
| `namespace_id + KQ...` | identité de référent Kristal | canonique dans son namespace |
| `namespace_id + KP...` | identité de propriété Kristal | canonique dans son namespace |
| `Q...` | item Wikidata | pas un KQ par substitution de préfixe |
| `P...` | propriété Wikidata | pas un KP par substitution de préfixe |
| `L...` | lexème Wikidata | **autre** type d'objet, à relier par preuve distincte |
| `L...-S...`, `L...-F...` | sens / forme de lexème | autres espaces de clés ; pas Q/P |
| Fonction GF / catégorie GF | objet grammatical | non assimilable à un ID Wikidata ou Kristal |

Les données GF (RGL, archives de dictionnaires `.gf`, PGF, WordBench) peuvent permettre une réalisation grammaticale après **un mapping attesté** `(namespace,KQ/P) ↔ entrée GF` avec langue et paradigme. Ce chantier est **distinct** de la lecture des 40 sources Wikidata et n'est pas livré en V5.3 documentaire.

## Différence entre audit, droit, et publication

Un rapport indiquant « forme observée » n'autorise ni redistribution d'un dump, ni publication d'une couche. Les licences doivent être déterminées **par source**, avec conditions de réutilisation, restrictions d'attribution et versions. L'activation éventuelle devra produire une décision versionnée, traçable et réversible, tout en préservant le Framework v11 et les catalogues antérieurs.

## Transparence des chiffres

Le dénominateur historique `294 364` couvre les **57** Kristals évaluables ; il ne mesure pas les 69 non évaluables. Un scan dont le périmètre change doit afficher ce changement : ne pas comparer ses pourcentages sans expliquer les nouveaux dénominateurs.
