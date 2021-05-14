Stock Special Route
===================
This module allows to define multiple paths inside the same stock route.

.. contents:: Table of Contents

Context
-------

Special Routes
--------------
The module adds the concept of a special route.

.. image:: static/description/special_route.png

A special route is a route used to filter per product the rules to apply for another route.

For example, you may define a purchase route with two or three steps.

.. image:: static/description/receipt_route.png

The special route is set on the first two rules.
These rules will be applied only for products linked to the special route.

The third rule will be applied as fallback for other products.

Therefore, some products will be received in three steps and others will be received in two steps.

Rule Order
~~~~~~~~~~
Because stock rules are evaluated in order of sequence, it is important that rules
with a special route appear first in sequence.

Known Issues
------------

Performance
~~~~~~~~~~~
The module stock_route_optimized improves the performance of stock rules in the context of procurements (pull).

However, this improvement does not concern push operations for now.

In order to filter stock rules per special route in the context of push operations,
this module decreases performance.

This issue could be fixed in future improvement of the module stock_route_optimized.

Contributors
------------
* Numigi (tm) and all its contributors (https://bit.ly/numigiens)
