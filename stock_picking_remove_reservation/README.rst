Stock Picking Remove Reservation
================================
Odoo provides a server action called 'Correct inconsistencies for reservation' to fix any
desynchronization between quants and their move lines.

This action is only accessible via the server actions menu in the technical panel.

This module allows the same feature to be integrated directly into the stock picking
form and unreserve move lines for the active picking.

Usage
-----
As a user with access to transfers (stock picking), when I receive the error message:

.. image:: static/description/stock_picking_error_message.png

I need to click on "Desynchronize the reservation."



Contributors
------------
* Numigi (tm) and all its contributors (https://bit.ly/numigiens)
