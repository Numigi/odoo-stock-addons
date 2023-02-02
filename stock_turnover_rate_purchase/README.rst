Stock Turnover Rate / Purchase
==============================
This module extends the module ``stock_turnover_rate``.

.. contents:: Table of Contents

Overview
--------
It allows to define minimum turnover rates on product categories.

On purchase orders, the minimum, target and effective turnover rates are used to colorize the lines.

Configuration
-------------
In the form view of a product category, I find a new field ``Minimum Turnover Rate``.

.. image:: stock_turnover_rate_purchase/static/description/product_category_form.png

The value defined on the category is displayed on products directly under this category.

.. image:: stock_turnover_rate_purchase/static/description/product_form.png

Usage
-----
In the form view of a purchase order, the turnover rate of the product is displayed on each line.

.. image:: stock_turnover_rate_purchase/static/description/purchase_order_form.png

The PO lines are colored based on the turnover rate:

* Green: the turnover rate exceeds the target turnover rate
* Gray (uncolored): the turnover rate is lower than the target turnover rate but higher than the minimum turnover rate
* Red (uncolored): the turnover rate is lower than the minimum turnover rate

Contributors
------------
* Numigi (tm) and all its contributors (https://bit.ly/numigiens)
