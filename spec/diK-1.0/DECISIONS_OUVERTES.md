# Registre des décisions — révision candidate.2

**ATTENTION :** le profil ci-dessous est **proposé et spécifié**, pas formellement approuvé par un décideur humain. Un agent ne peut pas changer le statut d'une ADR pour contourner les contrôles.

| Sujet | Position candidate pour la 1.0 locale | Décision à ratifier avant release |
|---|---|---|
| UI | CLI toujours disponible ; web loopback *ou* desktop, avec accessibilité RTL | choisir l'implémentation concrète et vérifier tests UI |
| Signature | SHA-256 intégré, signature non exigée en mono-user local | activer signatures si publication multi-acteurs |
| Export massif | conserver profil compact 0.3 inchangé, génération en streaming | tout profil shardé est une nouvelle version |
| Allocation KQ | service/framework producteur indépendant ; diK non mint | préciser le registre externe du déploiement |
| Wikidata | miroir local fourni par opérateur, snapshot figé ; réseau opt-in | politiques de refresh, licence et redistribution |
| Workspaces | 1 utilisateur local, isolation fichiers et loopback | ACL/SSO si remote |
| Performance | budgets hypothétiques à mesurer sur hardware publié | p95 définitif après banc reproductible |
| Historique | append-only et sauvegarde/restauration ; pas de purge automatique | politique légale de rétention externe |

**Ce qui n'est pas une décision ouverte :** KQ/KP canoniques, séparation lexical/crosswalk, non-mint Wikidata, ambiguïté non promue, rollback vers dernier snapshot vérifié, restauration des projections depuis le canon, signatures distinctes de SHA.

Toute décision différente nécessite ADR avec tests et analyse de compatibilité. Les extensions réseau, SaaS, IA générative automatique, LLM d'approbation, et multi-tenant ne font pas partie du profil local de diK 1.0 tant qu'elles ne sont pas spécifiées puis validées.
