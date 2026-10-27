# 08 — Interface et parcours utilisateur

## Navigation principale

**Projets** | **Dictionnaires** | **Wikidata / sources** | **Correspondances** | **Complétude** | **Migration** | **Audit & paramètres**.

Un **bandeau permanent** affiche : projet, namespace, snapshot du catalogue et nombre d'éléments en attente. Dans chaque écran, le contenu reflète un snapshot connu : il ne varie pas silencieusement pendant une revue.

### 1. Tableau de bord

Affiche : graphes/Kristals inspectés, KQ/KP uniques par namespace, langues **déclarées vs pourvues d'entrées**, indicateurs direct/fallback/manquant/conflit, anciennes identités textuelles non résolues, sources importées, anomalies de hash, décisions d'alignement en attente. Chaque mesure renvoie à son périmètre et sa version.

### 2. Dictionnaires

Inventaire par langue, domaine, source et priorité. Ouvrir un KQ/KP donne : sens/identité, labels concurrents, alias, définitions disponibles, provenance, licence, état de revue. Action « proposer un terme » → aperçu des conflits → décision → nouvelle couche curatée. **Aucune édition de l'import gelé.**

### 3. Sources et téléchargements

Liste de la copie Wikidata locale et des autres sources, état de téléchargement/import, volume, checksum, droits, versions, erreurs. Actions : `Analyser`, `Importer en simulation`, `Importer nouveau snapshot`, `Comparer versions`, `Annuler/reprendre` (future implémentation). Un import externe non conforme reste en quarantaine.

### 4. Atelier de conciliation

À gauche, un référent `(namespace, KQ/KP)` et ses propriétés; au centre, les candidats Wikidata Q/P et autres référentiels ; à droite, les libellés en plusieurs langues, sources et preuves. Proposer `exactMatch` / `closeMatch` / `broadMatch` / `narrowMatch` / `relatedMatch` ; le reviewer approuve ou rejette indépendamment du choix de terme d'affichage. Afficher toute divergence sans fusion silencieuse.

### 5. Matrice de complétude

Lignes : Kristals ou domaines ; colonnes : langues. Une cellule expose deux barres/pourcentages distincts **KQ et KP**, ainsi que direct vs utilisable avec fallback. Ouvrir une cellule liste les identifiants manquants par fréquence, type, domaine et source. Un Kristal non normalisé reçoit l'état « périmètre sémantique incomplet », **pas un 100 %**.

### 6. Atelier de migration

Comparer source (chemin JSON et contexte) aux identifiants proposés, type, candidats alternatifs, provenance, confiance *indicative* et décision. Actions : `Accepter`, `Rejeter`, `Demander un identifiant`, `Conserver non résolu`, `Exporter plan`. **Pas de bouton « appliquer »** sans contrat d'exécution Authoring Kit et contrôles transactionnels éprouvés.

### 7. Paramètres / audits

Configuration du réseau (désactivé par défaut), langues et fallbacks, langues prioritaires, politique de revue, registre local, chemin vers le miroir Wikidata, espace disque, droits de réutilisation et journal. Rechercher chaque décision par ID, reviewer, référent et snapshot.

## Accessibilité et internationalisation de diK elle-même

Interface en français pour l'initialisation, mais chaîne UI externalisée dès le départ. Navigation clavier, contrastes, prise en charge RTL, Unicode NFC pour comparaison non destructrice, affichage fidèle des scripts multiples, codes BCP 47 visibles, gestion des longues listes avec filtrage, pagination et export. La langue de l'interface est indépendante de la langue du dictionnaire inspecté.

## Erreurs explicites

`identité introuvable`, `correspondance seulement probable`, `langue non déclarée`, `fallback en boucle`, `conflit à priorité égale`, `licence incompatible`, `snapshot périmé`, `empreinte invalide`, `migration non approuvée`, `ancien graphe non normalisé`. Chaque erreur doit donner une action corrective claire sans cacher des données ou forcer une fusion.
