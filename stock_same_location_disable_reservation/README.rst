Stock Same Location Disable Reservation
=======================================
This module allows to prevent the system from reserving inventory in an origin location similar to the destination location.

Usage
-----
On a product, I do :

.. image:: static/description/product_location_availability.png

And on a picking, I do :

.. image:: static/description/stock_picking.png

Even if there are only quantities in the WH/Stock location, the system does not reserve these quantities because the location is the same as the destination location.
So the picking will still stay on the same state.

In other case, reservation could be done.

Contributors
------------
* Numigi (tm) and all its contributors (https://bit.ly/numigiens)
