# COV-/LEX-/ID-/SEC- — Scanner lexical intégré 14 langues (2026-11-21)

## Périmètre

Commande **native** : `dik coverage scan14`. Les cibles sont **exactement** :

`en, fr, es, de, nl, sv, da, no, nn, fi, et, af, it, pt`

- **Source de vérité** : manifeste `dik.project.json` choisi, registre KQ/KP, catalogue linguistique et couches auditées par le moteur diK Framework v11 (`dictionaries.audit`, SHA-256 et crosswalk exactMatch révisé).
- **Portée** : tous les KQ/KP enregistrés dans ce projet, y compris ceux hors du graphe actif (`dans_graphe` dans CSV).
- **Résolution** : priorité lexicale maximale, puis ordre de repli déclaré. Une langue non déclarée a un statut distinct d'un manque confirmé dans un catalogue configuré. Les conflits invalidant un catalogue font **échouer** l'audit, ils ne deviennent pas un faux résultat numérique.
- **Sortie** : dossier **nouveau** exclusivement en dehors du projet audité; publication après contrôles et création des rapports, sans altération des données amont.

## Windows PowerShell 7

```powershell
$repo = 'C:\mycode\diK\diK'
Push-Location $repo
try {
    $env:PYTHONPATH = Join-Path $repo 'src'
    py -3 -m dik coverage scan14 `
      --project 'examples/demo/dik.project.json' `
      --handoff 'integrations/unesco-mt1-10/handoff.json' `
      --konstellation 'C:\mycode\Konstellation\Konstellation' `
      --corpus 'data/demo.pack.json' `
      --out (Join-Path $env:USERPROFILE ('Downloads\DIK_SCAN14_' + (Get-Date -Format 'yyyyMMdd-HHmmss')))
    if ($LASTEXITCODE -ne 0) { throw 'Scanner diK échoué' }
}
finally { Pop-Location }
```

**Remplacer le chemin `--project` par le `dik.project.json` d'un vrai projet**. Le projet `examples/demo` n'est qu'un contrôle fonctionnel. La liste des 14 langues est également vérifiable avec `--spek <dossier-ou-zip-Spek>` ; l'option `--handoff` vérifie explicitement le manifeste diK reçu. Une exécution sans `--konstellation` reste un audit autonome diK.

## Rapports

| Fichier | Sens |
|---|---|
| `rapport.json` | Provenance, SHA-256 des sources, compte de références, tableau par langue, limites et avertissements |
| `couverture_14_langues.csv` | Statuts totaux par langue dans le projet sélectionné |
| `registre_14_langues_KQ_KP.csv` | Toutes les identités enregistrées × 14 locales, avec mot, couche, langue source et action |
| `lacunes_14_langues.csv` | Les cellules qui ne sont pas des traductions **directes** (`repli`, `manquant`, `langue_non_configuree`) |
| `couches_lexicales_auditees.csv` | Couches réelles disponibles, source, SHA-256, type et nombre d'enregistrements |
| `inventaire_termes_konstellation.csv` | **Optionnel** : textes du pack, non alignés au registre diK |
| `libelles_multilingues_dans_pack.csv` | **Optionnel** : langues déclarées sur les libellés du registre du pack |
| `chaines_interface_candidats.csv` | **Optionnel**, heuristique **non exhaustive** des littéraux Svelte/Astro |

Les CSV utilisent UTF-8 BOM et `;`, compatibles avec Excel en configuration francophone.

## Interprétation indispensable

1. Une **entrée de registre** n'est pas un mot courant, ni une entrée lexicale réelle. Le scanner mesure les **identités KQ/KP du projet choisi**, non tout le vocabulaire du monde ni toutes les ressources diK possibles.
2. Une **langue non configurée** dans le catalogue sélectionné n'atteste pas l'absence de traductions dans vos dictionnaires externes.
3. Les traductions de repli sont des libellés utilisables mais non directs. Le scanner n'est pas un traducteur automatique.
4. Les noms et chaînes de Konstellation sont **inventoriés uniquement** : aucune identité sémantique n'est déduite d'une similarité. Un CSV `exactMatch;accepted` fabriqué par un tiers n'est pas un crosswalk révisé et ne sera pas accepté comme preuve.
5. Le contrôle des droits, de la qualité des traductions et la qualification des 14 langues sur la collection entière sont **hors périmètre**. Il faut un vrai catalogue/revue pour les prouver.

## Portée des tests

8 nouveaux tests ciblés positifs et négatifs; suite `pytest` diK sur copie isolée. Voir `VALIDATION.md` pour les chiffres réels et les travaux non exécutés. Aucun schéma Framework vendorié ou registre historique modifié.


<!-- DIK-DOCS-LOCAL-1 -->
## Actualisation documentaire — 22 novembre 2026

Ne pas confondre `scan14` de projet, `kristals14` V2 et `resolve14` V3 sur les 126 Kristals officiels. Voir le [guide maître](../DIK_GUIDE_MAITRE_RESOLUTION_LOCALE.md), les [chapitres 34–43](../DIK_GUIDE_MAITRE_RESOLUTION_LOCALE.md) et l’[ADR DIK-LEX-2](../decisions/ADR-DIK-LEX-2-localiser-et-referencer.md). Ce complément est documentaire et ne change pas les contrats du Framework.
