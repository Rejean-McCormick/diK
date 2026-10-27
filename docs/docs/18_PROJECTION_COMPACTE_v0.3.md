# diK 0.3 — Projection compacte, réversible et linguistique

## Décision

Le nouveau format par défaut est `dik.compact-projection/1.0`. Il stocke **une fois** le graphe sémantique canonique (`canonical_graph`) et **une fois** chaque libellé nécessaire dans `lexicon.entries`, indexé par KQ/KP. Il ne duplique plus les traductions dans chaque assertion.

Les identifiants restent **dans toutes les positions sémantiques du graphe**. La table lexicale est seulement une vue dérivée, sans autorité. Les libellés ne sont jamais utilisés pour restaurer le graphe. On ne convertit **jamais** une vue Markdown éditée en KQ par heuristique.

## Format

```json
{
  "projection_format": "dik.compact-projection/1.0",
  "derived_only": true,
  "anchors": { "framework_contract": "11.0.0-draft.3", "namespace_id": "...", "graph_id": "...", "source_sha256": { "graph": "...", "catalog": "...", "registry": "...", "crosswalk": "..." } },
  "canonical_graph": { "assertions": [ { "id": "KA3001", "subject": "KQ1001", "predicate": "KP2001", "object": { "kind": "entity", "id": "KQ1002" }, "sources": ["KS4001"] } ] },
  "lexicon": {
    "requested_locale": "fr",
    "entries": {
      "KQ1001": { "label": "Saint Augustin", "status": "direct", "effective_locale": "fr", "layer_id": "..." },
      "KQ1002": { "label": null, "status": "missing" },
      "KP2001": { "label": null, "status": "missing" }
    },
    "coverage_counts": { "direct": 1, "fallback": 0, "missing": 2 },
    "complete_direct": false,
    "complete_usable": false
  },
  "digests": { "canonical_graph": "...", "lexicon": "...", "anchors": "..." },
  "limits": "..."
}
```

> Extrait pédagogique : le vrai `canonical_graph` contient également les métadonnées v11 obligatoires (namespace, registre des entités, propriétés, sources, etc.). Les `...` sont des placeholders, non une fixture prête à valider.

`lexicon.entries` contient *exactement* un enregistrement par KQ et KP référencé dans le graphe. Il ne contient pas les KA ni les KS : leurs identités et les références de sources demeurent dans le graphe canonique. Les fichiers dictionnaires 300+ langues restent externes : une projection n'embarque que **la langue demandée** et ses replis explicitement autorisés.

## Trois modes de lecture

- **Canonique :** KQ/KP/KA/KS, source de vérité.
- **Compact réversible (par défaut) :** graphe canonique + petite table lexicale + provenance et empreintes.
- **Markdown annoté ou épuré :** représentation calculée directement depuis le compact, non réversible seule. En cas de traduction manquante, afficher `[KQ…: non traduit]` : il est préférable de montrer un identifiant que d'inventer du sens.

Le format **verbose v0.2** (`dik.reversible-projection/1.0`) reste lisible et restaurable, et peut encore être exporté explicitement. Le compact est un nouveau contrat *applicatif diK* ; il n'est **pas** un nouveau schéma normatif du Framework v11.

## CLI

```bash
# Compact (nouveau défaut)
python -m dik projection export --project examples/demo/dik.project.json \
  --locale fr-CA --output exports/compact.json \
  --markdown exports/lecture.md --style clean

# Export historique explicite
python -m dik projection export --project examples/demo/dik.project.json \
  --locale fr --format verbose --output exports/ancien-format.json

# Un même point d'entrée supporte les deux formats
python -m dik projection verify --input exports/compact.json --project examples/demo/dik.project.json
python -m dik projection restore --input exports/compact.json --project examples/demo/dik.project.json \
  --output exports/retour-canon.json
```

L'export et le retour refusent d'écraser les fichiers déjà présents.

## Garanties et limites

- `restore(export_compact(G, L)) == G` pour les langues directes, les replis et les traductions absentes ; égalité de données JSON, pas identité des octets ni réengagement.
- Un `KQ`/`KP` absent, ajouté ou dupliqué, un libellé `missing` inventé, un statut incohérent, un qualificatif hors graphe ou une couverture falsifiée sont rejetés à la restauration détachée.
- `verify/restore --project` contrôlent les empreintes des sources puis régénèrent intégralement la projection, détectant les modifications du graphe ou des libellés même si les checksums ont été recalculés.
- Sans `--project`, les empreintes ne sont **pas une signature cryptographique**. Une restauration autonome n'authentifie pas l'auteur de la projection ; elle assure seulement la cohérence interne.
- Une vue Markdown *clean* masque les KQ connus mais laisse visibles les identifiants **sans traduction** pour éviter de masquer une lacune.
- Les textes littéraux et les citations restent des **données**, non des identités sémantiques. Les libellés rendus en Markdown sont échappés contre la formation accidentelle de tableaux et de HTML.
- Le format compact ne remplace pas le besoin futur d'une édition par patches sémantiques approuvés ou d'une qualification sur corpus massifs. L'audit initial des dictionnaires reste obligatoire et peut coûter des I/O sur un référentiel de 300 langues ; une indexation/caching sécurisé relèvera d'un jalon ultérieur.

## Vérification des gains

`PYTHONPATH=src python benchmarks/size_comparison.py` compare les deux enveloppes avec **les mêmes assertions répétées** sur un graphe synthétique, hors signature/contrat de production. Les gains dépendent du nombre de répétitions, des longueurs des libellés, de la compression et du contenu du graphe ; ce benchmark mesure la taille JSON non comprimée, pas la vitesse de traitement d'un dump Wikidata complet.
