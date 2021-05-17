Stock Route Optimized
=====================
This module improves performance and flexibility of stock routes.

.. contents:: Table of Contents

Context
-------
In vanilla Odoo, when a sale order is confirmed, stock rules are evaluated in order
to generate stock moves for each sold items.

The problem comes with the selection of a stock rule for a given product.

For each sold product:
    For each step of the delivery route:
        For each location (going through the parent hierarchy of routes):
            For each search operation (up to 3):
                Multiple SELECT queries are executed to the database (because the domain is complex)

.. image:: static/description/odoo_source_code.png

Suppose a 3 steps delivery route, with an order of 50 products.
The performance cost is non-negligeable, because of the high number of SELECT queries to the database.

Another issue with this mecanism is that it can not be extended without adding clauses
to the domain (therefore slowing down the system even more).

Hypothesis
----------
In a normal Odoo application, there are not thousands of stock routes and rules to evaluate.

With this condition, querying to the database every time to find matching routes
is not a good idea.

Stock rules can be all loaded and filtered directly in python in an efficient way.

Overview
--------
The module overrides the method ``_get_rule``.

Instead of using search domains to select stock rules, the module loads all rules related to the
given company and filter the rules directly in python.

The module can be extended using the method ``_matches_product`` defined on ``stock.rule``.

For an example of usage, see the module ``stock_special_route``.

Known Issues
------------

Performance
~~~~~~~~~~~
The module improves the performance of stock rules in the context of procurements (pull).

However, this improvement does not concern push operations for now.
Future improvement could be done for push operations as well.

Contributors
------------
* Numigi (tm) and all its contributors (https://bit.ly/numigiens)
