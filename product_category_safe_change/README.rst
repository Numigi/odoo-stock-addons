Product Category Safe Change
============================
This module allows to restrict the modification of a product category if the product linked to it has already some stock move
associated to it.

Usage
-----
* Restricting the modification of a category on product

As a user who can edit a product, I go to a product which had already some stock move.
I edit the product and change the category of the product.
I click on the `Save` button.
I get the following blocking error message:

.. image:: static/description/product_category_changed.png


* Restricting Inventory Properties Setup Changes

As a user in the `Inventory/Manager` group, I go to an product category (on `Inventory>Configuration`).
I have access to modify a category.
I try to modify one of the following fields :
-Stock Input Account
-Stock Output Account
-Stock Valuation Account
-Stock Journal
And then click on the `Save` button.

If I have products with this category that have stock move, I get the following blocking error message:

.. image:: static/description/product_category_account_updated.png

Contributors
------------
* Numigi (tm) and all its contributors (https://bit.ly/numigiens)
