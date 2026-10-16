# Stocks Home

Gestionnaire de stock pour la maison : suivi de vos produits, catégories et
mouvements de stock, avec une API REST JWT. Conçu pour être auto-hébergé.

> **Auto-hébergement** — Stocks Home est conçu pour tourner chez vous. Consultez
> la [SECURITY policy](SECURITY.md) pour signaler une vulnérabilité.

[![License: AGPL-3.0](https://img.shields.io/badge/License-AGPL--3.0-blue.svg)](LICENSE)
[![CI](https://github.com/Sicilia04/stocks-home-backend/actions/workflows/ci.yml/badge.svg)](https://github.com/Sicilia04/stocks-home-backend/actions)
[![Python](https://img.shields.io/badge/Python-3.14-blue.svg)](https://python.org)
[![Built with Cookiecutter Django](https://img.shields.io/badge/built%20with-Cookiecutter%20Django-ff69b4.svg?logo=cookiecutter)](https://github.com/cookiecutter/cookiecutter-django/)

## Fonctionnalités

- CRUD catégories, produits et mouvements de stock
- Authentification JWT (`django-ninja-jwt`) et session
- API REST via `django-ninja` / `django-ninja-extra`
- Base de données PostgreSQL
- Déploiement conteneurisé (Docker Compose)

## Stack

| Composant  | Outil                              |
| ---------- | ---------------------------------- |
| Langage    | Python 3.14                        |
| Framework  | Django 6.0                         |
| API        | django-ninja, django-ninja-jwt     |
| BDD        | PostgreSQL                         |
| Cache      | Redis (optionnel)                  |
| Outils     | uv, pre-commit, ruff, mypy         |

## Prérequis

- Docker + Docker Compose
- [uv](https://docs.astral.sh/uv/getting-started/installation/)
- Git

## Démarrage

```bash
# Construire et démarrer les services (django + postgres + mailtrap-local)
docker compose -f docker-compose.local.yml up --build -d

# Migrations
docker compose -f docker-compose.local.yml exec django python manage.py migrate

# Créer un superutilisateur
docker compose -f docker-compose.local.yml exec django python manage.py createsuperuser
```

L'application est accessible sur `http://127.0.0.1:8000`.
La documentation interactive de l'API (Swagger) nécessite un compte staff :
`/api/docs/`.

## Développement

Voir [CONTRIBUTING.md](CONTRIBUTING.md) pour le guide complet. En résumé :

```bash
# Tests
docker compose -f docker-compose.local.yml exec django pytest

# Lint + format (pre-commit : ruff, djlint, django-upgrade...)
uv run pre-commit run --all-files

# Type checks
uv run mypy stocks_home
```

## Documentation

La documentation Sphinx se trouve dans `docs/`. Pour la construire :

```bash
docker compose -f docker-compose.docs.yml up --build
# Documentation : http://127.0.0.1:9000
```

## Contribuer

Toute contribution est la bienvenue ! Pour démarrer, lisez
[CONTRIBUTING.md](CONTRIBUTING.md). En soumettant une contribution, vous
acceptez le [Code de conduite](CODE_OF_CONDUCT.md).

## Signaler un problème

- **Bogue** : [issues](https://github.com/Sicilia04/stocks-home-backend/issues) avec le modèle « Bug report ».
- **Nouvelle fonctionnalité** : [issues](https://github.com/Sicilia04/stocks-home-backend/issues) avec le modèle « Feature request ».
- **Vulnérabilité** : voir [SECURITY.md](SECURITY.md) — ne pas ouvrir d'issue publique.

## Licence

Distribué sous licence [AGPL-3.0](LICENSE).
