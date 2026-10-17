.. _devguide:

Developer Guide
======================================================================

This guide covers everything a contributor needs to know to set up a
development environment, run the project, and make changes safely.

If you are brand new to the codebase, read :ref:`architecture` first for a
bird's-eye view of how the pieces fit together.


Prerequisites
----------------------------------------------------------------------

* `Python <https://python.org>`_ 3.14 (or rely on Docker, which pins it)
* `Docker <https://docker.com>`_ and `Docker Compose <https://docs.docker.com/compose/>`_
* `uv <https://docs.astral.sh/uv/>`_ (the Python package/tool manager)
* `Git <https://git-scm.com>`_
* Optional: the `just <https://github.com/casey/just>`_ command runner (the
  repo ships a :file:`justfile` with handy aliases)


Setting up the environment
----------------------------------------------------------------------

All commands are run from the **project root**.

::

   # 1. Clone the repository (or cd into it)
   git clone https://github.com/Sicilia04/stocks-home-backend.git
   cd stocks_home-backend

   # 2. Build and start the containers (django + postgres + local mailer)
   docker compose -f docker-compose.local.yml up --build -d

   # 3. Apply database migrations
   docker compose -f docker-compose.local.yml exec django python manage.py migrate

   # 4. Create a superuser (use it for the admin and the API docs)
   docker compose -f docker-compose.local.yml exec django python manage.py createsuperuser

The web application is available at ``http://127.0.0.1:8000`` and the admin
at ``/admin/``.

To stop the stack:

::

   docker compose -f docker-compose.local.yml down

Use ``--volumes`` (or ``just prune``) to also drop databases and mailers.


Running the tests
----------------------------------------------------------------------

The test-suite is `pytest <https://pytest.org>`_ based and runs *inside* the
Django container so the exact same interpreter and dependencies are used.

::

   # Whole test-suite
   docker compose -f docker-compose.local.yml exec django pytest

   # A single app, e.g. the stock app
   docker compose -f docker-compose.local.yml exec django pytest stocks_home/stock

   # A single test function
   docker compose -f docker-compose.local.yml exec django pytest stocks_home/stock/tests/test_views.py::test_...

Tests use an isolated test database (configured in
``config/settings/test.py``); they never touch your dev data.


Code quality & formatting
----------------------------------------------------------------------

The project is linted and formatted with `ruff <https://docs.astral.sh/ruff/>`_
and template-processed by `djlint <https://www.djlint.com/>`_. All of this is
wired through `pre-commit <https://pre-commit.com>`_.

::

   # Install the git hooks once
   uv run pre-commit install

   # Run the full set of hooks on every tracked file
   uv run pre-commit run --all-files

If a hook fails, it will usually suggest a fix (``--fix``). Commit only after
the hooks pass.


Type checking
----------------------------------------------------------------------

`mypy <https://mypy.readthedocs.io>`_ is run over the ``stocks_home`` package
and ``config``:

::

   uv run mypy stocks_home config


Building the documentation
----------------------------------------------------------------------

The Sphinx documentation (this site) lives in the :file:`docs/` directory.

::

   # Build and serve the docs on port 9000
   docker compose -f docker-compose.docs.yml up --build
   # http://127.0.0.1:9000

See :ref:`howto` for how the RST files map to the rendered pages.


Project layout
----------------------------------------------------------------------

::

   stocks_home-backend/
   ├── config/                     # Django settings, urls, WSGI and the ninja API
   │   ├── api.py                 # Central NinjaExtraAPI instance + handlers
   │   ├── urls.py                # Top-level URL conf
   │   ├── wsgi.py                # WSGI entrypoint
   │   └── settings/
   │       ├── base.py            # Shared settings
   │       ├── local.py           # Local/dev overrides
   │       ├── production.py      # Production hardening
   │       └── test.py            # Test overrides (in-memory / test DB)
   │
   ├── stocks_home/               # The Django apps
   │   ├── users/                 # Custom user model, views, forms, admin, API
   │   │   ├── models.py
   │   │   ├── views.py           # Server-rendered (class-based) views
   │   │   ├── forms.py           # Admin + allauth signup forms
   │   │   ├── admin.py
   │   │   ├── adapters.py        # django-allauth adapter overrides
   │   │   └── api/               # REST endpoints (django-ninja)
   │   │       ├── views.py
   │   │       └── schema.py
   │   └── stock/                 # Business domain: categories, products, movements
   │       ├── models.py
   │       ├── admin.py
   │       └── api/
   │           ├── views.py
   │           └── schema.py
   │
   ├── docs/                      # Sphinx documentation (this site)
   ├── tests/                     # Project-wide tests
   ├── compose/                   # Dockerfiles for the local stack
   └── .envs/                     # Per-environment .env files


Conventions
----------------------------------------------------------------------

Commit messages
~~~~~~~~~~~~~~~

We follow `Conventional Commits <https://www.conventionalcommits.org/>`_:

* ``feat:``      new feature
* ``fix:``       bug fix
* ``refactor:``  behaviour-preserving change
* ``docs:``      documentation only
* ``test:``      adding/fixing tests
* ``chore:``     tooling, config, dependencies

Docstrings
~~~~~~~~~~

* Public classes and functions **must** have a docstring (Google style;
  ``napoleon`` renders them into these Sphinx pages).
* Explain *why* and non-obvious *how*, not just *what* the name already says.
* Inline code identifiers use double back-quotes (``like_this``), which render
  as monospace literals.

API design
~~~~~~~~~~

* The API is built with `django-ninja <https://django-ninja.dev/>`_. Each app
  exposes a ``Router`` in ``<app>/api/views.py`` and Pydantic (``ModelSchema``)
  request/response types in ``<app>/api/schema.py``.
* **Read** schemas describe the JSON *output*; **Write** schemas describe the
  accepted *input*. Keep them explicit.
* Business rules that can raise a model ``ValidationError`` belong in the model
  (``save`` / ``clean``); the global handler in :file:`config/api.py` converts
  them into HTTP 400 responses automatically.

Adding a new REST endpoint
~~~~~~~~~~~~~~~~~~~~~~~~~~~

1. Add (or extend) the model in ``stocks_home/<app>/models.py`` and create a
   migration (``python manage.py makemigrations``).
2. Add/adjust the read & write ``ModelSchema`` in ``<app>/api/schema.py``.
3. Add the view function in ``<app>/api/views.py`` with the appropriate
   ``@router.<verb>`` decorator and response type.
4. Write a test in ``<app>/tests/api/test_views.py``.
5. Run the quality gates (tests, pre-commit, mypy) — see above.

Pull request checklist
~~~~~~~~~~~~~~~~~~~~~~

- [ ] Code follows the conventions above and matches the surrounding style.
- [ ] Tests added/updated and passing.
- [ ] ``pre-commit run --all-files`` is green.
- [ ] ``mypy stocks_home config`` is green.
- [ ] Docs updated if the change is user- or API-visible.
- [ ] Commit messages follow Conventional Commits.
