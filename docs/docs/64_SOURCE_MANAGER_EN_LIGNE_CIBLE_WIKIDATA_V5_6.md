# 64 — diK V5.6 : Source Manager local **et en ligne**

**Date : 23 novembre 2026 · État : implémentation alpha.14**

## Pourquoi cette évolution

V5.5 a lu 40 sources thématiques locales, dont 46 889 entités GF-Wikidata en tableaux JSON, sans recoupement démontré avec les 1 776 liens acceptés des 57 Kristals évaluables. Les chiffres historiques sont **11 188/294 364** cellules reconnues et **69 Kristals non évaluables**. Il était insuffisant de ne rechercher des libellés que dans les ressources locales. **Un libellé absent d'un fichier local n'est pas nécessairement absent sur Wikidata.**

La V5.6 ajoute la consultation réseau **sur demande** de l'API officielle Wikidata, ciblée sur les Q/P déjà acceptés. Elle ne télécharge **pas** le dump mondial, ne consulte **pas** les KQ/KP non reliés et ne demande pas une traduction langue→langue.

## Sources en ligne : rôle et droits

| Fournisseur | Adresse | État diK V5.6 | Identité et droits |
|---|---|---|---|
| Wikidata Action API | `https://www.wikidata.org/w/api.php` | **Connecteur implémenté** | Q/P explicites, labels par langue, CC0 |
| Kaikki / Wiktionary | `https://kaikki.org/dictionary/` | Référencé / **non téléchargé** | Lexèmes par langue, CC-BY-SA / GFDL ; aucune équivalence KQ/KP prouvée |
| GF Resource Grammar Library | `https://github.com/GrammaticalFramework/gf-rgl` | Référencé / **non téléchargé** | Morphologie et grammaires, parties LGPL/BSD ; ce n'est pas un registre KQ/KP |

Les fournisseurs référencés ne deviennent pas des dictionnaires autorisés. Le rôle d'un adaptateur Kaikki (formes, sens, licences) et d'un connecteur GF (inflexion, paradigmes) **reste à réaliser** ; le simple téléchargement ne résoudrait pas l'absence de liens sémantiques.

### Sources officielles consultées

- https://www.wikidata.org/wiki/Wikidata:Data_access (Action API, règles de robots, maxlag, User-Agent, CC0)
- https://www.wikidata.org/wiki/Wikidata:Licensing (CC0)
- https://www.mediawiki.org/wiki/Wikibase/API (paramètres `wbgetentities`, `ids`, `languages`)
- https://kaikki.org/dictionary/ (Wiktionary sous CC-BY-SA/GFDL)
- https://github.com/GrammaticalFramework/gf-rgl/blob/master/LICENSE (licences des parties RGL)

## Flux implémenté

```text
126 Kristals officiels (v11 sélectionnée)
             │
    crosswalk exactMatch accepted + preuves KS
             │  namespace conservé ; liens contradictoires écartés
             ▼
       liste unique de Q/P
             │   consentement explicite --allow-network
             ▼
Wikidata Action API wbgetentities (HTTPS, 25 IDs/requête)
    props=labels ; languages=les 14 codes exacts ; aucun fallback
             │
             ▼
réponses JSON immuables : diK/reports/sources/online/wikidata_v56/blobs/<SHA>.json
             │   SHA-256 + statut + URI source + date + CC0
             ▼
index.json (checkpoint atomique / reprise incrémentale)
             │   vérification des blobs et des identités
             ▼
coverage resolve14 --online-index ...
             │
             ├─ wikidata_online_observations_candidates.csv
             └─ wikidata_online_potential_coverage.csv
```

**Interdictions :** requête par terme, suffixe numérique KQ/Q, similitude lexicale, conversion `nb→no`, `jp→ja`, traduction entre langues, lecture de `descriptions` comme formes, approbation implicite, publication dans le canon, mutation de dictionnaires.

## CLI nouvelle ou étendue

```powershell
# Sans réseau : voir les fournisseurs et les licences
py -3 -m dik sources online-catalog

# Avec consentement réseau explicite et cadre des 126 officiels :
py -3 -m dik sources online-fetch `
  --official-root 'C:\mycode\Kristal\kristal-public\kristals' `
  --dik-root 'C:\mycode\diK\diK' --min-kristals 126 --allow-network

# Après cette opération, l'audit peut relire le cache sans réseau :
py -3 -m dik coverage resolve14 `
  --official-root 'C:\mycode\Kristal\kristal-public\kristals' `
  --sources-root 'C:\mycode' --dik-root 'C:\mycode\diK\diK' `
  --min-kristals 126 `
  --online-index 'C:\mycode\diK\diK\reports\sources\online\wikidata_v56\index.json'
```

Le lanceur `TOUT_AUTO_PS7.ps1` installe V5.6 puis donne le consentement `--allow-network`, avant de faire l'audit. Il relance le registre local, puis écrit `DIK_V5_6_BILAN_*.zip`. Sans accès réseau, il peut créer le bilan à partir du cache disponible ; l'absence de téléchargement est indiquée, jamais présentée comme « aucun mot sur Wikidata ».

`--max-ids` (2500 par défaut) est un plafond par passage ; `--batch-size` vaut 25 par défaut (maximum 50). L'appel HTTP est borné et réessaie les codes temporaires (429/5xx), avec `maxlag=5`, `User-Agent` identifiable et pauses. `--refresh` est **optionnel** ; sans ce drapeau, les Q/P déjà capturés sont réutilisés et vérifiés, non retéléchargés. Le fournisseur ne reçoit que des Q/P, sans noms de Kristals, namespaces, chemins ni textes locaux. **Toute requête réseau expose néanmoins l'adresse IP du poste au fournisseur.**

## Niveau de preuve et métriques

Une réponse Wikidata HTTPS dont le SHA est enregistré + un crosswalk accepté avec KS permettent une **observation candidate**, non une publication ni une forme morphologique prête à l'emploi. Les redirections ou IDs inattendus sont signalés pour revue. Les formes retournées ne modifient pas les catégories `catalogue_courant`, `catalogue_raccorde`, `wikidata_observe`, `conflit` et `non_resolu` du rapport historique.

Deux nombres distincts sont produits :

- **Couverture validée historique :** basée sur les sources explicitement qualifiées et les règles existantes ; V5.6 ne l'augmente pas implicitement.
- **Potentiel candidat en ligne :** nombre de cellules ID-langue avec un libellé Wikidata exact observé et nombre de cellules non résolues qui possèdent désormais cette observation. Ces formes exigent encore une décision de publication et, selon la langue, une vérification linguistique.

L'index JSON local contient les labels en clair et **ne doit pas être partagé tel quel**. `dik sources export-v56` expurge les formes et chemins des nouveaux CSV dans le ZIP de bilan. Les sources externes restent sous leurs conditions respectives.

## Tests, limites et suites

Les tests du connecteur n'emploient **aucun réseau réel** : transport simulé, consentement, batchs, reprise, réponse incomplète, SHA altéré, redirection, `no` sans repli `nb`, absence de promotion et ZIP expurgé. L'absence de réseau en environnement de préparation empêche de confirmer le comportement HTTP réel sur Windows : seul le bilan lancé localement prouvera le nombre de Q/P obtenus et le potentiel candidat.

**À venir :** gouvernance formelle d'admission des labels Wikidata, téléchargement sélectif conforme des fichiers Kaikki avec alignement sémantique explicite, GF morphologique par lexème approuvé, Wikidata L/S/F et récupération documentée des 69 Kristals non évaluables. Pas d'affirmation de couverture nouvelle avant audit réel.
