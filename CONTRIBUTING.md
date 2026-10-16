# Contribuer à Stocks Home

Merci de votre intérêt ! Ce guide décrit comment préparer votre environnement
de développement, faire des contributions et soumettre des pull requests.

## Stack technique

- Python **3.14**
- Django **6.0**
- API : `django-ninja` / `django-ninja-jwt`
- Base de données : PostgreSQL
- Outils : [uv](https://docs.astral.sh/uv/), Docker, pre-commit, ruff

## Prérequis

- Docker et Docker Compose
- [uv](https://docs.astral.sh/uv/getting-started/installation/)
- Git

## Démarrer le développement

Toutes les commandes sont exécutées depuis la racine du projet.

```bash
# Construire puis démarrer les conteneurs (django + postgres + mailhog)
uv run docker compose -f docker-compose.local.yml up --build -d

# Créer un superutilisateur
uv run docker compose -f docker-compose.local.yml exec django python manage.py createsuperuser
```

## Tests

```bash
# Lancer la suite de tests
uv run docker compose -f docker-compose.local.yml exec django pytest
```

## Qualité du code

Le projet utilise [pre-commit](https://pre-commit.com/). Installez les hooks
une seule fois puis laissez-les tourner à chaque commit :

```bash
uv run pre-commit install
uv run pre-commit run --all-files
```

Cela exécute entre autres ruff (lint + format), djlint, django-upgrade et les
hooks `pre-commit-hooks`.

## Type checks

```bash
uv run mypy stocks_home
```

## Processus de contribution

1. Forkez le dépôt puis créez une branche depuis `master` :
   `git checkout -b feature/ma-feature`.
2. Faites vos modifications en suivant le style du projet.
3. Assurez-vous que les tests passent et que `pre-commit run --all-files` est
   vert.
4. Poussez votre branche et ouvrez une pull request vers `master`.

### Conventions de commit

Nous suivons le format [Conventional Commits](https://www.conventionalcommits.org/) :

- `feat:` nouvelle fonctionnalité
- `fix:` correctif
- `refactor:` refactoring sans changement de comportement
- `docs:` documentation
- `test:` ajout / modification de tests
- `chore:` tâches diverses (config, dépendances...)

### Soumettre une pull request

- Décrivez clairement le problème résolu et la solution proposée.
- Gardez la PR focalisée sur un changement.
- Ajoutez ou mettez à jour les tests si pertinent.
- Respectez le [Code de conduite](CODE_OF_CONDUCT.md).

## Signaler un problème

- **Bogue** : utilisez le modèle « Bug report » dans le onglet Issues.
- **Nouvelle fonctionnalité** : utilisez le modèle « Feature request ».
- **Vulnérabilité de sécurité** : voir [SECURITY.md](SECURITY.md) — ne pas
  ouvrir d'issue publique.
