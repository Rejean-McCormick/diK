# 36 — Source Manager local : référencer sans déplacer

**Statut : contrat cible proposé, pas une commande de découverte déjà livrée dans V3.** Le `Source Manager` est prévu par [02 Architecture](02_ARCHITECTURE.md) ; son index local opérationnel persistant et ses connecteurs ne sont pas démontrés par le dernier scan.

## 1. Séparation entre inventaire, admission et activation

La découverte n'autorise pas l'utilisation :

`source découverte` → `vérifiée sur disque` → `format parsé` → `provenance/licence vérifiées` → `alignement accepté` → `source activée`.

Le registre peut contenir des objets **non activables** ; cela évite de cacher des ressources déjà présentes tout en interdisant leur usage par hasard. L'index est dérivé et reconstruisible ; les fichiers maîtres restent en place.

## 2. Clé de source et résolution du chemin

Clé documentaire proposée : `(source_id, snapshot_id, content_sha256, kind)` ; séparer `logical_name`, `source_uri` éventuelle, `windows_path` absolu et `path_scope`. Ne jamais mettre un chemin Windows absolu **dans** le champ `path` du catalogue Framework v11 : ce champ est relatif au catalogue, et l'intégrité de la couche fait partie du contrat v11.

Une source hors catalogue v11 peut rester référencée par un manifeste **propre à diK** ; sa transformation en couche v11 exige un processus d'import/publish distinct, autorisé et reproductible. « Pointer » n'est pas un raccourci pour violer le schéma Framework.

## 3. Champs minimaux recommandés

| Champ | Sens | Contrôle |
|---|---|---|
| `source_id` / `kind` | Identifiant stable local, type (wikidata_qp, wikidata_lsf, gf_lexicon, framework_v11, etc.) | Type connu ou non activable |
| `declared_path` | Piste issue d'un index / configuration | Ne suffit pas pour `found=true` |
| `resolved_path` | Chemin canonique validé au moment du scan | Racine autorisée, aucune traversée de jonction |
| `path_scope` | Racine autorisée et nature de l'accès | Uniquement `read_only` pour discovery |
| `sha256`, `size_bytes` | Empreinte et taille locales | Empreinte ≠ preuve de provenance externe |
| `source_snapshot`, `license`, `attribution` | Origine / conditions | Non nulles pour une publication, revues manuellement |
| `observed_at_utc` | Date d'observation | Ne remplace pas un contrôle actuel |
| `namespace`, `alignment_evidence` | Liaison vers KQ/KP, si existante | N'admettre qu'une décision explicite et vérifiable |
| `state`, `reasons`, `enabled` | Parcours de qualification et activation | `enabled=false` par défaut |

Le [modèle JSON](../examples/resource-locator/source-registry.example.json) est **illustratif uniquement** ; il ne crée aucune nouvelle option CLI ni un schéma Framework.

## 4. Gestion des chemins Windows

- Résoudre les racines **par configuration explicite**, puis par profils connus (`C:\mycode`), puis produire des candidats non confirmés.
- Pour chaque objet, valider type réel, taille, limite de lecture, extension puis contenu ; ne pas se fier seulement à l'extension.
- Refuser traversée hors racine, liens symboliques/jonctions non autorisés, périphériques, pipes et chemins réseau non autorisés.
- Ne jamais lire un dump de plusieurs gigaoctets en RAM ; streaming, budget disque/CPU et contrôle de hachage par blocs.
- Le relocaliseur peut rechercher `source_id + digest` si un chemin change ; **n'active pas** automatiquement une copie si plusieurs correspondances existent.
- Cache dérivé SQLite ou JSONL reconstituable ; la preuve et la configuration restent immuables par snapshot.

## 5. Relations de provenance

Un résultat de résolution doit pouvoir expliquer : `source_id -> file_sha256 -> import_snapshot -> crosswalk_decision -> (namespace,KQ/KP,locale) -> forme`. Les décisions négatives et les ambiguïtés restent dans le ledger. Ne pas exporter de données privées simplement parce qu'un rapport les liste.

## 6. Exploitation, reproductibilité, publication

Le Source Manager propose un **dry-run** et un rapport `resources-found.csv` / `resources-rejected.csv`. Il écrit seulement dans le dossier de rapports de diK. Une activation ultérieure doit utiliser une configuration versionnée, une approbation et un test isolé, puis idéalement une nouvelle couche immuable. Les cheminements et privilèges Windows sont documentés dans [42](42_EXPLOITATION_WINDOWS_PS7.md).

## 7. Critères minimaux d'admission

Une ressource ne devient `active` que si la source existe, le format est accepté, le hash est enregistré, les droits sont contrôlés, la paire KQ/KP est prouvée, la locale est mappée, les conflits sont gérés et la politique de priorité l'autorise. Un `.gf` ne devient pas directement `catalog.json`; un JSONL issu d'une extraction Wikidata ne devient pas un dump global.

## Actualisation V4 — code opérationnel

Le contrat cible du présent chapitre reste pertinent, mais **une première implémentation de découverte et de registre existe depuis alpha.8**. `dik sources discover` enregistre les chemins, types de fichiers candidats et SHA locaux sous `diK/reports/resources` ; `dik sources verify` vérifie ces références ; `resolve14 --resource-registry` utilise ces pointeurs **uniquement** pour sélectionner les catalogues v11 qui repassent les audits Framework. Aucune activation GF ou publication automatique. Consulter [44](44_SOURCE_MANAGER_V4_IMPLEMENTATION.md) pour le statut réel et les limites.
