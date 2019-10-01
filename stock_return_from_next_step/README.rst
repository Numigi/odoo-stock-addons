Stock Return From Next Step
===========================
This module allows to generate a stock picking return from the next step.

.. contents:: Table of Contents

Context
-------
In vanilla Odoo, you may choose to process your stock operations in one or multiple steps.

For example, the delivery route offers 3 options:

1. Ship Only
2. Pick + Ship
3. Pick + Pack + Ship

With multiple steps, you may end up with the following issue.

* All products have been processed on the first step.
* At the second step, for some reason, the full quantities may not be processed.

After partially processing the picking, you need to:

* Navigate through menus and find the first step picking.
* Manually create a return from this first step.

This is very error prone and not much convenient for the user.

Summary
-------
In the above case, it would be more convenient for the user to simply generate a stock return
when completing the second step.

When asked whether to create a ``Back Order``, the user would instead select to return the products
to their original location.

This is how the module behaves.

Configuration
-------------

Warehouse
~~~~~~~~~
As member of ``Stock / Manager``, I go to the form of my warehouse.

I select the ``(Pick + Ship)`` route for delivering.

.. image:: static/description/warehouse_form.png

Delivery Step
~~~~~~~~~~~~~
I go to the ``Delivery`` picking type related to the ``(Pick + Ship)`` route.

I notice a new checkbox ``Enable Return Unprocessed Quantities``.

.. image:: static/description/delivery_picking_type_form.png

This box allows to enable the new feature on this type of operation.

Usage
-----

Pick Step
~~~~~~~~~
As member of the group ``Stock / User``, I process a ``Pick`` operation.

.. image:: static/description/pick_operation_ready.png

I select all quantities, then I validate the picking.

.. image:: static/description/pick_operation_done.png

Ship Step
~~~~~~~~~
Later, when the order is ready to ship, I go to the related ``Delivery Order``.

.. image:: static/description/ship_operation_ready.png

I notice that one of the items to ship is the wrong product (there is a labelling error).

I fill the quantities for every other item, then I click on ``Validate``.

.. image:: static/description/ship_operation_validate.png

A wizard is opened, asking whether to ``Create a Back Order`` or ``Create a Return``.

I click on ``Create a Return``.

A wizard appears, asking to validate the quantities to return.

I click on ``Return``.

.. image:: static/description/return_wizard.png

A new stock picking is open.

.. image:: static/description/return_wizard.png

This picking is a return operation of the initial ``Pick`` operation.

Partial Returns
~~~~~~~~~~~~~~~
In the above example, when asked to confirm the quantities to return,
I could select to partially return products.

In such case, a back order is created for the quantities that were not returned.

Contributors
------------
* Numigi (tm) and all its contributors (https://bit.ly/numigiens)

More information
----------------
* Meet us at https://bit.ly/numigi-com
