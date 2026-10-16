# Sécurité

## Signaler une vulnérabilité

**N'ouvrez pas d'issue publique** pour signaler une vulnérabilité de sécurité.

Utilisez le canal **Private vulnerability reporting** de GitHub :
[Security → Advisories → New draft](https://github.com/Sicilia04/stocks-home-backend/security/advisories/new).

Ce canal permet une communication réservée entre vous et les mainteneurs, avec
le formulaire :

- version concernée (tag / commit SHA),
- description du problème,
- étapes de reproduction,
- PoC si disponible.

## Politique de réponse

- Accusé de réception sous **72 h**.
- Évaluation initiale et plan de correctif sous **7 jours** (lorsqu'il est
  possible de reproduire le problème).
- Notification de correction dès que le correctif est disponible, et
  publication d'un avis de sécurité (`security advisory`) accompagné d'un
  numéro CVE si nécessaire.

## Périmètre

Ce programme couvre le code du dépôt `stocks-home-backend` et les images
Docker officielles du projet. Les dépendances tierces sont couvertes par leur
propre politique de sécurité respective.
