# diK — Décisions d'architecture (ADR, version 0.1.0)

## ADR-001 — Identifiant de référent sémantique (IRS)
- Décision : « IRS » est le terme générique pour une identité d'entité/concept ; KQ est sa forme Kristal ; QID la forme Wikidata. `KP` désigne les propriétés ; `KA`, `KS` leurs familles respectives.
- Conséquence : l'UI peut utiliser « identifiants sémantiques » plutôt que « Q » ; les contrats conservent leurs IDs techniques.

## ADR-002 — Un registre interne + correspondances externes
- Décision : KQ/KP sont canoniques dans le namespace ; Wikidata Q/P restent des références externes avec relations typées, preuve et revue.
- Rejeté : réplication des numéros Wikidata et mutation d'un KQ lorsque Wikidata ajoute un Q.

## ADR-003 — Stockage portable file-backed, calcul dérivé
- Décision : des fichiers immuables versionnés et un catalogue constituent le canon ; un index SQLite ou moteur de recherche est effaçable et reproductible.
- Rejeté : serveur central nécessaire pour lire un Kristal.

## ADR-004 — Qualité lexicale ≠ similarité ≠ identité
- Décision : même libellé et traduction ne valent pas même concept ; résolution inverse à candidats et validation obligatoire des équivalences.
- Conséquence : alias polysémiques et homographes multiples sont conservés.

## ADR-005 — Complétude stricte et de secours séparées
- Décision : couverture par KQ et KP, langue par langue ; direct / fallback / manquant / conflit ; pas de score 100 % sur inventaire incomplet.

## ADR-006 — Migration non destructive
- Décision : produire un plan et une nouvelle révision ; ancien canon, preuves et engagements historiques intacts ; toute mutation déléguée à un producteur de Kristals explicitement autorisé.

## ADR-007 — Sécurité, licence et confidentialité
- Décision : import local privilégié. Provenance, attributs et conditions de réutilisation des sources externes conservés ; aucune exposition de corpus privé par une requête de recherche par défaut.
