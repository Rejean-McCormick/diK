# 05 — Sources, import de Wikidata et synchronisation

## Idée simple, exécution rigoureuse

La **copie locale de Wikidata** peut servir de source privilégiée. Il n'est pas nécessaire de télécharger un dump par langue : les exports d'entités comportent leurs différents `labels`, `aliases`, `descriptions` dans les langues présentes. **Cela n'implique pas que 300 langues soient déjà couvertes pour chaque Q/P**. Les lexèmes Wikidata `L…` (mots, formes, sens) constituent un corpus distinct, à ne pas confondre avec les libellés Q/P.

## Provenance minimale par source

Chaque snapshot ingéré doit conserver : `source_id`, origine locale ou URI, version/date du snapshot, digest SHA-256, taille et format, nature des identifiants, licence ou contraintes de réutilisation, métadonnées de l'import, état de contrôle, plus les révisions Wikidata si disponibles. Ces champs sont une **proposition de manifeste diK** ; les fichiers lexicaux eux-mêmes suivent les schémas Framework.

## Pipeline d'import prévu

1. **Choisir** source locale (prioritaire) ou téléchargement explicitement demandé ; prévisualiser l'espace disque requis et les conditions d'utilisation.
2. **Vérifier** le digest du téléchargement lorsque disponible, parser en flux (JSON compressé) sans charger tout le dump dans la RAM ; interdire les chemins d'archive dangereux.
3. **Lire les entités** Q/P et leurs libellés/alias/descriptions ; normaliser les codes de langue dans un registre séparé, préserver les données originales.
4. **Associer** les entrées aux KQ/KP via les **crosswalks `accepted + exactMatch`** ; les autres deviennent candidats d'alignement, jamais termes importés comme vérifiés.
5. **Écrire les couches lexicales** par langue et éventuellement tranche d'identifiants ; utiliser JSONL et hashes, contrôler les duplications.
6. **Construire un catalogue** pointant vers chaque couche avec version, provenance et priorité. Préserver la couche humaine lors des mises à jour du miroir.
7. **Comparer avec le snapshot précédent** : Q/P nouveaux, retirés, redirigés ; libellés ajoutés/modifiés/supprimés ; correspondances à réexaminer.
8. **Installer de façon atomique** le snapshot après validation ; conserver rapports d'erreur et possibilité de retour à la précédente révision.

## Télécharger et reprendre

Fonction prévue, **pas encore un outil diK livré** : requêtes HTTP respectueuses du serveur, métadonnées `ETag`/`Last-Modified` si disponibles, reprise de plages seulement si le serveur la permet, fichier temporaire, contrôles d'intégrité, débit configurable, annulation/reprise sûre et reporting de progression. Le réseau est **désactivé par défaut** pour les corpus privés. Les dumps Wikimedia restent une source externe dont la cadence et le format doivent être vérifiés avant chaque import.

### Synchronisation d'un Q apparu plus tard

`KQ85001` peut exister avant qu'un Q Wikidata ne décrive la même réalité. L'arrivée d'un Q ouvre une **suggestion**. Après examen des sens et preuve, diK ajoute un crosswalk accepté dans une nouvelle version. Les ID internes et les engagements des graphes existants ne changent jamais.

### Redirections, scissions et fusions

Une redirection Wikidata ne doit pas déclencher une fusion silencieuse de KQ. Les décisions deviennent `superseded` lorsque leur validité ou leur cible change et sont remplacées dans une nouvelle vue active. Les divergences restent auditées.

## Sources non-Wikidata

Pour une terminologie externe, inscrire `source_system`, `source_snapshot`, `source_record_id`, `license` et une `alignment` avec décision et `KS` de preuve. Les licences ne sont pas uniformes : diK doit pouvoir refuser l'import ou empêcher sa redistribution, selon les conditions applicables. La donnée Wikidata structurée est diffusée sous **CC0**, mais cela ne vaut pas automatiquement pour toutes les autres sources ou pièces liées.

## Références externes officielles

- Exports d'entités Wikidata : https://www.wikidata.org/wiki/Wikidata:Database_download
- Accès aux données et bonnes pratiques : https://www.wikidata.org/wiki/Wikidata:Data_access
- Licences Wikidata : https://www.wikidata.org/wiki/Wikidata:Licensing
- Lexèmes, formes et sens : https://www.wikidata.org/wiki/Wikidata:Lexicographical_data/Documentation

Ces liens servent d'orientation. Le **schéma des artefacts diK/Kristal** est défini localement par le Framework v11 et non par la page Wikidata.
