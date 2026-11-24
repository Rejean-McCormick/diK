# 49 — Observation conservatrice des QID Wikidata et frontières GF

**Implémentation alpha.9 / V5. Aucune traduction entre langues. Aucune publication automatique.**

## Résolution attendue

`(namespace_id, KQ/KP)` → `external-crosswalk.json` exactMatch `accepted` et preuves KS → `Q/P` Wikidata → **label explicite de la locale demandée** dans une source vérifiée. Un label n'est pas une identité. Les `L/S/F` de Wikidata sont des lexèmes/sens/formes ; ils ne sont **pas** synonymes des `Q/P` d'entités et de propriétés. Les fonctions GF ne sont pas davantage des KQ/P.

## Nouvelle option d'observation (pas de résolution)

```powershell
py -3 -m dik coverage resolve14 `
  --official-root 'C:\mycode\Kristal\kristal-public\kristals' `
  --sources-root 'C:\mycode' `
  --dik-root 'C:\mycode\diK\diK' `
  --resource-registry 'C:\mycode\diK\diK\reports\resources\resource-registry-latest.json' `
  --observe-qid-lexicon
```

Ce mode repère l'unique source `wikidata_qid_lexicon_candidate` du registre, vérifie **avant lecture** son chemin et SHA-256, puis examine uniquement les libellés explicitement présents, soit au format `{"qid":"Q...","labels":{"fr":"..."}}`, soit au format réel `{"Q...":{"fr":"..."}}`. Les identifiants de langue sont exacts et aucun repli de `no` vers `nb` ou `nn` n'est effectué. Il rejette une observation en conflit pour le même Q/P et la même locale. Il ne dérive jamais un label depuis `lemma`, `forms`, `gf_function`, ou une proximité de graphie.

La sortie `wikidata_qid_observations_candidates.csv` conserve seulement les observations dont le Q/P est déjà lié à un KQ/KP par une correspondance **acceptée et auditée**. Celles-ci restent étiquetées `observation_non_publiee` : **elles ne modifient aucun total** de `catalogue_courant`, `catalogue_raccorde` ou `wikidata_observe`.

Le `rapport.json` consigne `wikidata_qid_lexicon` (format, compteurs, champs rencontrés, limites) et `totaux.wikidata_qid_observations_non_publiees` séparément des formes effectivement résolues.

### Pourquoi ne pas convertir directement le lexique QID en dictionnaire ?

Le fichier `qid-lexicon.jsonl` de 60 083 octets a été fourni le 23 novembre 2026 : **50 lignes JSONL**, chacune au format `{"QID":{"locale":"libellé"}}`, soit **1 888 libellés** et **155 codes de langue**. Le lecteur V5.1 reconnaît maintenant ce schéma, mais il ne crée ni correspondance KQ/KP↔Q, ni approbation de droits. Sur le rapport V5 reçu, aucun des 50 QID ne recoupe les QID acceptés des 57 Kristals évaluables ; il n'y a donc pas de gain de couverture à attendre de ce fichier seul. Les sources nécessaires à une résolution plus large restent à qualifier.

## Grammatical Framework

- Le localisateur trouve `Dict*`, `Lexicon*`, `Irreg*`, fichiers `*.gf` et `*.pgf`.
- Le RGL apporte des mécanismes de morphologie, de syntaxe et des lexiques propres à GF ; il ne remplace ni les identifiants canoniques des Kristals ni les décisions d'alignement.
- **Non implémenté dans V5 :** lien revu GF↔KQ/KP ; compilation et appel de paradigmes GF pour réaliser une forme pour une identité vérifiée ; preuve des contraintes de licence, langues et versions des modules.
- Les archives, snapshots et fichiers de test ne deviennent jamais prioritaires du seul fait de leur découverte.

## Suite de la qualification

1. Lire sur le poste les vrais champs du JSONL QID et d'un échantillon de dictionnaires GF, sans transférer leurs contenus complets.
2. Identifier les artefacts de publication/droits et le contrat exact GF↔KQ/P.
3. Ratifier les correspondances via le Framework, puis construire l'adaptateur de réalisation grammaticale.
4. Reprendre les 69 Kristals officiels sans v11 exploitable, par famille de cause, sans créer des identités inventées.
5. Relancer le portefeuille de 126 officiels × 14 langues et vérifier séparément « observé », « approuvé » et « non résolu ».
