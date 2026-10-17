.. _howto:

How To — Project Documentation
======================================================================

This page explains how the documentation in this site is built and how to add
new pages.

Get started
----------------------------------------------------------------------

Documentation is written as `ReST <https://docutils.sourceforge.io/docs/ref/rst/restructuredtext.html>`_
files in the :file:`docs/` directory and rendered by
`Sphinx <https://www.sphinx-doc.org/>`_.

To build and serve the documentation locally::

   docker compose -f docker-compose.docs.yml up --build
   # Documentation: http://127.0.0.1:9000

Changes to files in ``docs/`` are picked up automatically by the live-reload
server (``sphinx-autobuild``), so you can edit and refresh the browser
without restarting the container.


Where the docs come from
----------------------------------------------------------------------

Two kinds of content feed this site:

1. **Hand-written pages** — the ``*.rst`` files in :file:`docs/` (this file,
   ``index.rst``, ``devguide.rst``, ``architecture.rst``, etc.). The list of
   pages, and their order, is defined by the ``.. toctree::`` directive at the
   top of ``index.rst``.
2. **API reference** — generated from the Python code's docstrings via the
   ``autodoc`` / ``automodule`` / ``autoclass`` directives (see
   ``stock.rst`` and ``users.rst`` for examples).

Docstrings to documentation
----------------------------------------------------------------------

The Sphinx extension ``sphinx.ext.autodoc`` (with the ``napoleon`` extension
for Google-style docstrings) is already enabled in :file:`docs/conf.py`.

Any class or function that has a docstring and is referenced by an
``autoclass`` / ``automodule`` directive is rendered automatically. To point
your new ``.rst`` page at a module, add a line such as::

   .. automodule:: stocks_home.stock.models
      :members:
      :undoc-members:
      :show-inheritance:

Adding a new documentation page
----------------------------------------------------------------------

1. Create a new ``.rst`` file in :file:`docs/` (e.g. ``mytopic.rst``).
2. Give it a top-level title and, optionally, a reference label
   (``.. _mytopic:``).
3. Add the file to the ``toctree`` in ``index.rst`` where it should appear.
4. Rebuild with the command above and check the rendered page.


Sphinx configuration
----------------------------------------------------------------------

All builder settings live in :file:`docs/conf.py` (project name, extensions,
theme, exclusion rules). Most changes you might make:

* Add / remove extensions (e.g. ``sphinx.ext.intersphinx`` for cross-project
  links).
* Change the ``html_theme``.
* Adjust ``exclude_patterns`` to keep build noise out.
