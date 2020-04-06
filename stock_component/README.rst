Stock Component
===============

.. contents:: Table of Contents

Summary
-------
This module adds parentality between serial numbers.

The parent serial number is an equipment.
The children are components, which also can have child components.

When a serial number is moved, all children components are moved with the parent in a transparent way.

Configuration
-------------
In the form view of a serial number, I notice a table ``Components``.

.. image:: static/description/serial_form.png

I click on ``Add``.

A wizard is opened.

.. image:: static/description/serial_add_component_wizard.png

I select a product, then I select the serial number of the component to add.

Then I click on ``OK``.

.. image:: static/description/serial_add_component_wizard_filled.png

The selected number is now a component of the equipment.

.. image:: static/description/serial_after_add_component.png

Constraints
~~~~~~~~~~~
When adding a component to a serial number, the child serial number must be located in the same location as the parent.
The component can also be located in a child location under the parent's location.

If the component is in a package, then the parent serial number must be in the same package and vice versa.

If the component has an owner, then the parent serial number must have the same owner and vice versa.

Also, a serial number can not be added as component under multiple parents.

Usage
-----
I create a delivery order and select the equipment.

.. image:: static/description/delivery_order.png

I validate the delivery order.

.. image:: static/description/delivery_order_done.png

In the global list of stock moves, I notice that the component was moved with the equipment.

.. image:: static/description/stock_move_list.png

This move generated for the component is what we call a ``Shadow Move``.
It is automatically created when the equipment is moved.

If you attempt to move a child component directly (in a picking or an inventory adjustment),
a blocking message will appear.

.. image:: static/description/picking_with_component_error.png

Removing a Component
--------------------
To remove a component from its parent, you must go to the form view of the equipment and click on ``Remove``.

.. image:: static/description/serial_remove_component_button.png

.. image:: static/description/serial_remove_component_wizard.png

Then select the number to remove and click on ``OK``.

.. image:: static/description/serial_remove_component_wizard_filled.png

.. image:: static/description/serial_remove_component_after.png

Contributors
------------
* Numigi (tm) and all its contributors (https://bit.ly/numigiens)
