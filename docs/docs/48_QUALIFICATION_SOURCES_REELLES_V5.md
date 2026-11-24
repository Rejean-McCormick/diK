# 48 — Qualification réelle des ressources locales (diK alpha.9 / V5)

**Maturité : implémentation expérimentale et conservatrice.** Les ressources restent sur leurs disques. La commande ne publie rien et n'accorde aucune autorité lexicale.

## Contexte observé (registre fourni le 23 novembre 2026)

- `dik.local-resource-registry/1.0` : **5 269** références, **12** racines accessibles, zéro dossier racine signalé absent.
- **486** catalogues v11, **392** crosswalks, **392** registres v11.
- **2 423** fichiers GF RGL candidats, **1 185** autres fichiers de grammaire GF, **333** fichiers GF lexicaux, **17** PGF.
- **40** JSONL thématiques Wikidata et **1** `qid-lexicon.jsonl`.
- Toutes les références ont un SHA-256 local. Toutes portent `allowed_for_resolution=false`. Une empreinte valide ne vaut ni licence vérifiée, ni équivalence sémantique.
- **1 246** références ont une empreinte déjà portée par une autre référence ; ce sont des copies, pas de nouvelles formes lexicales. Certains `.pgf` proviennent de répertoires de tests.

Ce bilan dérive du **registre fourni** ; ce n'est ni un audit des contenus des fichiers GF ni une preuve qu'un dump global Wikidata existe sur l'ordinateur.

## Nouvelle commande implémentée

```powershell
$env:PYTHONPATH = 'C:\mycode\diK\diK\src'
py -3 -m dik sources qualify `
  --registry 'C:\mycode\diK\diK\reports\resources\resource-registry-latest.json' `
  --dik-root 'C:\mycode\diK\diK'
```

Produits dans `diK\reports\resources\QUALIFICATION_<horodatage>` :

- `rapport.json` : ventilation par genre, racine, état, doublons SHA et analyse des champs explicitement présents dans le lexique QID.
- `source-qualification.csv` : chaque chemin, son empreinte, un statut de vérification et la prochaine action.
- `scan.log` : trace succincte.

### États

- `v11_a_auditer` : catalogues et crosswalks structurés mais **non autorisés** par la simple découverte ; la commande `resolve14` poursuit sa validation Framework indépendante.
- `gf_sans_lien_semantique` : grammaires, paradigmes et lexiques GF présents sans preuve de lien KQ/KP.
- `wikidata_thematique_candidat` : JSONL thématiques non interprétés comme dumps Q/P complets.
- `lexique_qid_a_inspecter` : lexique QID trouvé, lecture du schéma à titre de diagnostic.
- `artefact_de_test` : certains `.pgf` sont des fixtures de test, non des grammaires de production.
- `non_verifie` : source disparue, altérée, hors budget ou inaccessible ; aucun raccordement admissible.

Tous les états gardent `rights_status=non_qualifie` et `semantic_link=non_prouve_par_la_decouverte` : il n'existe pas de transition implicite vers `allowed_for_resolution=true`.

## Distinguer les différents niveaux de preuve

1. **Chemin** : fichier local trouvé sans suivre de lien symbolique ou jonction.
2. **Intégrité locale** : taille et SHA de l'inventaire toujours identiques ; aucune preuve cryptographique de l'éditeur amont.
3. **Structure** : format, namespace, couche et schéma contrôlés avec l'adaptateur adéquat.
4. **Lien sémantique** : `(namespace,KQ/KP)` vers Wikidata Q/P seulement via un `exactMatch` accepted, pièces KS, et absence de contradiction entre les révisions auditées.
5. **Lexicalisation** : libellé de la langue sollicitée explicitement présent pour la même identité ; jamais de FR→EN ou autre traduction.
6. **Publication** : licences, droits, décision de revue et gouvernance validés séparément.

`source qualification` couvre surtout les étapes 1–2 ; les preuves 3–6 ne sont pas créées par elle.

## Sécurité et limites

- Lecture seule des sources ; sorties uniquement sous `diK/reports`.
- Vérification SHA-256 avant inspection de la source QID ; refus des liens et jonctions dans les chemins.
- Aucun accès réseau, Git, Render ni génération de mots.
- Les fichiers GF ne sont pas compilés automatiquement. Une forme GF ne prouve jamais un KQ/KP.
- Une source de plus de 64 Mio reste non vérifiée au niveau de cette commande (budget réglable) ; un hash local ne constitue pas une attestation de licence.
- Si un répertoire a été déplacé, la source devra être redécouverte. La relocalisation par contenu reste à implémenter.
