# 45 — Exploiter le Source Manager V4 sous Windows / PS7

Le dépôt installé est supposé dans `C:\mycode\diK\diK`. Les commandes sont **sans droits admin** si l'utilisateur peut écrire dans `diK/reports`. Exécuter avec Python 3.11+ et `jsonschema` déjà installé.

```powershell
$dik = 'C:\mycode\diK\diK'
$env:PYTHONPATH = Join-Path $dik 'src'

# Étape 1 — localiser sans déplacer, sans importer
$loc = py -3 -m dik sources discover --sources-root 'C:\mycode' --dik-root $dik |
    ConvertFrom-Json
if ($LASTEXITCODE -ne 0) { throw 'Localisation echouee' }

# Étape 2 — contrôler la persistance et les empreintes
py -3 -m dik sources verify --registry $loc.registry
if ($LASTEXITCODE -ne 0) { throw 'Registre perime ou invalide' }

# Étape 3 — auditer les 126 Kristals officiels depuis les catalogues référencés
py -3 -m dik coverage resolve14 --sources-root 'C:\mycode' `
    --resource-registry $loc.registry --dik-root $dik --min-kristals 126
if ($LASTEXITCODE -ne 0) { throw 'Resolution interrompue' }
```

Le portefeuille officiel est détecté dans `C:\mycode\Kristal\kristal-public\kristals` ou `C:\mycode\kristal-public\kristals`. On peut le passer avec `--official-root` pour éviter toute ambiguïté.

### Racines personnalisées

`dik sources discover --sources-root 'C:\mycode' --extra-root 'D:\mes-dictionnaires' ...` : étend le périmètre **uniquement sur demande**. Les dossiers et fichiers sont contrôlés dans le budget. Un inventaire tronqué (`truncated=true`) doit être complété avant tout diagnostic exhaustif.

### Dump Wikidata Q/P

Si et seulement si le registre contient un *véritable* dump Q/P admissible, on peut l'observer explicitement :

```powershell
py -3 -m dik coverage resolve14 --sources-root 'C:\mycode' `
  --resource-registry $loc.registry --wikidata-source-id 'local-ID-FROM-REGISTRY' `
  --dik-root $dik --min-kristals 126
```

Le `source_id` est obtenu depuis `resource-registry.json`, **jamais deviné**. Le SHA du fichier vérifie la cohérence locale, pas la provenance indépendante. `qid-lexicon.jsonl` n'est pas un dump global Q/P. Ne jamais passer un id inventé dans cette commande.

### Où sont les logs ?

- `diK\reports\resources\DISCOVERY_*` : registre, CSV et trace de découverte.
- `diK\reports\resources\resource-registry-latest.json` : pointeur sur le dernier état local.
- `diK\reports\resolution_14_langues\RESOLUTION_*` : `rapport.json`, `scan.log`, matrices, catalogue sources, GF candidats et alertes.
- `diK\reports\installations\...` : sauvegardes et historique d'installation du pack PS7.

**Attention :** partager `resource-registry.json` peut révéler des chemins locaux. Préférer un rapport filtré si les emplacements sont sensibles.

### Point critique du lanceur PS7 (révision du pack)

Le lanceur inclus conserve **un tableau** de portefeuilles candidats, même lorsqu'un seul chemin existe. `@(... | Where-Object ...)` évite qu'un accès `[0]` retourne le premier caractère de `C:\mycode...`. Le scan n'utilise que le chemin complet. Cette correction concerne le lanceur, pas les identités KQ/KP.

Le contrôle `sources verify` retourne `VERIFIED` si toutes les empreintes vérifiables correspondent, `INCOMPLETE` si des ressources n'avaient pas été hashées, et échoue sur une source modifiée ou disparue. Les ressources `INCOMPLETE` ne doivent pas être présentées comme certifiées.
