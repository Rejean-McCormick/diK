# diK — Projections linguistiques bidirectionnelles

**Implémentation initiale : diK 0.2.0, 2026-10-16.**  
**Contrats externes inchangés : Kristal Framework 11.0.0-draft.3.**  
**Format applicatif expérimental diK : `dik.reversible-projection/1.0`.**

## Décision

Le **graphe KQ/KP/KA/KS** demeure la source de vérité. Les libellés naturels sont des **annotations de présentation** générées à partir des dictionnaires. **Le retour au canon ne fait jamais de recherche inverse mot → KQ** : il relit exclusivement la partie canonique conservée dans l'enveloppe diK. La projection de lecture n'a aucune autorité pour créer, fusionner, traduire ou modifier les identités.

Cette solution sépare trois produits différents :

| Sortie | Usage | Reconvertible seule ? |
|---|---|---|
| JSON diK réversible | Archive de travail avec graphe canonique, lecture, empreintes et références | **Oui** ; contrôles renforcés avec le projet original |
| Markdown annoté | Lecture par IA, débogage, revue, références `KQ/KP` visibles | **Non**, requiert le JSON |
| Markdown épuré | Lecture humaine facile, sans répétition systématique des IDs | **Non**, requiert le JSON |

Le Markdown est une **vue jetable** : ne jamais le présenter comme un Kristal modifiable ou canonique. Le JSON réversible peut être regeneré autant que nécessaire lorsque les dictionnaires évoluent, mais conserve les empreintes du projet source utilisé.

## Contrat concret de l'enveloppe

- `projection_format = dik.reversible-projection/1.0` ; `derived_only = true`.
- `anchors` fixe le contrat Framework, le namespace, l'identité de graphe et les SHA-256 des fichiers de graphe, catalogue lexical, registre et correspondances externes.
- `canonical_graph` contient **sans remplacement lexical** le graphe v11 complet, notamment les assertions, les qualificatifs, les sources et les valeurs littérales.
- `readable` contient les sujets, propriétés, objets entités et qualificatifs sous forme `{id, label, status, effective_locale, layer_id}`, selon disponibilité. Les littéraux restent des valeurs, jamais des recherches conceptuelles.
- `digests` contient des empreintes SHA-256 sur la sérialisation canonique JSON des parties principales.

**Empreinte n'est pas signature.** Les SHA-256 détectent les modifications accidentelles, mais quelqu'un peut recalculer des empreintes sur une enveloppe malveillante. Avec `--project`, diK compare les sources épinglées et régénère la projection, puis exige une égalité structurelle exacte. Sans `--project`, il ne peut certifier l'authenticité de la source ; seule la cohérence interne est vérifiée.

## Résolution de langue

1. Valider le graphe, les IDs et les couches lexicales via les schémas Framework v11.
2. Charger **une fois par couche** les libellés nécessaires à ce graphe ; éviter un balayage complet du dictionnaire pour chaque KQ.
3. Utiliser d'abord la langue demandée, puis uniquement les replis explicitement déclarés par le catalogue (ex. `fr-CA → fr`).
4. Appliquer les priorités déterministes des couches ; rejeter les conflits entre libellés concurrents au même niveau.
5. Marquer explicitement `direct`, `fallback`, `missing`. Ne pas inventer de traduction ; pour les manquants, conserver l'ID et afficher « non traduit ».
6. Générer séparément le JSON de provenance et le texte destiné à l'IA ou à l'utilisateur.

Le nombre de langues (300 ou davantage) est une caractéristique du catalogue ; on ne duplique pas 300 fois le graphe source. On génère une projection pour la langue demandée, à partir d'un dictionnaire versionné, et on peut la mettre en cache par `(empreinte graphe, empreinte catalogue, locale, profil)`.

## Commandes livrées

```bash
# Voir un Kristal dans une langue, avec IDs pour l'IA / audit
python -m dik projection export \
  --project examples/demo/dik.project.json \
  --locale fr-CA \
  --output exports/fr-CA.dikproj.json \
  --markdown exports/fr-CA.annotated.md

# Même modèle, mais texte épuré pour l'utilisateur
python -m dik projection export \
  --project examples/demo/dik.project.json \
  --locale en --style clean \
  --output exports/en.dikproj.json \
  --markdown exports/en.readable.md

# Contrôler l'enveloppe + dictionnaires exacts d'origine
python -m dik projection verify \
  --input exports/fr-CA.dikproj.json \
  --project examples/demo/dik.project.json

# Reconstruire le format sémantique pur, dans un NOUVEAU fichier
python -m dik projection restore \
  --input exports/fr-CA.dikproj.json \
  --project examples/demo/dik.project.json \
  --output exports/restored-semantic.json
```

Sans `--project`, `verify` et `restore` permettent une récupération *détachée*, fondée sur le graphe embarqué et ses empreintes non authentifiées. Ce mode est moins sûr et réservé aux archives dont la provenance a déjà été vérifiée.

Le retour garantit **l'égalité de données du graphe JSON**, pas l'identité des espaces, de l'indentation ni des octets du fichier d'origine. Le nouveau graphe doit ensuite passer les contrôles du Framework avant toute publication.

## Et si une IA ou un utilisateur modifie la version lisible ?

Une modification libre d'un mot est **insuffisante pour modifier une relation**. En 0.2.0, une projection altérée échoue au contrôle et ne se convertit pas silencieusement en nouveaux KQ/KP. Pour éditer effectivement le contenu sémantique, il faudra un flux séparé :

1. **Proposition** : l'éditeur envoie un patch structuré référençant `KA`, `KQ` et `KP` explicites, les anciens et nouveaux objets typés et les preuves requises.
2. **Validation** : comparaison avec le graphe source engagé, contrôle de registre / cardinalité / types / provenance et décision humaine pour toute ambiguïté.
3. **Application** : Authoring Kit construit un **nouveau graphe canonique** et des engagements nouveaux ; l'ancien reste intact.
4. **Reprojection** : diK produit des vues dans les langues demandées depuis ce nouvel état.

La capacité de traitement automatique des **patches sémantiques édités** n'est **pas livrée** en diK 0.2.0. Elle nécessitera un contrat partagé avec l'Authoring Kit / Framework et des tests d'intégration.

## Invariants et acceptation

- `restore(export(G, L)) == G` pour toutes les langues déclarées, y compris les langues incomplètes.
- La lecture d'un mot ne crée **jamais** une équivalence sémantique ; le crosswalk Wikidata reste distinct.
- Les identifiants de référents et propriétés ne dépendent pas de la langue.
- Sources, qualificatifs et valeurs littérales ne sont jamais traduits par substitution d'ID.
- Un changement du catalogue épinglé bloque la vérification avec `--project` (une nouvelle projection est alors nécessaire).
- Pas d'écrasement automatique de fichier projeté ou restauré.
- Une version uniquement Markdown ne suffit pas à reconstruire le canon.
- Les volumes massifs et l'interface graphique restent des étapes de qualification ultérieures.

## Interopérabilité

L'Integration Pack v11 possède déjà une **projection de lecture dérivée**, mais pas cette enveloppe de reconversion diK. Ce profil est actuellement **applicatif à diK**, pas un schéma normatif nouvellement ajouté à Framework v11. L'alignement formel des formats inter-repos nécessitera une version ultérieure du contrat ou un adaptateur explicitement testé.
