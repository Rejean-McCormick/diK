# 68 — Registre fédéré KQ/KP ↔ Wikidata (V5.9, candidat)

## Usage

Le registre rassemble les identités connues des Kristals officiels **sans les
remplacer**. Il indexe le statut source des rapprochements Wikidata Q/P, sans
promouvoir candidats, rejets ou correspondances approximatives.

Depuis `C:\mycode\diK\diK`, en PowerShell 7 :

```powershell
python -m dik world federation-build `
  --official-root 'C:\mycode\Kristal\kristal-public\kristals' `
  --output-dir 'C:\mycode\diK\diK\reports\federation-v59-01' `
  --min-kristals 126
python -m dik world federation-audit `
  --dir 'C:\mycode\diK\diK\reports\federation-v59-01'
python -m dik world federation-query `
  --dir 'C:\mycode\diK\diK\reports\federation-v59-01' `
  --wikidata-id Q8018
python -m dik world federation-query `
  --dir 'C:\mycode\diK\diK\reports\federation-v59-01' `
  --namespace 'kristal:exemple' --id KQ1001
```

Chaque dossier de sortie doit être **nouveau** : pas d'écrasement. L'index
SQLite et son manifeste sont autonomes et localement vérifiables, mais les
Kristals officiels restent en lecture seule. Une consultation ne modifie rien.

## Statuts retournés

- `ACCEPTED_EXACT_REVIEWED` : source Framework porte `accepted` +
  `exactMatch` + identifiant de décision et références KS, type KQ↔Q/KP↔P.
  Ce n'est **pas** une nouvelle décision de diK.
- `CANDIDATE_ONLY`, `REJECTED`,
  `ACCEPTED_SOURCE_NOT_APPROVED_FOR_QUERY` : visibilité pour revue, **aucune
  résolution exacte**.
- `DUPLICATE_NAMESPACE_LOCAL_KEY_REVIEW_REQUIRED` : même namespace+ID
  présent dans plusieurs Kristals ; blocage de fusion automatique.
- `NOT_EVALUABLE` : aucune source v11 complète/sûre ou erreur de validation ;
  l'identité est **inconnue à l'index**, pas prouvée absente du Kristal.

Les réponses n'ajoutent ni traductions, ni définitions imaginées, ni QID
inventés. Les données lexicales V5.7/V5.8 ne sont pas modifiées.

## Limites et migration

L'index utilise la logique de sélection de révision v11 disponible dans diK et
valide les sources avec le Framework vendored draft.3. Une divergence vers
draft.4 doit être étudiée à part. Les 13 langues constituent le **nouveau
périmètre cible** ; les anciens outils `*14`, les données `no` et les rapports
historiques restent conservés et **ne sont pas renommés artificiellement**.

L'inspection du registre n'est pas l'audit de toutes les couches de dictionnaire
ou de toutes les assertions des Kristals non évaluables. Aucun outil
inter-dépôts ne peut le traiter comme une permission de publication.
