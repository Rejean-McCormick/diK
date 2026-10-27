# 23 — Profil local 1.0 et gouvernance des décisions

**Type : choix normatifs candidats diK, non modification du Framework.** Référence ADR-0003.

## Produit local fini

La version 1.0 cible un poste, fonctionne **hors ligne** (après installation), et peut exploiter un miroir Wikidata local. Les requêtes de téléchargement sont explicites ; une simple projection n'utilise jamais le réseau. La CLI reste un support de premier rang ; UI desktop ou web loopback possible, à décider au moment de l'implémentation avec contrôle d'authentification/CSRF si web.

Le moteur est un **monolithe modulaire** : `domain` pur (identity, lexical, alignment, projection, coverage), `application` (revue, import, publication, migration-plan), `adapters` (Framework, Wikidata, fichiers, SQLite, CLI/UI). Ports typés, interfaces versionnées, zéro import de SQLite ou de HTTP dans `domain`. Les caches n'allouent jamais de KQ et n'approuvent jamais une correspondance.

## Permissions de publication

Les fichiers historiques et catalogues publiés sont immuables. Une correction crée un nouveau snapshot avec manifeste et empreinte ; un pointeur atomique active le snapshot seulement après validation. Avant activation, aucune nouvelle donnée n'est visible. En cas de crash, le précédent manifeste vérifié reste actif. En cas de corruption, quarantaine, pas de réécriture silencieuse.

La provenance et les décisions sont distinctes des préférences lexicales. Le réviseur doit être enregistré comme **identité d'acteur existante**, jamais inventé par l'IA. Les décisions acceptées exigent preuves KS et contraintes de correspondance exactes imposées par Framework ; diK ne peut pas auto-conférer l'autorité de `reviewer`.

## Contrôle des changements

Toute ambiguïté entre ce profil et Framework v11 draft.3 = `BLOCKED: CONTRACT_CONFLICT`. Les 5 contrats JSON diK `1.0-candidate` ne deviennent **pas** des schémas ratifiés par le simple fait de compiler. Une release stable exigera leur gel explicite et une suite de compatibilité.
