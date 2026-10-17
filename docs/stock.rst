.. _stock:

Stock API
=========

The ``stock`` app exposes the following REST endpoints. All require an
authenticated session (JWT or Django session cookie).

Endpoints
---------

Categories
~~~~~~~~~~

+----------------------------------------+---------------------+
| Method & path                          | Description         |
+========================================+=====================+
| GET    /api/stock/categories/          | List all categories |
+----------------------------------------+---------------------+
| POST   /api/stock/categories/          | Create a category   |
+----------------------------------------+---------------------+
| GET    /api/stock/categories/{id}/     | Fetch one category  |
+----------------------------------------+---------------------+
| PATCH  /api/stock/categories/{id}/     | Update a category   |
+----------------------------------------+---------------------+
| DELETE /api/stock/categories/{id}/     | Delete a category   |
+----------------------------------------+---------------------+

Products
~~~~~~~~

+--------------------------------------+-------------------+
| Method & path                        | Description       |
+======================================+===================+
| GET    /api/stock/products/          | List all products |
+--------------------------------------+-------------------+
| GET    /api/stock/products/{id}/     | Fetch one product |
+--------------------------------------+-------------------+
| POST   /api/stock/products/          | Create a product  |
+--------------------------------------+-------------------+
| PATCH  /api/stock/products/{id}/     | Update a product  |
+--------------------------------------+-------------------+
| DELETE /api/stock/products/{id}/     | Delete a product  |
+--------------------------------------+-------------------+

Stock movements
~~~~~~~~~~~~~~~

+---------------------------------------+-----------------------------+
| Method & path                         | Description                 |
+=======================================+=============================+
| GET    /api/stock/movements/          | List all movements          |
+---------------------------------------+-----------------------------+
| GET    /api/stock/movements/{id}/     | Fetch one movement          |
+---------------------------------------+-----------------------------+
| POST   /api/stock/movements/          | Record a stock in/out event |
+---------------------------------------+-----------------------------+



Error handling
--------------

* **401 Unauthorized** - no valid JWT / session cookie.
* **404 Not Found** - the resource does not exist (or you don't have access).
* **400 Bad Request** - model-level validation failed
  (e.g. insufficient stock, inactive product). The body follows the same
  ``{"detail": ["reason 1", "reason 2"]}`` format that ninja uses for its
  own validation errors.
* **409 Conflict** - a category with products cannot be deleted.
* **500 Internal Server Error** - an unhandled server-side error (e.g.
  a database ``IntegrityError`` that is not a business-rule violation).

Schemas
-------

Request / response shapes are auto-generated into the OpenAPI docs (available
at ``/api/docs/``, staff only). The canonical definitions live in:

.. autoclass:: stocks_home.stock.api.schema.CategorySchema
   :members:

.. autoclass:: stocks_home.stock.api.schema.CategoryWriteSchema
   :members:

.. autoclass:: stocks_home.stock.api.schema.ProductSchema
   :members:

.. autoclass:: stocks_home.stock.api.schema.ProductWriteSchema
   :members:

.. autoclass:: stocks_home.stock.api.schema.StockMovementSchema
   :members:

.. autoclass:: stocks_home.stock.api.schema.StockMovementWriteSchema
   :members:

Models
------

.. automodule:: stocks_home.stock.models
   :members:
   :undoc-members:
   :show-inheritance:


Source
------

* Models: :file:`stocks_home/stock/models.py`
* API views: :file:`stocks_home/stock/api/views.py`
* Schemas: :file:`stocks_home/stock/api/schema.py`
