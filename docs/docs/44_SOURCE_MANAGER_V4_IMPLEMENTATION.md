# 44 — diK V4 : registre local opérationnel de ressources

**Version : 1.0.0-alpha.8 — statut du code livré dans ce dépôt.** Ce chapitre fait autorité sur les commandes V4 et complète le contrat cible du chapitre [36](36_SOURCE_MANAGER_LOCAL_ET_REFERENCES.md).

## Décision fondamentale

diK **ne traduit pas** une langue dans une autre. Il résout `(namespace_id, KQ/KP, locale)` depuis des couches lexicales v11 effectivement auditées, ou observe un libellé Wikidata Q/P par un **exactMatch accepted** avec preuve. Un chemin `.gf` trouvé **ne donne aucun mapping KQ/P**. La découverte ne modifie jamais la source ni l'identité.

## Fonctionnalités effectivement implémentées

- `dik sources discover` : recherche **ciblée** dans les racines connues sous `--sources-root`, plus `--extra-root` explicitement autorisés ; ne suit ni liens symboliques ni jonctions Windows ; refuse des budgets invalides ; contrôle SHA-256 par blocs jusqu'au seuil annoncé.
- Crée un inventaire **non activé**, une entrée par chemin réel, avec `source_id` stable dérivé du chemin, type candidat, taille, hash éventuel, raison et racine. Les ressources de plus de `--max-hash-bytes` restent `found_unhashed`.
- Rapports sous `diK/reports/resources/DISCOVERY_UTC/` : `resource-registry.json`, `resources-found.csv`, `scan.log`. Un pointeur de fichier `resource-registry-latest.json` est remplacé atomiquement pour les traitements locaux suivants. Une exécution datée reste conservée.
- `dik sources verify --registry ...` : vérifie la présence et les empreintes du registre, sans l'activer. Une source modifiée ou disparue rend la commande **en échec** (`STALE`) ; des fichiers sans empreinte produisent un avertissement `INCOMPLETE`, non un faux statut vérifié.
- `dik coverage resolve14 --resource-registry ...` : consulte les chemins de catalogues v11 relevés dans ce registre, mais passe ensuite **chaque catalogue** aux validateurs du Framework. Une nouvelle empreinte différente est un refus ; un catalogue non valide ne devient pas source de résolution.
- `--wikidata-source-id` : pointer explicitement vers une source inventoriée *identifiée comme candidate de dump Q/P* ; l'extraction locale des libellés ne se fait qu'après les correspondances Q/P acceptées. La présence, l'empreinte et l'absence de conflits restent vérifiées. Cela **n'est pas une activation automatique de Wikidata**.
- Si `--official-root` est omis, le scanner essaie les deux dispositions connues sous `--sources-root`, dont `Kristal/kristal-public/kristals`; ambiguïté ou absence = erreur. Le nombre d'officiels dépend uniquement du portefeuille reconnu, pas du nombre de catalogues localisés.

## État de chaque référence

`state=fingerprinted` : fichier présent, taille et SHA calculés. Ce statut ne garantit ni licence, ni authenticité indépendante, ni correspondance sémantique. `state=found_unhashed` : chemin présent mais fichier au-dessus du budget. `unreadable` : lecture refusée. **`allowed_for_resolution=false` pour toutes les références à la découverte.** Les seuls catalogues donnant des formes dans `resolve14` doivent passer le contrôleur v11 indépendamment.

**Compatibilité** : les noms `GF_Lexicons_Archive/DictFre.gf`, `gf-rgl/Lexicon...gf`, `gf-wikidata-tools/extraction/data/qid-lexicon.jsonl` sont des *pistes* de sources. Ni les fichiers `.gf`, ni le `qid-lexicon.jsonl` thématique ne sont convertis implicitement en dictionnaires KQ/KP. `--wikidata-source-id` refuse une entrée de type `wikidata_qid_lexicon_candidate`.

## Limites délibérées et travail non livré

- Aucun parsing/alignement canonique automatique de `.gf`, `.pgf`, GF RGL ou Wikidata L/S/F vers KQ/KP.
- La classification des noms de dumps Q/P est heuristique : tout dump doit être vérifié par des preuves indépendantes (licence, provenance, format, couverture), et la sélection du `source_id` est explicite.
- Les révisions v11 non complètes restent non évaluables. Les 126 Kristals reconnus et 57 évaluables sont des résultats du rapport local daté, **pas un invariant du programme**.
- Pas de scan caché des lecteurs Windows, pas de trafic réseau, pas d'import automatique, pas de renommage, pas de déplacement de dumps, pas de push Git ou Render.
- La référence `source_id` dépend du chemin : un déplacement modifie l'ID ; le registre précédent permet de diagnostiquer l'ancien chemin, mais **la relocalisation par digest n'est pas encore automatique**.
- Le budget de 20 000 fichiers maximum par défaut peut tronquer un inventaire ; dans ce cas `summary.truncated=true` et les taux de couverture ne doivent pas être présentés comme exhaustifs.

Voir [45 — procédure PS7](45_COMMANDES_V4_WINDOWS.md), [46 — tests et sécurité](46_VALIDATION_ET_LIMITES_V4.md) et [41 — feuille de route](41_FEUILLE_DE_ROUTE_LOCALISATION_ET_TESTS.md).

Voir aussi [47 — Revue de sûreté du paquet V4 révisé](47_REVUE_PACK_V4_1.md).
