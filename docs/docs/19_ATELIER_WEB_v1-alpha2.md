# Atelier diK — Interface locale v1.0 alpha.2

## Base du design

Référence : `guide-architecture-interfaces-ia-v2(3).zip`, guide `senior-interface-ux-patterns-v2`. Il prescrit l'organisation par **intentions et objets métier**, pas un onglet par service. Principes retenus : UX-01, UX-03, UX-05, UX-06, UX-07, UX-08, UX-09, UX-11, UX-12, UX-14, UX-15 et UX-18.

### Parcours quotidien (UX-01, UX-05, UX-07)

1. **Retrouver un concept** par terme dans un index (candidats) ou directement par KQ/KP.
2. **Examiner la fiche** : identifiant stable, libellé local ou absence, statut `direct`/`fallback`/`missing`, correspondances externes `accepted` ou `candidate`, utilisations dans les assertions.
3. **Corriger une traduction** si le mode curation a été activé par l'opérateur : créer un *nouveau* catalogue candidat, revoir son chemin et son SHA-256. Aucun remplacement du canon.
4. **Inspecter la complétude** : une matrice par page de 25 langues, détails KQ/KP manquants avec lien vers leur fiche.
5. **Lire le Kristal** en vue épurée ou annotée, ou exporter son enveloppe JSON compacte contenant le canon pour restauration fidèle.

Ce parcours remplace le dashboard alpha.1 orienté « recherche + 40 premières langues ». L'accueil n'est pas un écran de statistiques décoratives (UX-08), mais un point de départ vers la recherche.

### Navigation (UX-03, UX-09, UX-11)

| Espace | Usage | Actions |
|---|---|---|
| Concepts et traductions | Travail principal | chercher, consulter KQ/KP, corriger lexicalement si autorisé |
| Complétude | Priorisation des manques | parcourir langues, ouvrir une fiche manquante |
| Lire un Kristal | Lecture et projection | choisir vue clean/annotated, exporter JSON réversible |
| Diagnostics | Secondaire | inspection technique et API en lecture seule |

Le changement de langue conserve la fiche sélectionnée / le contexte de la vue. Pas de pages distinctes pour chaque commande CLI.

### Confiance / refus de drift

- **KQ/KP toujours canoniques**; libellés uniquement dérivés. Une vue `clean` cache les codes à l'écran, pas dans le JSON d'export.
- **Aucun mapping Wikidata accepté par l'UI**. La recherche retourne des candidats non approuvés.
- L'API est en lecture seule. L'unique POST `/curate` n'est disponible qu'avec `--workspace` explicitement passé au démarrage; il produit une nouvelle révision immuable du catalogue en dehors de la racine du projet.
- Les noms de réviseurs sont déclaratifs. Ce n'est **pas** une gouvernance multi-acteur authentifiée; aucune signature cryptographique n'est produite.
- Protection locale : liaison uniquement `127.0.0.1`, contrôle `Host`, contrôle `Origin` quand fourni, jeton CSRF aléatoire, confirmation, taille des requêtes bornée, CSP, escaping HTML, blocage des frames, pas de cookies ni scripts externes.
- Pour tout contrôle d'intégrité complet, l'API diagnostics et les opérations d'audit/curation passent par les validations du Framework 11.0.0-draft.3. Le résumé d'accueil lit seulement les références validées du graphe/registre (pas les centaines de dictionnaires à chaque ouverture).

### Performance et limites

- Pagination à **25 langues** par réponse Web plutôt que de calculer 300+ langues pour l'écran initial.
- La recherche inverse utilise SQLite; l'index est généré séparément par la commande `dik index build`. L'interface ne prétend pas le reconstruire automatiquement.
- L'aperçu textuel ne montre que 30 assertions. Les exports Web sont limités (taille du graphe source <= 25 Mo; JSON résultant <= 40 Mo) : utiliser la CLI pour les corpus massifs.
- L'interface n'est pas une autorité canonique, une solution multi-utilisateur ou un éditeur de conversions legacy.

## Exécuter

```bash
PYTHONPATH=src python -m dik index build \
  --project examples/demo/dik.project.json --output /tmp/dik-local-index.sqlite
PYTHONPATH=src python -m dik serve \
  --project examples/demo/dik.project.json --index /tmp/dik-local-index.sqlite --port 8765
# Curation locale facultative : dossier extérieur au projet
PYTHONPATH=src python -m dik serve \
  --project examples/demo/dik.project.json --index /tmp/dik-local-index.sqlite \
  --workspace /tmp/dik-revisions --port 8765
```

## Scénarios de contrôle (UX-14)

1. Retrouver « Saint Augustin » en français; le résultat unique est affiché comme **candidat**, ouvrir la fiche `KQ1001`; Wikidata Q8018 est clairement une **correspondance externe**.
2. En français, `KQ1002` n'a pas de libellé; afficher l'absence, ne pas inventer une traduction.
3. Dans une matrice de 301 langues déclarées, pouvoir atteindre la page 13 et ouvrir une fiche de concept manquant.
4. Lire le graphe en mode épuré, puis annoté; télécharger son enveloppe et restaurer le même canon.
5. Sans `--workspace`, `POST` est refusé. Avec `--workspace`, sans jeton ou depuis une origine étrangère, aucune création. Avec jeton correct, publier un **nouveau catalogue** et vérifier que graphe, registre, crosswalk et catalogue initial conservent leurs empreintes.

Ces tests automatiques sont dans `tests/test_webapp_workbench.py`. Ils ne remplacent pas une revue UX humaine ou une validation en production.
