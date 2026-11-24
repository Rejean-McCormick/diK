# 54 — Architecture cible : lecture des ressources Wikidata sans traduction (V5.3)

> **Mise à jour du 23 novembre 2026 :** les composants dont les formats sont prouvés sont implémentés dans **alpha.11**. Lire le [chapitre 61 — état réellement livré](61_IMPLEMENTATION_EFFECTIVE_V5_3.md). Les parties visant des schémas locaux encore inconnus demeurent des spécifications, non des fonctionnalités certifiées.

**Spécification proposée, non implémentée au 23 novembre 2026.** Complète [02 — architecture](02_ARCHITECTURE.md), [36 — Source Manager](36_SOURCE_MANAGER_LOCAL_ET_REFERENCES.md), [37 — connecteurs](37_CONNECTEURS_WIKIDATA_GF.md) et [52 — état V5.2](52_AUDIT_WIKIDATA_THEMATIQUE_V5_2.md).

## Flux d'exécution cible

```text
126 Kristals officiels ──► registres/crosswalks v11 audités
       │                         │
       │                  (namespace_id,KQ/KP)
       │                         │ exactMatch accepted + preuves KS
       │                         ▼
       │                    Q/P autorisés ──────────────────────┐
       │                                                        │
Source Manager (5 269 pointeurs, inventaire)                    │
       │                                                        │
       ├─► source intacte? SHA / taille / racine / licence      │
       ├─► profil de schéma typé (jamais déduit du seul nom)    │
       ├─► parseur JSONL streaming + checkpoint                │
       ├─► extracteur Q/P (champ explicite documenté) ─────────┤
       └─► extracteur de libellés avec locale explicite         │
                                                                ▼
                     jointure exacte Q/P + locale + namespace
                                      │
                       ┌──────────────┴──────────────┐
                       ▼                             ▼
                diagnostic candidat            conflit/refus
                       │
                  revue provenance,
                  licence et preuve
                       │
          activation explicite FUTURE seulement
                       │
          compositeur lexical V11 qualifié
                       ▼
             forme affichable dans diK
```

## Modules conceptuels et responsabilités

| Étape / rôle | Entrée | Sortie | Interdiction |
|---|---|---|---|
| `resource_pointer` | Registre V4/V5 | Source, empreinte, racine | Ne transforme pas `found` en `active` |
| `schema_probe` | Échantillons vérifiables du contenu | Profil typé + version + confiance | Ne conclut pas « aucun Q/P » si format inconnu |
| `adapter_registry` | Profil validé, version | Un adaptateur déterministe sélectionné | Ni correspondance par nom de fichier, ni conversion implicite |
| `id_extractor` | Enregistrement conforme au schéma | Q/P, rôle du champ et preuve d'extraction | Ne confond pas sujet/propriété/valeur d'une assertion |
| `lexical_extractor` | Champ textuel explicite, locale | Forme candidate + langue exacte | Ne crée pas de mot depuis des claims, tokens GF ou une autre langue |
| `accepted_link_index` | Crosswalks audités officiels | `(namespace, KQ/KP) ↔ Q/P` acceptés | Ne promeut pas les liens `candidate` |
| `join_and_conflicts` | Identités + observations | Candidats ou conflits avec provenance | Ne choisit pas arbitrairement un terme contradictoire |
| `rights_gate` | Provenance/versions/licence/revue | admissible ou refus motivé | N'infère pas les droits depuis un SHA |
| `reporter` | Diagnostics complets | JSON/CSV/journal + manifeste reproductible | N'augmente pas la couverture avec un candidat |

Les noms ci-dessus sont **conceptuels** ; ils ne constituent **pas** des commandes CLI déjà disponibles. Le futur développeur pourra les mapper à `src/dik/source_qualification.py`, `src/dik/wikidata_thematic.py` et `src/dik/resolution14.py` sans rupture de contrat.

## Strates de confiance — ne pas les raccourcir

`REFERENCED` (pointeur vérifié) → `SCHEMA_VERIFIED` (identité et champs lisibles) → `IDENTIFIER_OBSERVED` (Q/P explicite) → `ACCEPTED_LINK_OVERLAP` (Q/P recoupe lien officiel accepté) → `LEXICAL_CANDIDATE` (locale + forme explicitement attestées) → `ELIGIBLE` (droits/provenance et revue) → `ACTIVE` (autorisation de publication versionnée).

Ce sont des **états cibles**. L'implémentation V5.2 n'expose pas cette machine à états ; son `TRIAGE_ONLY` reste le statut courant. Un artefact peut être `SCHEMA_UNKNOWN`, `PARTIAL` ou `CONFLICT` à n'importe quelle étape, sans promotion forcée.

## Priorités lexicales et absence de traduction

L'ordre de sélection des couches lexicales v11 reste celui du catalogue validé par le Framework. Le futur observateur Wikidata ne court-circuite **ni le catalogue courant ni les priorités**. Il n'existe pas de `source_locale` dans la demande `(namespace, KQ/KP, target_locale)` : pas de FR→EN, pas de EN→DE, ni de repli `nb`→`no` par défaut.

## Politique d'utilisation des sources

- **`identity-candidates.jsonl`** : candidats de liens, **pas** preuve d'identité ni lexique actif.
- **`statements.jsonl`** : déclarations structurées ; les Q/P pouvant y figurer comme sujet, prédicat ou valeur doivent garder leur rôle. Aucune valeur d'assertion ne devient label.
- **`City.jsonl`, `Country.jsonl`, `University.jsonl`, `Part_of world.jsonl`** : jeux GF-Wikidata thématiques à schéma **non validé avec les données présentes dans le ZIP**. Leurs formes possibles doivent être inspectées avant d'écrire un adaptateur.
- **`qid-lexicon.jsonl`** : schéma `{"Q...":{"fr":"..."}}` confirmé pour 50 lignes ; sans intersection prouvée avec les Q/P acceptés de l'audit précédent.
- **Wikidata L/S/F et GF RGL/PGF** : **frontières distinctes**, décrites au chapitre 57. Une ressource GF trouvée ne prouve aucune liaison KQ/P↔fonction GF.

## Déploiement et sécurité

L'inspection se fait hors-ligne, en lecture seule, sous des racines explicitement autorisées, sans suivi de liens/jonctions, sans import au dépôt, sans requête réseau et sans modification des dictionnaires. Les artefacts dérivés (`schema-profiles`, index de jointure, checkpoints et rapports) sont créés uniquement sous `diK/reports/` avec chemins et empreintes enregistrés. Les chemins absolus sont sensibles au partage externe ; produire un ZIP expurgé si nécessaire.

**Contrats complémentaires :** [55](55_CONTRATS_SCHEMAS_JSONL_V5_3.md), [56](56_STREAMING_REPRISE_SECURITE_V5_3.md), [57](57_PREUVES_KQ_QP_LSF_GF_V5_3.md), [58](58_STATUTS_ET_RAPPORTS_V5_3.md).
