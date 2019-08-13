Purchase Warehouse Access
=========================
This module adds extra access rules to the ``Purchase`` application.

.. contents:: Table of Contents

Summary
-------
This module extends the features of ``stock_warehouse_access``.

The later one adds access per warehouse to objects related to the ``Inventory`` application.
A user is only allowed to see or edit objects related to his assigned warehouse(s).

This module adds the same behavior for ``Purchase Orders`` (or ``Quotations``).

Configuration
-------------
See the README of module ``stock_warehouse_access`` for details on how to setup warehouses per user.

Usage
-----
As member of the group ``Purchase / User``, I go to the ``Purchase`` app.

I notice that only quotations / orders of my own warehouse are displayed.

.. image:: static/description/purchase_order_list.png

I can see the warehouse related to my order in the ``Other Information`` tab:

.. image:: static/description/purchase_order_form.png

Contributors
------------
* Numigi (tm) and all its contributors (https://bit.ly/numigiens)
