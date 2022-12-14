Stock Picking Add Transit / Stock Rental
========================================
This module is a binding between
`stock_picking_add_transit <https://github.com/Numigi/odoo-stock-addons/tree/12.0/stock_picking_add_transit>`_
and `stock_rental <https://github.com/Numigi/odoo-stock-addons/tree/12.0/stock_rental>`_.

Without this module, when adding a transit to a rental return,
the transit would be added before the existing picking instead of after.

This is due to the fact that the customer location used for rental is an internal location (not a customer location).

Contributors
------------
* Numigi (tm) and all its contributors (https://bit.ly/numigiens)
