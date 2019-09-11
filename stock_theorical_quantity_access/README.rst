Stock Theoretical Quantity Access
=================================
This module hides the theoretical quantity on inventory adjustments.

When the theoritical quantity is known, it can be used by employees to steal products.

Usage (as Employee)
-------------------
As member of ``Inventory / User``, I create a new inventory adjustment.

.. image:: static/description/inventory_form.png

I select ``All Products``.

I notice that the ``Include Exhausted Products`` checkbox is automatically checked.
I can not uncheck the box.

..

	This prevents employees from knowing which products are exhausted.

.. image:: static/description/inventory_exhausted_checkbox.png

I start the inventory.

.. image:: static/description/inventory_started.png

I notice that:

* The column ``Theoretical Quantity`` is hidden.
* The column ``Checked Quantity`` contains only zeros.

Usage (as Manager)
------------------
As member of ``Inventory / Manager``, I create a new inventory adjustment.

.. image:: static/description/inventory_form_manager.png

I select ``All Products``.

I notice that the ``Include Exhausted Products`` checkbox is automatically checked.
However, I can manually uncheck the box.

I start the inventory.

.. image:: static/description/inventory_started_manager.png

I notice that:

* The column ``Theoretical Quantity`` is visible.
* The column ``Checked Quantity`` contains only zeros.

Contributors
------------
* Numigi (tm) and all its contributors (https://bit.ly/numigiens)
