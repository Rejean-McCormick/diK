# 46 — Validation technique, contrat de sûreté et limites V4

## Contrôles automatiques effectués pour ce dépôt

- Les tests du projet doivent être lancés avec `PYTHONPATH=src python -m pytest -q`, sans réseau ni écriture dans les sources. Voir les résultats joints à la livraison, qui ne valent **pas** preuve sur le Windows de l'utilisateur.
- `tests/test_resource_locator.py` contrôle la découverte de lexiques GF, de `qid-lexicon.jsonl`, la persistance du registre, le refus des répertoires de rapport hors diK, l'interdiction des liens symboliques, l'empreinte modifiée et les registres forgés.
- L'intégration V3 `resolution14` continue de valider les sources v11 avec schémas, empreintes et namespace. Une ressource GF sans mapping KQ/KP ne peut produire une forme résolue.

## Contrats à respecter

1. L'inventaire ne signifie pas activation (`allowed_for_resolution=false`).
2. Le mot ne prouve pas l'identité ; le Q/P n'est pas identique au KQ/P ; un crosswalk candidat est interdit comme mapping accepté.
3. Un `.gf` trouvé devient une **référence**, pas un mot utilisable par diK. Un `.jsonl` thématique reste candidat.
4. Les sources sont lues mais jamais éditées ; les rapports sont écrits uniquement sous `diK/reports`.
5. Les scans officiels choisissent une révision v11 canonique par dossier de découverte ; les copies sont recensées comme sources mais non comptées comme Kristals distincts.
6. Les opérations réseau sont absentes de `sources discover` et `coverage resolve14`. Les autres commandes de diK comportent leurs propres règles opt-in.

## Limites et risques restants

- Un hash local identifie le contenu, **pas** la licence, la provenance ou l'intégrité signée par un tiers.
- Le registre de découverte n'est ni une base SQL de recherche lexicale, ni une table de mapping sémantique GF.
- La classification des formats est volontairement prudente et peut manquer des ressources ; elle n'a pas pour but de parcourir aveuglément le PC.
- Un fichier de plus de 64 Mio (valeur par défaut) n'est pas hashé ; il reste `found_unhashed`. Le scanner v11 continue d'auditer ses catalogues selon son propre budget.
- Une révision non évaluable ou une forme non résolue ne constitue **jamais** une demande de traduction.
- La découverte utilise le filesystem au moment de son exécution ; vérifier le registre et relancer l'audit en cas de déplacement / changement de fichier.

## À développer ensuite, distinct du présent update

Mapping GF↔KQ/KP avec décisions de revue, extraction Q/P fiable d'un dump certifié, intégration L/S/F avec paradigmes et preuves, revalidation de droits, détection de déplacements, UX du Source Manager, support des 69 officiels sans v11 et audit de performance à très grande échelle.

## Errata de la revue V4.1 (pack corrigé)

- Le filtre PS7 des deux chemins de portefeuille doit être enveloppé par `@(...)`, sinon un seul chemin peut devenir une chaîne indexée caractère par caractère. Le test Windows réel reste à effectuer.
- `sources verify` ne doit pas retourner un succès silencieux si une source a changé : l'état `STALE` provoque maintenant un échec de commande ; `INCOMPLETE` est explicitement annoncé lorsque le budget de hash empêche une validation complète.
- Les manifestes `RELEASE-SHA256.json` et `RELEASE_MANIFEST_SHA256.json` désignent **alpha.7**, et `docs/MANIFEST_SHA256.json` est l'attestation historique documentaire **0.2.0**. Ce ne sont pas des manifestes actuels de V4 ; ils restent intacts pour préserver l'historique. Le paquet révisé contient une empreinte complète propre à **V4.1**.
- Le test `pytest` vérifie l'exécution Python mais **ne simule pas PowerShell 7 sur Windows**, ni le raccordement GF final, ni l'évaluation des 69 Kristals dont les sources v11 ne sont pas suffisantes.
