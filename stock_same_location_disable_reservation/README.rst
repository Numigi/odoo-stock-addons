Stock Same Location Disable Reservation
=======================================
This module allows to prevent the system from reserving inventory in an origin location, on picking or on quant, similar to the destination location.

Usage
-----
*Case A*
On a product, I do :

.. image:: static/description/product_location_availability.png

And on a picking, I do :

.. image:: static/description/stock_picking.png

Even if there are only quantities in the WH/Stock location, the system does not reserve these quantities because the location is the same as the destination location.
So the picking will still stay on the same state.

*Case B*

Now, on a product, I do :

.. image:: static/description/product_on_hand.png

And on a picking, I do :

.. image:: static/description/picking_check.png

This still will be blocked by system. No reserved product was made, because the system did not found any avalaible quantity
on different location.

In other case, I will have a reserved quantity on quant and picking:

.. image:: static/description/quant_with_reserved_quantity.png

.. image:: static/description/stock_move_line_reservation.png

.. image:: static/description/stock_move_line_reservation.png

Contributors
------------
* Numigi (tm) and all its contributors (https://bit.ly/numigiens)
