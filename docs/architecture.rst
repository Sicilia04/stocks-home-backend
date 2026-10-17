.. _architecture:

Architecture
======================================================================

This page gives a high-level view of how Stocks Home works, how the pieces fit
together, and the key invariants a contributor must preserve.


Applications
----------------------------------------------------------------------

There are two Django apps under :file:`stocks_home/`:

* ``users``  – custom user model and user self-service (profile view/edit,
  signup) plus a small REST API. It is scaffolded by *cookiecutter-django*
  and should mostly be left alone unless you need to change authentication or
  profile fields.
* ``stock``  – the actual product of this project: categories, products, and
  stock movements with an audit trail.

Both apps are wired into the shared ``NinjaExtraAPI`` instance in
:file:`config/api.py`, which is the single source of truth for:

* the authentication stack (JWT + session),
* the OpenAPI / docs configuration (``/api/docs/``, staff-only),
* the global exception handling for model-level validation errors,
* and the mounting of each app's ``Router`` under ``/api/``.


Authentication & the API layer
----------------------------------------------------------------------

* ``django-ninja-jwt`` provides JWT-based login, refresh, and logout,
  registered through the default controller in :file:`config/api.py`.
* ``ninja.security.SessionAuth`` allows the server-rendered part of the app
  (Django views + admin) to authenticate through the classic session cookie.
* Every route in ``users/api`` and ``stock/api`` requires an authenticated
  request; anonymous calls are rejected with ``401``.

The interactive OpenAPI documentation is served at ``/api/docs/`` and is
gated behind ``staff_member_required`` so only staff users can access it.


The stock domain model
----------------------------------------------------------------------

``stocks_home/stock/models.py`` defines three models (all extending
``TimeStampedModel`` so they carry ``created`` / ``modified``):

::

   Category 1 ───< Product 1 ───< StockMovement >─── 1 User

* **``Category``** – a named grouping of products. Its ``slug`` is generated
  with ``slugify`` from the name in ``Category.save`` — never set by callers.
* **``Product``** – identified by a unique barcode (EAN-8/EAN-13). Holds a
  ``quantity`` and a ``min_quantity`` threshold. The
  ``is_low_stock`` property (``quantity < min_quantity``) is a *derived*
  value, not a column.
* **``StockMovement``** – an auditable in/out event attributed to a user.
  This is the **only** way a product's quantity changes.

Key relationships:

* ``Category → Product`` is ``on_delete=PROTECT``: a category that still has
  products cannot be deleted.
* ``Product → StockMovement`` is ``on_delete=CASCADE``: deleting a product
  removes its movement history.
* ``User → StockMovement`` is ``on_delete=PROTECT``: a user with movement
  history cannot be deleted.


Invariants (do not break these)
----------------------------------------------------------------------

1. **A product's ``quantity`` is only ever changed by a ``StockMovement``.**
   The API deliberately omits ``quantity`` from the product write-scheme, and
   ``StockMovement.save`` is the single place where ``quantity`` is updated.

2. **Writing a movement and updating the stock are one atomic operation.**
   ``StockMovement.save`` wraps everything in ``transaction.atomic()`` so a
   failed movement never leaves a half-updated product, and vice versa.

3. **Stock can never go negative, and it is race-safe.**
   For an ``OUT`` movement the decrement is performed with a conditional
   ``UPDATE`` (``filter(quantity__gte=-delta).update(...)``). The guard lives
   inside the SQL statement, so concurrent clients cannot both "win" an
   insufficient-stock update — if no row is updated, a ``ValidationError`` is
   raised and the transaction rolls back.

4. **Validation errors from the model surface as HTTP 400, not 500.**
   Model ``save``/``clean`` raising a model ``ValidationError`` is translated
   by the global handler in :file:`config/api.py` into a consistent
   ``{"detail": [...]}`` 400 response.

5. **The category slug always matches its name.**
   It is recomputed in ``Category.save``; if two distinct names slugify to
   the same value the database raises ``IntegrityError``.

The rest of this codebase (views, schemas, admin) is written to *preserve*
these invariants — keep it that way when extending the app.


A stock movement, step by step
----------------------------------------------------------------------

1. ``POST /api/stock/movements/`` with ``{product, kind, quantity}``.
2. The signed-in user is attached automatically (``request.user``).
3. ``StockMovement.save`` opens an atomic block and validates the product is
   active.
4. For ``out``, it attempts a conditional decrement of the product quantity;
   for ``in`` it increments.
5. Only after the product update succeeds is the movement row inserted.
6. On any ``ValidationError`` the block aborts and the API returns ``400``.


Next
----------------------------------------------------------------------

* :ref:`stock` — the REST endpoints and schemas in detail.
* :ref:`users` — the custom user model and its API.
