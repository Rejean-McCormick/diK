# Validation effective — diK 1.0 spécification candidate.2

**Il s'agit de tests de DOCUMENTATION. Aucun code du futur logiciel diK 1.0 n'a été qualifié.**

## Réalisé sur cette révision

| Vérification | Résultat |
|---|---|
| Schémas applicatifs *proposés* + exemples | 5/5 valides |
| Cas négatifs JSON Schema | 3/3 rejetés |
| Oracles documentaires machine-lisibles | 27/27 PASS |
| Registre de traçabilité | 87 exigences réelles, 174 futurs tests positifs/négatifs **NOT_RUN** |
| Catalogue initial TCK | 30 cas **NOT_RUN** |
| Empreintes `SOURCE_LOCK.json` (sources épinglées) | 13/13 vérifiées |
| Archives sources épinglées | 5/5 vérifiées |
| Fixtures Framework v11 contre schémas officiels | 5/5 validées |
| Contrôle `--strict` avec sources présentes | PASS |
| Contrôle `--strict` sans sources | FAIL (comportement voulu) |
| Contrôle `--strict` avec source altérée | FAIL (comportement voulu) |
| Tests historiques de diK 0.3.0 | 36/36 PASS, **pas diK 1.0** |

## Reproduire le contrôle documentaire

```bash
python -m pip install 'jsonschema>=4.21,<5'
python tools/verify_reference_vectors.py
python tools/validate_documentation.py
DIK_SOURCE_DATA_ROOT=/mnt/data KRISTAL_FRAMEWORK_ROOT=/mnt/data/work_kristal_v11_draft3 \
  python tools/validate_documentation.py --strict
```

Les chemins `/mnt/data/...` sont ceux de l'environnement de vérification d'origine ; sur un autre poste, fournir les répertoires sources correspondants tels qu'ils figurent dans `SOURCE_LOCK.json`. La commande sans `--strict` peut indiquer `PASS` **tout en avertissant que les sources sont indisponibles** ; elle ne remplace jamais la commande stricte.

## Restant avant gel puis release 1.0

- **Approbation humaine** de l'ADR-0003 et des contrats applicatifs cibles ; budgets performance ratifiés après bench réel.
- Tests produit sur tous les P0/P1, 30 TCK initiaux et 87×2 exigences ; pas de `NOT_RUN` bloquant.
- Application réelle de diK 1.0 : conciliation multisource, import massif, migrations via producteur, UI/API, 301 langues sparse, sécurité/crash/reprise.
- Compatibilité qualifiée avec les versions exactes de Framework, Authoring Kit et Integration Pack.
- Benchmark du produit réel contre les seuils décidés et preuve de restauration historique.

**Statut :** documentation candidate.2 plus précise, avec contrôle anti-drift vérifiable. Ni version finale du logiciel ni API applicative formellement gelée.
