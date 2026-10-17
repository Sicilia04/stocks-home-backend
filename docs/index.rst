.. Stocks Home documentation master file, created by
   sphinx-quickstart.
   You can adapt this file completely to your liking, but it should at least
   contain the root `toctree` directive.

Stocks Home — Developer Documentation
======================================================================

**Stocks Home** is a self-hosted stock manager: it tracks products, their
categories, and stock movements, and exposes a REST API (JWT + session auth)
built on `django-ninja`. This documentation is the reference for developers
contributing to the project.

Contents
--------

.. toctree::
   :maxdepth: 2
   :caption: Contents:

   devguide
   architecture
   stock
   users
   pycharm/configuration
   howto


Quick start
-----------

A three-command tour of the local stack (Docker + uv based). See the
full :ref:`devguide` for details.

::

   # Build and start the services (django + postgres)
   docker compose -f docker-compose.local.yml up --build -d

   # Run migrations, then create a superuser
   docker compose -f docker-compose.local.yml exec django python manage.py migrate
   docker compose -f docker-compose.local.yml exec django python manage.py createsuperuser

The application is served at `http://127.0.0.1:8000`. The interactive OpenAPI
docs are at ``/api/docs/`` (staff only).


Indices and tables
==================

* :ref:`genindex`
* :ref:`modindex`
* :ref:`search`
